import copy
import datetime
import json
import pickle

from DBHandler import get_template_id_by_name, delete_template
from DBHandler.fill_database import fill_database
from YandexDisk import YaDiskInfo
from YandexDisk.YaDiskHandler import get_last_added_files, __get_templates_from_trash__, \
    update_tree


# Update actuality of database. Insert new files and removing deleted templates.
def update_db(last_updated_time: datetime.datetime):
    ya_disk_info = YaDiskInfo()
    __get_templates_from_trash__('/', ya_disk_info)
    for template_info in ya_disk_info.templates:
        # template_id = get_template_id_by_name('disk:/' + template_info.path, template_info.name)
        template_id = get_template_id_by_name(template_info.path, template_info.name)
        # if template_info.path ПРОВЕРЯТЬ нет ли на диске
        # удалять по корзине только те, которые были удалены после last_updated_time
        # изменяется ли время добавления файла при перетаскивании внутри диска?
        # может сразу сделать через разность деревьев
        delete_template(template_id)
    ya_disk_info = YaDiskInfo()
    get_last_added_files(last_updated_time, ya_disk_info)
    print('yadisk info:', ya_disk_info)
    fill_database(ya_disk_info)
    templ = ya_disk_info.get_templates()
    print(f"Found {len(templ)} templates to insert.")
    
    


# Update actuality of database and tree.
def update_tree_and_db():
    with open("./Tree/ObjectTree.pkl", "rb") as tree_file:
        tree = pickle.load(tree_file)

    last_updated_time = datetime.datetime.fromisoformat(json.load(open("./CONFIG/config.json"))["last-update-time"])
    time_copy = copy.deepcopy(last_updated_time)
    update_tree(tree, last_updated_time, True)
    update_db(time_copy)

    with open("./Tree/ObjectTree.pkl", "wb") as tree_file:
        pickle.dump(tree, tree_file)

    tree.log_tree()
