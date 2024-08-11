from DBHandler.insert_scripts import (insert_many_slides,
                                                  insert_many_fonts,
                                                  insert_template)
from YandexDisk import YaDiskInfo
from pptxHandler.pptxHandler import (install_templates,
                                                 get_slides_information)


def fill_database(yadisk_info: YaDiskInfo) -> None:
    # For each template insert into DB and install it in local directory.
    for template_info in yadisk_info.get_templates():
        # Get uniq id, that was given by DB.
        template_id = insert_template(template_info)
        install_templates('./Data/Templates/', [template_info])
        # Get info about slides into current template and add insert them into DB.
        slide_info_list = get_slides_information('./Data/Templates/' + template_info.name)
        insert_many_slides(template_id, slide_info_list)

    insert_many_fonts(yadisk_info.get_fonts())
    # insert_many_images(yadisk_info.get_images())
