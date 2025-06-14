import copy
import datetime
import json
import pickle
import os

from DBHandler import get_template_id_by_name, delete_template
from DBHandler.fill_database import fill_database
from YandexDisk import YaDiskInfo
from YandexDisk.YaDiskHandler import get_last_added_files, __get_templates_from_trash__, \
    update_tree, create_tree
from Tree.ClassTree import Tree, Node

from DBHandler.insert_scripts import (insert_many_slides,
                                                  insert_many_fonts,
                                                  insert_template)
from YandexDisk import YaDiskInfo
from pptxHandler.pptxHandler import (install_template,
                                                 get_slides_information)

import logging

logger = logging.getLogger(__name__)

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

def delete_old_files(tree_node: Node):
    if tree_node.children:
        for child in tree_node.children:
            delete_old_files(child)
    else:
        try:
            path = tree_node.path
            os.remove('./Data/Templates/' + path[path.rfind('/') + 1:]) # брать имя файла из бд по пути папки
        except FileNotFoundError:
            logger.info('Данного файла нет на локальном диске')
    

def delete_old(tree_node: Node, new_tree_node: Node):
    if tree_node.resource_id == new_tree_node.resource_id:
        for node in tree_node.children:
            found = None
            for new_node in new_tree_node.children:
                if node.resource_id == new_node.resource_id:
                    found = node
                    delete_old(node, new_node)
                    break
            if found is None:
                delete_old_files(tree_node)
    else:
        delete_old_files(tree_node)


def add_new_files(new_tree_node: Node):
    if new_tree_node.children:
        for child in new_tree_node.children:
            add_new_files(child)
    else:
        ya_disk_info = YaDiskInfo() # поиск только по поддереву
        # скачивание только из Advanced
        last_updated_time = datetime.datetime.fromisoformat(json.load(open("./CONFIG/config.json"))["last-update-time"])
        get_last_added_files(last_updated_time, ya_disk_info)
        template_info = ya_disk_info.add_template(new_tree_node.name, new_tree_node.path, new_tree_node.resource_id)
        print('tmpl_info: ', template_info)
        print(f"Inserting template: {template_info.name}")
        print(f"path: {template_info.path}")
        template_id = insert_template(template_info)
        print(f"Assigned template_id: {template_id}")

        # Get uniq id, that was given by DB.
        # template_id = insert_template(template_info)
        install_template('./Data/Templates/', template_info)
        # Get info about slides into current template and add insert them into DB.
        slide_info_list = get_slides_information('./Data/Templates/' + template_info.name)
        insert_many_slides(template_id, slide_info_list)

    # insert_many_fonts(yadisk_info.get_fonts())


def add_new(tree_node: Node, new_tree_node: Node):
    if tree_node.resource_id == new_tree_node.resource_id:
        for new_node in new_tree_node.children:
            found = None
            for node in tree_node.children:
                if node.resource_id == new_node.resource_id:
                    found = node
                    add_new(node, new_node)
                    break
            if found is None:
                add_new_files(new_tree_node)
    else:
        add_new_files(new_tree_node)

def compare_trees(tree: Tree, new_tree: Tree):
    tree_node = tree.root
    new_tree_node = new_tree.root
    delete_old(tree_node, new_tree_node)
    add_new(tree_node, new_tree_node)


def update_tree_and_db():
    with open("./Tree/ObjectTree.pkl", "rb") as tree_file:
        tree = pickle.load(tree_file)

    last_updated_time = datetime.datetime.fromisoformat(json.load(open("./CONFIG/config.json"))["last-update-time"])
    time_copy = copy.deepcopy(last_updated_time)

    new_tree = create_tree()

    compare_trees(tree, new_tree)

    # update_tree(tree, last_updated_time, True)
    # update_db(time_copy)

    with open("./Tree/ObjectTree.pkl", "wb") as tree_file:
        pickle.dump(tree, tree_file)

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