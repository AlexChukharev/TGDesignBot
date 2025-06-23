import logging

# Inner class Node. Has 4 fields: name, parent, an array of children and full path.
class Node:
    def __init__(self, resource_id: str, name: str, parent=None):
        self.resource_id = resource_id
        self.name = name
        self.parent = parent
        self.children = []

        if parent is None:
            self.path = self.name
        else:
            self.path = parent.path + '/' + self.name
            print('parent_path:', self.parent.path)

        print('node_name:', self.name)
        print('node_path:', self.path)
        

    # СДЕЛАТЬ КОРЕНЬ /TelegramBot

# with open("./CONFIG/config.json", "r") as jsonFile:
#             data = json.load(jsonFile)
#             if data["test_mode"]:
#                 __search_in_directory__('/TelegramBotFastTest/', last_updated_time, ya_disk_info)
#             else:
#                 __search_in_directory__('/TelegramBot/', last_updated_time, ya_disk_info)

class Tree:
    def __init__(self):
        self.root = Node('', '')

    def make_root(self, resource_id: str, name: str):
        self.root = Node(resource_id, name)
        print('root:', self.root.name, self.root.path)

    # Insert new node to tree. Takes the name of parent node and value - name of child.
    def insert_node(self, parent: str, resource_id: str, name: str):
        node = self.__find_by_path__(parent)#, resource_id, load) # надо сверять везде id???
        print('parent_path:', parent)
        print('name', name)
        if node is None:
            raise Exception("Target node does not exist")
        node.children.append(Node(resource_id, name, parent=node))

    # Delete the node and it's children by name.
    def delete_node(self, path: str):
        node = self.__find_by_path__(path)
        if node is None or node.parent is None:
            return
        for child in node.children:
            self.delete_node(child.path)
        node.children.clear()
        node.parent.children.remove(node)
        node.parent = None

    # # Checking is node is leaf of tree.
    # def is_leaf(self, path: str) -> bool:
    #     node = self.__find_by_path__(path)
    #     return node is not None and len(node.children) == 0

    # Get a list of children nodes
    def get_children(self, path: str) -> list:
        node = self.__find_by_path__(path)
        # return [child.name for child in node.children] if node else []
        return node.children if node is not None else None
    
    # # Return name of parent of target node.
    # def get_parent(self, path: str) -> str:
    #     node = self.__find_by_path__(self.root, path)
    #     if node is None or node.parent is None:
    #         raise Exception("No such node")
    #     return node.parent.path

    def exist(self, path: str) -> bool:
        return self.__find_by_path__(path) is not None

    # # Searching target Node in tree. If node doesn't exist return fake node with name = 'None'
    # def __search__(self, node: Node, target: str, lst: list):
    #     if target == '/':
    #         lst.append(self.root)
    #         return
    #     for children in node.children:
    #         if children.name == target:
    #             lst.append(children)
    #             return
    #         else:
    #             self.__search__(children, target, lst)

    # def __get_parent__(self, node: Node, target: str, lst: list):
    #     for children in node.children:
    #         if children.name == target:
    #             lst.append(node)
    #         else:
    #             self.__get_parent__(children, target, lst)

    # def __find_by_path__(self, target_path: str, resource_id=None, load=False) -> Node | None:
    def __find_by_path__(self, target_path: str) -> Node | None:

        # print('compare:', self.root.path, target_path)

        if target_path == self.root.path:
            print('found root:', self.root.name, self.root.path)
            return self.root

        current = self.root
        parts = target_path.strip('/').split('/')
        print('parts:', parts)
        for part in parts[2:]:
            found = None
            for child in current.children:
                if child.name == part:
                    found = child
                    break
            if not found:
                # if load:
                #     found = Node(resource_id, part, parent=current)
                #     current.children.append(found)
                #     # return None
                #     # TODO сделать дублирование функций Или флаг для загрузки дерева и для обновления
                # else:
                return None
            current = found

        print('found node:', current.name, current.path)
        return current
    

    def log_tree(self, node=None, level=0, console=0):
        if console == 0:
            logger = logging.getLogger(__name__)
            
            if node is None:
                logger.info("Logging tree:")
                node = self.root
            
            logger.info("  " * level + f"Node: {node.name} (Path: {node.path})")
            
            for child in node.children:
                self.log_tree(child, level + 1, console)
        else:
            if node is None:
                print("Logging tree:")
                node = self.root
            
            print("  " * level + f"Node: {node.name} (Path: {node.path})")
            
            for child in node.children:
                self.log_tree(child, level + 1, console)

    # def log_tree(self, node=None, level=0, logger=None):
    #     if logger is None:
    #         logger = logging.getLogger("tree_logger")
            
    #     if node is None:
    #         node = self.root

    #     logger.debug("  " * level + f"Node: {node.name} (Path: {node.path})")

    #     for child in node.children:
    #         self.log_tree(child, level + 1, logger=logger)