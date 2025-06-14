class TemplateInfo:
    def __init__(self, name: str, path: str, resource_id: str):
        self.resource_id = resource_id
        self.name = name
        self.path = path


class FontInfo:
    def __init__(self, path: str, name: str, resource_id: str):
        self.resource_id = resource_id
        self.path = path
        self.name = name


class ImageInfo:
    def __init__(self, position: str, path: str, resource_id: str):
        self.resource_id = resource_id
        self.position = position
        self.path = path


class YaDiskInfo:
    def __init__(self):
        self.templates = []
        self.fonts = []
        self.images = []

    def add_template(self, name: str, path: str, resource_id: str):
        self.templates.append(TemplateInfo(name, path, resource_id))

    def add_font(self, path: str, name: str, resource_id: str):
        self.fonts.append(FontInfo(path, name, resource_id))

    def add_image(self, position: str, path: str, resource_id: str):
        self.images.append(ImageInfo(position, path, resource_id))

    def get_templates(self) -> list:
        return self.templates

    def get_fonts(self) -> list:
        return self.fonts

    def get_images(self) -> list:
        return self.images

    def clear(self):
        self.templates.clear()
        self.fonts.clear()
        self.images.clear()
