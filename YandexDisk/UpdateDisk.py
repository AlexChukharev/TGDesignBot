import copy
import datetime
import json
import pickle
import os

from DBHandler import get_template_id_by_name
from DBHandler.delete_scripts import delete_template, delete_font, delete_slide
from DBHandler.fill_database import fill_database
from YandexDisk import YaDiskInfo
from YandexDisk.YaDiskHandler import get_last_added_files, __get_templates_from_trash__, \
    create_tree, is_template, get_all_files_in_disk
from DBHandler.select_scripts import get_templates_from_child_directories
from DBHandler.update_scripts import update_path
from Tree.ClassTree import Tree, Node

from DBHandler.insert_scripts import (insert_many_slides,
                                                  insert_many_fonts,
                                                  insert_template)
from YandexDisk import YaDiskInfo
from pptxHandler.pptxHandler import (install_template,
                                                 get_slides_information)
from .YaDiskInfo import YaDiskInfo, TemplateInfo

import logging
import asyncio
import yadisk

logger = logging.getLogger(__name__)

ya_disk = yadisk.YaDisk(token=str(os.getenv('YANDEX_DISK_TOKEN')))

# Update actuality of database. Insert new files and removing deleted templates.
# def update_db(last_updated_time: datetime.datetime):
#     ya_disk_info = YaDiskInfo()
#     __get_templates_from_trash__('/', ya_disk_info)
#     for template_info in ya_disk_info.templates:
#         # template_id = get_template_id_by_name('disk:/' + template_info.path, template_info.name)
#         template_id = get_template_id_by_name(template_info.path, template_info.name)
#         # if template_info.path ПРОВЕРЯТЬ нет ли на диске
#         # удалять по корзине только те, которые были удалены после last_updated_time
#         # изменяется ли время добавления файла при перетаскивании внутри диска?
#         # может сразу сделать через разность деревьев
#         delete_template(template_id)
#         # НЕ УДАЛЯЕТ ИЗ ДЕРЕВА
#     ya_disk_info = YaDiskInfo()
#     get_last_added_files(last_updated_time, ya_disk_info)
#     print('yadisk info:', ya_disk_info)
#     fill_database(ya_disk_info)
#     templ = ya_disk_info.get_templates()
#     print(f"Found {len(templ)} templates to insert.")

async def delete_old_files(tree_node: Node):
    # удалить запись из бд в templates и fonts; и если из advanced, то slides
    if tree_node.children:
        for child in tree_node.children:
            await delete_old_files(child)
    else:
        try:
            files = await get_templates_from_child_directories(tree_node.path)
            file_name = files[0][2]
            file_path = files[0][1]
            try:
                os.remove('./Data/Templates/' + file_name) # брать имя файла из бд по пути папки
            except FileNotFoundError:
                logger.info('Данного файла нет на локальном диске')
            template_id = get_template_id_by_name(file_path, file_name)
            if not template_id:
                logger.info(f'Шаблон {file_name} не найден в БД')
                return
            delete_template(template_id)
            # delete_font(template_id)
            # delete_slide(template_id)
            logger.info(f'Шаблон {template_id} удалён')
        except Exception as e:
            logger.info(f'Ошибка при удалении шаблона: {e}')

    

async def delete_old(tree: Tree, tree_node: Node, new_tree_node: Node):
    # плохо удаляет вершины
    if tree_node.resource_id == new_tree_node.resource_id:
        print('tree_node.children:', [node.name for node in tree_node.children])
        children = tree_node.children.copy()
        for node in children:
            print('checking', node.path)
            found = None
            # new_children = new_tree_node.children.copy
            for new_node in new_tree_node.children:
                if node.resource_id == new_node.resource_id:
                    found = node
                    await delete_old(tree, node, new_node)
                    # break
            if found is None:
                print('deleting', node.path)
                tree.delete_node(node.path)
                await delete_old_files(node)
    else:
        await delete_old_files(tree_node)


def update_db_files_paths(tree_node: Node, new_path: Node):
    if tree_node.children:
        for child in tree_node.children:
            update_db_files_paths(child.path, new_path + child.name)
    else:
        update_path(tree_node.path, new_path)


def update_paths(tree: Tree, tree_node: Node, new_tree_node: Node):
    # учесть, если поменялось имя файла
    if tree_node.path != new_tree_node.path:
        update_db_files_paths(tree_node, new_tree_node.path)
        tree_node.name = new_tree_node.name
        tree_node.path = new_tree_node.path
    for node in tree_node.children:
        for new_node in new_tree_node.children:
            if node.resource_id == new_node.resource_id:
                update_paths(tree, node, new_node)
    

def update_files(tree: Tree, tree_node: Node, last_updated_time: datetime.datetime):
    if tree_node.children:
        for child in tree_node.children:
            update_files(tree, child, last_updated_time)
    elif 'Advanced' in tree_node.path:
        # files = await get_templates_from_child_directories(tree_node.path)
        # file_name = files[0][2]
        # file_path = files[0][1]
        # template_id = get_template_id_by_name(file_path, file_name)
        
        # for template_info in ya_disk_info.get_templates():
        #     if is_template(template_info) and tree_node.path in template_info.path:
        for item in ya_disk.listdir(tree_node.path):
            if is_template(item) and last_updated_time < item.modified:
                # удалить локально, если файл заменился
                install_template('./Data/Templates/', TemplateInfo(item.name, item.path, item.resource_id))
                slide_info_list = get_slides_information('./Data/Templates/' + item.name)
                # TODO delete_slide(template_id)
                # insert_many_slides(template_id, slide_info_list) СДЕЛАТЬ

