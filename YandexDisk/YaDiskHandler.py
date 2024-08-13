import datetime
import json
import os
import pickle

from dotenv import load_dotenv
import yadisk
from DBHandler import get_template_id_by_name
from Tree.ClassTree import Tree
from YandexDisk.YaDiskInfo import YaDiskInfo
from DBHandler import delete_template

from .YaDiskInfo import TemplateInfo

load_dotenv()
ya_disk = yadisk.YaDisk(token=str(os.getenv('YANDEX_DISK_TOKEN')))


# Takes item from YaDisk and checking is it a photo directory.
def is_images(item) -> bool:
    return item.is_dir() and ('фото' in item.name.lower() or "photo" in item.name.lower())


# Takes item from YaDisk and checking is it a graphics directory.
def is_graphics(item) -> bool:
    return item.is_dir() and ('график' in item.name.lower() or "graphic" in item.name.lower())


# Takes item from YaDisk and checking is it a template.
def is_template(item) -> bool:
    return item.name.endswith('.pptx')


# Takes item from YaDisk and checking is it a font.
def is_font(item) -> bool:
    return item.name.endswith('.zip') and ('шрифт' in item.name.lower() or "font" in item.name.lower())


# Checking is token valid.
def check_token(token):
    if not token.check_token():
        raise Exception("Invalid token")


# Recursive find in YaDisk. Takes the current directory and find files in it.
def __search_in_directory__(directory: str,
                            last_updated_time: datetime.datetime,
                            ya_disk_info: YaDiskInfo):
    for item in ya_disk.listdir(directory):
        if item.is_dir() and (not is_images(item)) and (not is_graphics(item)):
            __search_in_directory__(item.path, last_updated_time, ya_disk_info)

        elif last_updated_time < item.created:
            if is_images(item) or is_graphics(item):
                ya_disk_info.add_image(item.path, item.path[: item.path.rfind('/')])

            elif is_template(item):
                ya_disk_info.add_template(item.name, item.path[: item.path.rfind('/')])

            elif is_font(item):
                ya_disk_info.add_font(item.path[: item.path.rfind('/')], item.name)


# Function take an empty lists ant trying to bring from YDisc all files created from last
# checking. Using ISO 8601 format of time with milliseconds.
def get_last_added_files(last_updated_time: datetime.datetime, ya_disk_info: YaDiskInfo):
    check_token(ya_disk)
    try:
        __search_in_directory__('/DesignBot/', last_updated_time, ya_disk_info)
    except Exception as e:
        ya_disk_info.clear()
        raise Exception("Can't find any files")


# Recursive find deleted templates from last update in trash box of YaDisk.
# Takes the current directory and find files in it.
def __get_templates_from_trash__(directory: str,
                                 ya_disk_info: YaDiskInfo):
    for item in ya_disk.trash_listdir(directory):
        if item.is_dir() and (not is_images(item)) and (not is_graphics(item)):
            __get_templates_from_trash__(item.path, ya_disk_info)
        elif is_template(item):
            path = directory.split('/')
            path[1] = path[1][: path[1].rfind('_')]
            path = '/'.join(path[1:])
            ya_disk_info.add_template(item.name, path)


# Removes outdated information from the folder tree.
def __delete_nodes__(directory: str, tree: Tree):
    for item in ya_disk.trash_listdir(directory):
        if item.is_dir():
            __delete_nodes__(item.path, tree)
            tree.delete_node(item.name)


# Adds information about new directories to the tree.
def __add_nodes__(directory: str, last_updated_time, tree: Tree):
    for item in ya_disk.listdir(directory):
        if item.is_dir() and (not is_images(item)) and (not is_font(item)):
            if last_updated_time < item.created:
                if directory == "/DesignBot/":
                    tree.insert("root", item.name)
                else:
                    tree.insert(directory[directory.rfind('/') + 1:], item.name)
            __add_nodes__(item.path, last_updated_time, tree)


# Update actuality of the current tree object.
def update_tree(tree: Tree, last_updated_time):
    check_token(ya_disk)
    __delete_nodes__('/', tree)
    __add_nodes__('/DesignBot/', last_updated_time, tree)
    with open("./Tree/ObjectTree.pkl", "wb") as fp:
        pickle.dump(tree, fp)

    # Updating last_updated_time in json.
    last_updated_time = datetime.datetime.now(tz=datetime.timezone.utc)
    with open("./config.json", "r") as jsonFile:
        data = json.load(jsonFile)

    data["last-update-time"] = last_updated_time.isoformat()

    with open("./config.json", "w") as jsonFile:
        json.dump(data, jsonFile)


# This function returns all files from YDisk.
# Returns an object of class YaDiskInfo.
def get_all_files_in_disk() -> YaDiskInfo:
    last_updated_time = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
    ya_disk_info = YaDiskInfo()
    get_last_added_files(last_updated_time, ya_disk_info)
    return ya_disk_info


# Upload a local file to YaDisk by dest_path.
def upload_to_disk(dest_path: list, local_path: str):
    check_token(ya_disk)
    path_to_files = list(ya_disk.listdir('/'))[0].path
    dest_path_str = path_to_files[:path_to_files.rfind('/') + 1] + local_path.split('/')[-1]
    if len(dest_path) != 0:
        dest_path_str = path_to_files[:path_to_files.rfind('/') + 1] + '/'.join(dest_path) + '/' + \
                        local_path.split('/')[-1]
    ya_disk.upload(local_path, dest_path_str)


def get_download_link(path: str) -> str:
    check_token(ya_disk)
    return ya_disk.get_download_link(path)


# Delete file (not directory) from YaDisk.
def delete_from_disk(path: str):
    check_token(ya_disk)
    try:
        if path.endswith('.pptx'):
            try:
                os.remove('./Data/Templates/' + path[path.rfind('/') + 1:])
            except FileNotFoundError:
                print('Данного файла нет на локальном диске')
            template_info = TemplateInfo(path[path.rfind('/') + 1:], path[:path.rfind('/')])
            template_id = get_template_id_by_name(template_info.path, template_info.name)
            delete_template(template_id)
        ya_disk.remove(path)
    except Exception as e:
        raise "No such file or directory"
