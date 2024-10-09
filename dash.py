import networkx

class btreeNode: #class for nodes in the btree
    def __init__(self, id):
        self.id = id
        self.leftchild = None
        self.rightchild = None

class btree:
    def __init__(self):
        self.root = None

    def insert(self, val):
        if self.root is None:
            self.root = btreeNode(val) #convert graph's node to an abstract btreeNode
        else:
            self.recursive_insert(self.root, val)

    def recursive_insert(self, current_node, val):
        if val < current_node.id:
            if current_node.leftchild is None:
                current_node.leftchild = btreeNode(val)
            else:
                self.recursive_insert(current_node.leftchild, val)
        else: #if val greater than or equal to value of current node
            if current_node.rightchild is None:
                current_node.rightchild = btreeNode(val)
            else:
                self.recursive_insert(current_node.rightchild, val)

    def inorder_traversal(self):
        result = []
        self.recursive_inorder_traversal(self.root, result)
        return result
    
    def recursive_inorder_traversal(self, node, result):
        if node is not None:
            self.recursive_inorder_traversal(node.leftchild, result)
            result.append(node.id)
            self.recursive_inorder_traversal(node.rightchild, result)

def dash(graph, deletednode, deletednodeneighbours):
    #note: deletednodeneighbours is only a list of ints!!! delta values have to be acquired from the graph


    #print(f"lol! got graph with {len(graph.nodes)} nodes") #debug
    #print(f"list of neighbors of node 1: {get_neighbors(graph, 1)}") #debug
    print(f"Most recently deleted node: {deletednode}, Neighbours of deleted node: {deletednodeneighbours}") #debug


    binarytree = btree()

    #1. inserted neighbours of deleted node by ascending order of delta value
    sorted_deletednodeneighbours = sorted(deletednodeneighbours, key=lambda id: graph.nodes[id]['delta'])
    print(f"Sorted neighbours by delta values: {sorted_deletednodeneighbours}")

    for id in sorted_deletednodeneighbours:
        binarytree.insert(id)
        print(f"Inserted node {id} into binary tree.")

    #2. add edges between nodes of graph based on how they are connected in binary tree
    traversed = binarytree.inorder_traversal()

    for i in range(len(traversed) - 1):
        graph.add_edge(traversed[i], traversed[i+1])
        print(f"Added edge between {traversed[i]} and {traversed[i+1]}")

    #3. propagate minimum DashID of neighbour nodes to all nodes processed in this operation
    #find minimum DashID of deletednodeneighbours
    min_dashID = min([graph.nodes[id]['dashID'] for id in deletednodeneighbours])
    print(f"Minimum DashID of deleted node's neighbours: {min_dashID}")

    #propagate minimum DashID to all nodes processed in this operation
    for id in traversed:
        graph.nodes[id]['dashID'] = min_dashID

        print(f"Propagated DashID {min_dashID} to node {id}")   
    
    print(f"=== DASH operation complete ===")
    return graph