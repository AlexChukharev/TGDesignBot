import pickle

from Tree import ClassTree

try:
    tree_obj = pickle.load(open("./Tree/ObjectTree.pkl", "rb"))
except:
    tree = ClassTree.Tree()
dist_indx = 9
indx_list_start = 0
indx_list_end = indx_list_start + dist_indx
child_list = list()


async def set_default():
    global indx_list_start, indx_list_end
    indx_list_start = 0
    indx_list_end = indx_list_start + dist_indx
