import networkx
import netgraph

def return_node_delta(graph, id):
        return graph.nodes[id]['delta']

class btreeNode: #class for nodes in the btree
    def __init__(self, graph, id):
        self.id = id
        self.delta = return_node_delta(graph, id) #delta value of the node
        self.leftchild = None
        self.rightchild = None

class btree:
    def __init__(self, graph):
        self.root = None
        self.graph = graph

    def insert(self, val):
        if self.root is None:
            self.root = btreeNode(self.graph, val) #convert graph's node to an abstract btreeNode
        else:
            self.recursive_insert(self.root, val)

    def recursive_insert(self, current_node, val):
        if return_node_delta(self.graph, val) < current_node.delta:
            if current_node.leftchild is None:
                current_node.leftchild = btreeNode(self.graph, val)
            else:
                self.recursive_insert(current_node.leftchild, val)
        else: #if val greater than or equal to value of current node
            if current_node.rightchild is None:
                current_node.rightchild = btreeNode(self.graph, val)
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

    if len(deletednodeneighbours) == 1:
        print("Only one neighbour, no need to heal.")
        return graph, []


    binarytree = btree(graph)

    #prestep. remove duplicate nodes from deletednodeneighbours
    deletednodeneighbours = list(set(deletednodeneighbours))


    #1. inserted neighbours of deleted node by ascending order of delta value
    sorted_deletednodeneighbours = sorted(deletednodeneighbours, key=lambda id: graph.nodes[id]['delta'])
    print(f"Sorted neighbours by delta values: {sorted_deletednodeneighbours}")

    for node_id in sorted_deletednodeneighbours:
        delta_value = graph.nodes[node_id]['delta']
        print(f"Node ID: {node_id}, Delta Value: {delta_value}")


    for id in sorted_deletednodeneighbours:
        binarytree.insert(id)
        print(f"Inserted node {id} into binary tree.")

    #2. add edges between nodes of graph based on how they are connected in binary tree
    traversed = binarytree.inorder_traversal()
    new_edges = [] #list of new edges created via healing
    edges_added = False #track whether edges were created to avoid unneccessary propagation of DashID if all edges already exist
    altered_nodes = [] #nodes with new edges

    for i in range(len(traversed) - 1):
        if not graph.has_edge(traversed[i], traversed[i+1]):
            graph.add_edge(traversed[i], traversed[i+1])
            new_edges.append((traversed[i], traversed[i+1])) #add new edge to list
            print(f"Added edge between {traversed[i]} and {traversed[i+1]}")
            edges_added = True
            altered_nodes.append(traversed[i])
            altered_nodes.append(traversed[i+1])
        else:
            print(f"Edge between {traversed[i]} and {traversed[i+1]} already exists.")

    #3. propagate minimum DashID of neighbour nodes to all nodes processed in this operation
    #find minimum DashID of deletednodeneighbours
    if edges_added:
        min_dashID = min([graph.nodes[id]['dashID'] for id in deletednodeneighbours])
        print(f"Minimum DashID of deleted node's neighbours: {min_dashID}")

        #propagate minimum DashID to all nodes processed in this operation
        for id in altered_nodes:
            graph.nodes[id]['dashID'] = min_dashID
            graph.nodes[id]['delta'] += 1 #

            print(f"Propagated DashID {min_dashID} to node {id}")
    else:
        print(f"No edges were added, DashID not propagated.")   

    return graph, new_edges