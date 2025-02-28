import tkinter as tk
from tkinter import Frame, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from collections import defaultdict
import math
import time
import os

import dash

def connect_graph(graph):
    if nx.is_connected(graph):
        return graph
    
    components = list(nx.connected_components(graph))
    largest_component = components[0]

    for component in components[1:]:
        node_in_largest = next(iter(largest_component))
        node_in_component = next(iter(component))
        
        graph.add_edge(node_in_largest, node_in_component)
        
        largest_component.update(component)
    
    return graph

class NetGraph:
    def __init__(self, root):
        self.root = root
        self.root.title("NetGraph")

        self.frame = Frame(self.root)
        self.frame.pack()

        #entry for node number
        self.node_label = tk.Label(self.frame, text="Number of Nodes:")
        self.node_label.pack()
        self.node_entry = tk.Entry(self.frame)
        self.node_entry.pack()

        #generator button
        self.generate_button = tk.Button(self.frame, text="Generate Random Graph", command=self.generate_graph)
        self.generate_button.pack()

        #delete buttons
        self.deletion_label = tk.Label(self.frame, text="=== Deletion Strategies ===")
        self.deletion_label.pack()

        self.delete_button = tk.Button(self.frame, text="Delete [Random]", command=self.delete_random_node, bg='orangered')
        self.delete_button.pack()

        self.delete_max_button = tk.Button(self.frame, text="Delete [Most Connections]", command=self.delete_max_node, bg='orangered')
        self.delete_max_button.pack()

        self.delete_maxneighbour_button = tk.Button(self.frame, text="Delete [Neighbour of Most Connections]", command=self.delete_maxneighbour_node, bg='orangered')
        self.delete_maxneighbour_button.pack()

        self.healing_label = tk.Label(self.frame, text="=== Healing Strategies ===")
        self.healing_label.pack()

        self.dash_button = tk.Button(self.frame, text="DASH Healing Step", command=self.DASH_healingstep, bg='green')
        self.dash_button.pack()

        self.debug_button = tk.Button(self.frame, text="DEBUG (Autoplay)", command=self.Automatic, bg='blue')
        self.debug_button.pack()

        #disconnected graph warning
        self.warning_label = tk.Label(self.frame, text="", fg="red")
        self.warning_label.pack()

        self.nodecount_label = tk.Label(self.frame, text="Node Count: N/A")
        self.nodecount_label.pack()

        self.highest_delta_label = tk.Label(self.frame, text="Highest Node Delta: N/A")
        self.highest_delta_label.pack()

        self.highest_degree_label = tk.Label(self.frame, text="Highest Node Degree: N/A")
        self.highest_degree_label.pack()

        self.logNcount = tk.Label(self.frame, text="2 Log(n): N/A")
        self.logNcount.pack()

        self.nodenumber = tk.Label(self.frame, text="Number of Nodes: N/A")

        self.canvas = None
        self.G = None #g = graph
        self.healcount = 0

    def debug(self):
        print(self.partition(self.G, 1))

    def partition(self, node):
        neighbors = list(self.G.neighbors(node))
        #remove neighbours added via healing edge so we're only left with natural neighbors
        filterlist = self.get_healing_neighbors(node)
        if len(filterlist) > 0:
            for i in filterlist:
                neighbors.remove(i)

        print(f"Natural Neighbors of deleted node {node}: {neighbors}")

        # Partitioning the neighbors based on their IDs
        partitions = {}
        for neighbor in neighbors:
            # Assuming each node has a randomly assigned ID
            node_id = self.G.nodes[neighbor]['dashID']
            if node_id not in partitions:
                partitions[node_id] = []
            partitions[node_id].append(neighbor)
            print(f"Neighbor {neighbor} with dashID {node_id} added to partition")

        # Select unique representatives from each partition
        unique_neighbors = []
        for partition_id, partition in partitions.items():
            # Choose the neighbor with the lowest initial ID
            representative = min(partition, key=lambda x: self.G.nodes[x]['initial_dashID'])
            unique_neighbors.append(representative)
            print(f"Partition {partition_id} representatives: {partition}, selected: {representative} (via initial ID {self.G.nodes[representative]['initial_dashID']})")

        print(f"Unique neighbors for deleted node {node}: {unique_neighbors}")
        return unique_neighbors

    def get_healing_neighbors(self, node):
        if self.G is None:
            print("Graph is None, returning empty list.")
            return []

        healing_neighbors = []
        for u, v in self.valid_new_edges:
            if u == node:
                healing_neighbors.append(v)
                print(f"Node {node} is connected to {v} via healing edge.")
            elif v == node:
                healing_neighbors.append(u)
                print(f"Node {node} is connected to {u} via healing edge.")
        
        print(f"Healing neighbors for node {node}: {healing_neighbors}")
        return healing_neighbors

    def handle_deletion(self, node):
        print(f"==Deletion event: Node {node}===")
        self.last_deleted_node = node
        self.last_deleted_node_neighbours_list = self.partition(node)

        #process healing neighbours (add them to list of deleted node's neighbours and decrement their delta value)
        templist = self.get_healing_neighbors(node)
        for i in templist:
            self.last_deleted_node_neighbours_list.append(i)
            self.G.nodes[i]['delta'] -= 1

        self.G.remove_node(node)

        if node in self.pos:
            del self.pos[node] #remove pos from dictionary
        print(f"===Deletion conclusion===")

    def check_connectedness(self):
        if not nx.is_connected(self.G):
            self.warning_label.config(text="Warning: The graph is disconnected!")
        else:
            self.warning_label.config(text="")

    def generate_graph(self): #for initial generation
        try:
            nodenumber = int(self.node_entry.get())
            if nodenumber <= 0:
                raise ValueError("Number of nodes must be positive.")
            
            self.pos = {} #dictionary to store node positions
            self.last_deleted_node = None
            self.last_deleted_node_neighbours_list = None #contains unique neighbours (not sharing the same dashID) of the last deleted node
            self.new_edges = [] #list of new edges created via healing
            self.healcount = 0
            
            #higher power = smaller radius
            power = 0.5
            radius = 1.0 / (nodenumber ** power) #make radius smaller if more nodes

            #use networkx to generate a random graph.
            self.G = nx.random_geometric_graph(n=nodenumber, radius=radius)
            self.G = connect_graph(self.G)
            

            #initialize node deltas (degrees changed) and DASH ID
            for node in self.G.nodes():
                id = random.random() #random float between 0 and 1
                
                self.G.nodes[node]['delta'] = 0
                self.G.nodes[node]['dashID'] = id
                self.G.nodes[node]['initial_dashID'] = id

            #if previous graph exists, clear it
            if self.canvas:
                if not messagebox.askyesno("Confirmation", "Do you want to generate a new graph?"):
                    return
            
                self.canvas.get_tk_widget().destroy()
                plt.close('all') #clear prev figure
                messagebox.showwarning("Warning", "Previous graph cleared!")

            logn = 2 * math.log(self.G.number_of_nodes())
            self.logNcount.config(text=f"2 Log(n): {logn}")

            self.pos = nx.spring_layout(self.G, k=0.4, iterations=7) #initial node positions are stored in self.pos
            self.draw_graph()

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def draw_graph(self):
        fig, ax = plt.subplots(figsize=(10, 8))

        #calculate colourmap (based on node degrees)
        degrees = dict(self.G.degree())
        
        if degrees: #make sure degrees isnt empty
            normalized = Normalize(vmin=1, vmax=max(degrees.values()))
            colormap = plt.cm.coolwarm
        else:
            normalized = Normalize(vmin=1, vmax=1)
            colormap = plt.cm.coolwarm

        #give unconnected nodes a distinct colour
        node_colors = [
            '#515151' if degrees[node] == 0 else colormap(normalized(degrees[node]))
            for node in self.G.nodes()
        ] #if node has connections, colour is determined by normalised colormap. lower bound is 1, upper bound is current maximum degree within the network (within the current iteration)

        labels = {node: f"nID: {node}\nDashID: {self.G.nodes[node].get('dashID'):.3f}\nDelta: {self.G.nodes[node].get('delta')}" for node in self.G.nodes()}
        
        #draw network
        self.check_connectedness()
        nx.draw(self.G, self.pos, ax=ax, with_labels=True, labels=labels, node_color=node_colors, node_size=500, font_size=8, edge_color='grey')
        self.valid_new_edges = [(u, v) for u, v in self.new_edges if u in self.G.nodes() and v in self.G.nodes()]
        nx.draw_networkx_edges(self.G, self.pos, edgelist=self.valid_new_edges, edge_color='red', ax=ax, width=1.5)

        #add colorbar
        scalarmap = plt.cm.ScalarMappable(cmap=colormap, norm=normalized)
        scalarmap.set_array([])
        colorbar = fig.colorbar(scalarmap, ax=ax, orientation='horizontal', pad=0.1)
        colorbar.set_label('Node Degree (Connections per Node)')

        highest_delta = 0
        for node in self.G.nodes():
            if self.G.nodes[node]['delta'] > highest_delta:
                highest_delta = self.G.nodes[node]['delta']
        self.highest_delta_label.config(text=f"Highest Delta: {highest_delta}")

        self.nodenumber.config(text=f"Number of Nodes: {self.G.number_of_nodes()}")

        self.highest_degree_label.config(text=f"Highest Degree: {max(degrees.values())}")

        self.nodecount_label.config(text=f"Node Count: {self.G.number_of_nodes()}")

        self.canvas = FigureCanvasTkAgg(fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def delete_random_node(self):
        if self.G is None or len(self.G) == 0:
            messagebox.showwarning("Warning", "No graph exists!")
            return

        node_deletion_target = random.choice(list(self.G.nodes()))
        self.handle_deletion(node_deletion_target)

        plt.close('all') #clear prev figure
        self.canvas.get_tk_widget().destroy() #clear prev canvas
        self.draw_graph()

    def delete_max_node(self):
        if self.G is None or len(self.G) == 0:
            messagebox.showwarning("Warning", "No graph exists!")
            return
        
        max_node = max(self.G.degree, key=lambda x: x[1])[0] #get node with max edge count
        self.handle_deletion(max_node)

        plt.close('all') #clear prev figure
        self.canvas.get_tk_widget().destroy() #clear prev canvas
        self.draw_graph()


    def delete_maxneighbour_node(self):
        if self.G is None or len(self.G) == 0:
            messagebox.showwarning("Warning", "No graph exists!")
            return
        
        max_node = max(self.G.degree, key=lambda x: x[1])[0] #get node with max edge count
        max_node_neighbours = list(self.G.neighbors(max_node))

        try:
            self.handle_deletion(random.choice(max_node_neighbours))
        except IndexError as e:
            messagebox.showerror("All nodes in graph are isolates!", str(e))

        plt.close('all') #clear prev figure
        self.canvas.get_tk_widget().destroy() #clear prev canvas
        self.draw_graph()


    #network healing (singular step) per Degree Assisted Self-Healing algorithm described by Dr Amitabh Trehan
    #currently unimplemented
    def DASH_healingstep(self):

        print(f"=== DASH operation {self.healcount} initiated ===")
        returned_new_edges = []
        self.G, returned_new_edges = dash.dash(self.G, self.last_deleted_node, self.last_deleted_node_neighbours_list)

        for i, j in returned_new_edges:
            self.new_edges.append((i, j))
            self.G.nodes[i]['delta'] += 1
            self.G.nodes[j]['delta'] += 1

        print(f"New edges created in this healing step: {returned_new_edges}")
        self.valid_new_edges = [(u, v) for u, v in self.new_edges if u in self.G.nodes() and v in self.G.nodes()]
        print(f"New existant edges created since graph creation: {self.valid_new_edges}")

        plt.close('all') #clear prev figure
        self.canvas.get_tk_widget().destroy() #clear prev canvas
        self.draw_graph()
        self.healcount += 1
        print(f"=== DASH operation complete ===")
        return returned_new_edges #this is only ever used by the Automatic function if its running. can be ignored otherwise.

    def Automatic(self): #delete random nodes, heal, log output until no nodes are left. good for bulk testing.
        print(f"=== Automation initiated ===")

        LogN = 2 * math.log(self.G.number_of_nodes())
        #maximal values encountered since automation start
        highestMaxDelta = 0
        highestMaxDegree = 0
        everDisconnected = False

        output_dir = "auto_output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        else: #clear output if the folder already exists
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)

        with open("automatic_log_output.txt", "w", encoding='utf-8') as file: #this will also overwrite the log if it already exists

            startTime = time.time()
            while len(self.G) > 1:

                self.delete_random_node()
                file.write(f"Node {self.last_deleted_node} was deleted. \n")                

                edgelist = self.DASH_healingstep() #function also updates graph. return value is new edges
                file.write(f"DASH healing step was performed. New edges: {edgelist}\n")

                filename = f"{output_dir}/{len(self.G)}.png"
                plt.savefig(filename)

                #values of current iteration
                curMaxDelta = max([self.G.nodes[node]['delta'] for node in self.G.nodes()])
                curMaxDegree = max(dict(self.G.degree()).values())

                #check cur values exceed max, if so update them
                #write cur values to file

                print(f"Stats for graph with {len(self.G)} nodes remaining: Current max delta is {curMaxDelta}, current max degree is {curMaxDegree}.\n")
                file.write(f"Stats for graph with {len(self.G)} nodes remaining: Current max delta is {curMaxDelta}, current max degree is {curMaxDegree}.\n")

                if curMaxDelta > highestMaxDelta:
                    highestMaxDelta = curMaxDelta
                    nodesWhenHighestDelta = len(self.G)
                    file.write(f"New highest delta value found: {curMaxDelta}. Currently {nodesWhenHighestDelta} remaining.\n")

                if curMaxDegree > highestMaxDegree:
                    highestMaxDegree = curMaxDegree
                    nodesWhenHighestDegree = len(self.G)
                    file.write(f"New highest degree value found: {curMaxDegree}. Currently {nodesWhenHighestDegree} remaining.\n")

                if not nx.is_connected(self.G):
                    if not everDisconnected:
                        everDisconnected = True
                        nodesWhenFirstDisconnect = len(self.G)
                        file.write(f"Graph is disconnected for the first time! Currently {nodesWhenFirstDisconnect} nodes remaining.\n")
                    else:
                        file.write(f"Graph is currently disconnected!\n")

            #when there is one node left
            endTime = time.time()
            file.write(f"=== Graph is now depleted of nodes. Summarizing information below ===\n")
            elapsedTime = endTime - startTime
            
            #todo: write max values to log
            file.write(f"Highest delta value encountered: {highestMaxDelta}. Encountered when {nodesWhenHighestDelta} nodes were remaining.\n")
            file.write(f"Highest degree value encountered: {highestMaxDegree}. Encountered when {nodesWhenHighestDegree} nodes were remaining.\n")
            file.write(f"2 Log(n) value: {LogN}.\n")

            if everDisconnected:
                file.write(f"Graph first became disconnected when {nodesWhenFirstDisconnect} nodes were remaining.\n")
            else:
                file.write(f"Graph remained connected.\n")

            file.write(f"=== Automation concluded in {elapsedTime:.2f} seconds. End of log. ===")
            file.close()

            print(f"=== Automation concluded {elapsedTime:.2f} seconds ===")

#main control loop
if __name__ == "__main__":
    root = tk.Tk()
    app = NetGraph(root)
    root.mainloop()
