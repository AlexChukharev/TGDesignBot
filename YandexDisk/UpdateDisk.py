import copy
import datetime
import json
import pickle

from DBHandler import get_template_id_by_name, delete_template
from DBHandler.fill_database import fill_database
from YandexDisk import YaDiskInfo
from YandexDisk.YaDiskHandler import get_last_added_files, __get_templates_from_trash__, \
    create_tree


# Update actuality of database. Insert new files and removing deleted templates.
def update_db(last_updated_time: datetime.datetime):
    ya_disk_info = YaDiskInfo()
    get_last_added_files(last_updated_time, ya_disk_info)
    fill_database(ya_disk_info)
    ya_disk_info.clear()
    __get_templates_from_trash__('/', ya_disk_info)
    for template_info in ya_disk_info.templates:
        template_id = get_template_id_by_name('disk:/' + template_info.path, template_info.name)
        delete_template(template_id)
