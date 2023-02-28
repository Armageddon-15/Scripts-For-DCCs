"""
    test only
"""
import hou

def print_node_path(node: hou.Node) -> None:
    """Print node's path."""
    print(f"{node.path()}")


def length_of_two_added_vectors(a: hou.Vector3, b: hou.Vector3) -> hou.Vector3:
    """Return length of a sum of two vectors."""
    sum_vec: hou.Vector3 = a + b
    return sum_vec.length()

