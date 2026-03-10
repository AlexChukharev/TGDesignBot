import logging
import datetime
import json
import os

from dotenv import load_dotenv
import yadisk
from CONFIG.config import CONFIG
from Tree.ClassTree import Tree
from YandexDisk.YaDiskInfo import YaDiskInfo


load_dotenv()
ya_disk = yadisk.YaDisk(token=str(os.getenv('YANDEX_DISK_TOKEN')))
logger = logging.getLogger(__name__)


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
        if item.is_dir():
            __search_in_directory__(item.path, last_updated_time, ya_disk_info)

        elif last_updated_time < item.created:
            if is_template(item):
                ya_disk_info.add_template(item.name, item.path[: item.path.rfind('/')])

            elif is_font(item):
                ya_disk_info.add_font(item.path[: item.path.rfind('/')], item.name)


# Function take an empty lists ant trying to bring from YDisc all files created from last
# checking. Using ISO 8601 format of time with milliseconds.
def get_last_added_files(last_updated_time: datetime.datetime, ya_disk_info: YaDiskInfo):
    check_token(ya_disk)
    try:
        if CONFIG["test_mode"]:
            __search_in_directory__('/TelegramBotFastTest/', last_updated_time, ya_disk_info)
        else:
            __search_in_directory__('/TelegramBot/', last_updated_time, ya_disk_info)
    except Exception as e:
        ya_disk_info.clear()
        raise Exception("Can't find any files")


# Recursive find deleted templates from last update in trash box of YaDisk.
# Takes the current directory and find files in it.
def __get_templates_from_trash__(directory: str,
                                 ya_disk_info: YaDiskInfo):
    for item in ya_disk.trash_listdir(directory):
        if item.is_dir():
            __get_templates_from_trash__(item.path, ya_disk_info)
        elif is_template(item):
            path = directory.split('/')
            path[1] = path[1][: path[1].rfind('_')]
            path = '/'.join(path[1:])
            ya_disk_info.add_template(item.name, path)


# Adds information about new directories to the tree.
def __add_nodes__(directory: str, tree: Tree):
    # отсортировать по пути
    #for item in sorted(ya_disk.listdir(directory), key=lambda x: x.name):
    for item in ya_disk.listdir(directory):
        if item.is_dir() and (not is_font(item)):
            if (directory == "/TelegramBot/") or (directory == "/TelegramBotFastTest/"):
                tree.insert("root", item.name, item.path)
            else:
                parent_path = item.path.rsplit("/", 1)[0]
                tree.insert(parent_path, item.name, item.path)
            __add_nodes__(item.path, tree)


# Update actuality of the current tree object.
def create_tree(tree: Tree):
    check_token(ya_disk)
    if CONFIG["test_mode"]:
        tree.root.path = "disk:/TelegramBotFastTest"
        __add_nodes__('/TelegramBotFastTest/', tree)
    else:
        tree.root.path = "disk:/TelegramBot"
        __add_nodes__('/TelegramBot/', tree)


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


def get_file_size(path: str) -> int:
    check_token(ya_disk)
    return ya_disk.get_meta(path).size