# проверка имени для ВСЕХ файлов


def add_new_files(new_tree_node: Node, ya_disk_info: YaDiskInfo):
    # переименование в бд
    if new_tree_node.children:
        for child in new_tree_node.children:
            add_new_files(child, ya_disk_info)
    else:
        # ya_disk_info = YaDiskInfo() # поиск только по поддереву
        # скачивание только из Advanced
        # last_updated_time = datetime.datetime.fromisoformat(json.load(open("./CONFIG/config.json"))["last-update-time"])
        print(new_tree_node.path)
        # get_last_added_files(last_updated_time, ya_disk_info)
        # ya_disk_info.add_template(new_tree_node.name, new_tree_node.path, new_tree_node.resource_id)
        for template_info in ya_disk_info.get_templates():
            if is_template(template_info) and new_tree_node.path in template_info.path:
                # добавлять в бд путь без названия файла и отдельно название
                print('tmpl_info: ', template_info)
                print(f"Inserting template: {template_info.name}")
                print(f"path: {template_info.path}")
                template_id = insert_template(template_info)
                print(f"Assigned template_id: {template_id}")

                # Get uniq id, that was given by DB.
                # template_id = insert_template(template_info)
                if 'Advanced' in template_info.path:
                    install_template('./Data/Templates/', template_info)
                    # Get info about slides into current template and add insert them into DB.
                    print('template_info.name!!!', template_info.name)
                    slide_info_list = get_slides_information('./Data/Templates/' + template_info.name)
                    print('slides list size', len(slide_info_list))
                    insert_many_slides(template_id, slide_info_list)


def add_new_nodes(tree: Tree, new_node: Node):
    print('inserting', new_node.path)
    tree.insert_node(new_node.parent.path, new_node.resource_id, new_node.name)
    for new_child in new_node.children:
        add_new_nodes(tree, new_child)

# def update_paths(tree_node: Node):
#     for child in tree_node.children:
#         child.path = child.parent.path + '/' + child.name
#         update_paths(child)


def add_new(tree: Tree, tree_node: Node, new_tree_node: Node, ya_disk_info: YaDiskInfo):
    if tree_node.resource_id == new_tree_node.resource_id:
        # if tree_node.name != new_tree_node.name:
        #     tree_node.name = new_tree_node.name
        #     update_paths(tree_node)
        # if tree_node.path != new_tree_node.path:
        #     update_db_files_paths(tree_node, new_tree_node.path)
        #     tree_node.name = new_tree_node.name
        #     tree_node.path = new_tree_node.path
        for new_node in new_tree_node.children:
            found = None
            for node in tree_node.children:
                if node.resource_id == new_node.resource_id:
                    found = node
                    add_new(tree, node, new_node, ya_disk_info)
                    # break
            if found is None:
                # tree.insert_node(new_node.parent.path, new_node.name, new_node.resource_id)
                add_new_nodes(tree, new_node)
                add_new_files(new_node, ya_disk_info)
    else:
        add_new_files(new_tree_node, ya_disk_info)


async def compare_trees(tree: Tree, new_tree: Tree, last_updated_time: datetime.datetime):
    ya_disk_info = get_all_files_in_disk()
    tree_node = tree.root
    new_tree_node = new_tree.root
    await delete_old(tree, tree_node, new_tree_node)
    update_paths(tree, tree_node, new_tree_node)
    update_files(tree, tree_node, last_updated_time)
    add_new(tree, tree_node, new_tree_node, ya_disk_info)
    insert_many_fonts(ya_disk_info.get_fonts())
    # переместить


async def update_tree_and_db():
    with open("./Tree/ObjectTree.pkl", "rb") as tree_file:
        tree = pickle.load(tree_file)

    last_updated_time = datetime.datetime.fromisoformat(json.load(open("./CONFIG/config.json"))["last-update-time"])
    # time_copy = copy.deepcopy(last_updated_time)

    new_tree = create_tree()

    await compare_trees(tree, new_tree, last_updated_time)

    # update_tree(tree, last_updated_time, True)
    # update_db(time_copy)

    with open("./Tree/ObjectTree.pkl", "wb") as tree_file:
        pickle.dump(tree, tree_file)

    last_updated_time = datetime.datetime.now(tz=datetime.timezone.utc)
    with open("./CONFIG/config.json", "r") as jsonFile:
        data = json.load(jsonFile)

    data["last-update-time"] = last_updated_time.isoformat()

    with open("./CONFIG/config.json", "w") as jsonFile:
        json.dump(data, jsonFile)

    tree.log_tree()

    
# Update actuality of database and tree.
# def update_tree_and_db():
#     with open("./Tree/ObjectTree.pkl", "rb") as tree_file:
#         tree = pickle.load(tree_file)

#     last_updated_time = datetime.datetime.fromisoformat(json.load(open("./CONFIG/config.json"))["last-update-time"])
#     time_copy = copy.deepcopy(last_updated_time)
#     update_tree(tree, last_updated_time, True)
#     update_db(time_copy)

#     with open("./Tree/ObjectTree.pkl", "wb") as tree_file:
#         pickle.dump(tree, tree_file)

#     tree.log_tree()