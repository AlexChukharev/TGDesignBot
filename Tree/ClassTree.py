import unicodedata

def normalized(input: str) -> str:
    return unicodedata.normalize("NFC", input)

class Tree:
    class Node:
        def __init__(self, name: str, path: str, parent: "Tree.Node | None" = None):
            self.name = name
            self.path = path
            self.parent = parent
            self.children: list[Tree.Node] = []


    def __init__(self):
        self.root = self.Node(name="root", path="root", parent=None)
        self._index: dict[str, Tree.Node] = {"root": self.root}


    def insert(self, parent_path: str, name: str, path: str) -> None:
        if path in self._index:
            raise Exception(f"Node with path '{path}' already exists")

        parent = self.get_node(parent_path)
        if parent is None:
            raise Exception("Target parent does not exist")

        node = self.Node(
            name=name, 
            path=path, 
            parent=parent
        )
        parent.children.append(node)
        self._index[normalized(path)] = node


    def get_children_names(self, path: str) -> list[str]:
        node = self.get_node(path)
        return [child.name for child in node.children]
    

    def get_parent(self, path: str) -> Node:
        node = self.get_node(path)
        parent = node.parent
        if parent is None:
            raise Exception("No parent (root)")
        return parent


    def get_node(self, path: str) -> Node:
        node = self._index.get(normalized(path))
        if node is None:
            raise Exception("No such node")
        return node