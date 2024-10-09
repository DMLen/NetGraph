import tkinter as tk
from tkinter import Frame, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

import dash

def get_unique_neighbors(graph, node):
        #get unique neighbours of a node
        neighbors = list(graph.neighbors(node))

        #remove neighbours that share the same dashID
        target_dashID = graph.nodes[node].get('dashID')

        unique_neighbors = []
        for neighbor in neighbors:
            if graph.nodes[neighbor].get('dashID') != target_dashID:
                unique_neighbors.append(neighbor)
                print(f"Node {neighbor} has a different dashID than {node} ({target_dashID})")
            else:
                print(f"Node {neighbor} has the same dashID as {node} ({target_dashID}). Excluding from unique neighbours.")
        
        return unique_neighbors

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

        self.delete_maxneighbour_button = tk.Button(self.frame, text="Delete [Neighbour of Most Connections] [UNIMPLEMENTED]", command=self.delete_maxneighbour_node, bg='orangered')
        self.delete_maxneighbour_button.pack()

        self.healing_label = tk.Label(self.frame, text="=== Healing Strategies ===")
        self.healing_label.pack()

        self.dash_button = tk.Button(self.frame, text="DASH Healing Step", command=self.DASH_healingstep, bg='green')
        self.dash_button.pack()

        self.canvas = None
        self.G = None #g = graph
        self.pos = {} #dictionary to store node positions
        self.last_deleted_node = None
        self.last_deleted_node_neighbours_list = None #contains unique neighbours (not sharing the same dashID) of the last deleted node

    def generate_graph(self):
        try:
            nodenumber = int(self.node_entry.get())
            if nodenumber <= 0:
                raise ValueError("Number of nodes must be positive.")
            
            #higher power = smaller radius
            power = 0.5
            radius = 1.0 / (nodenumber ** power) #make radius smaller if more nodes

            #use networkx to generate a random graph.
            self.G = nx.random_geometric_graph(n=nodenumber, radius=radius)

            #initialize node deltas (degrees changed) and DASH ID
            for node in self.G.nodes():
                self.G.nodes[node]['delta'] = 0
                self.G.nodes[node]['dashID'] = random.random() #random float between 0 and 1

            #if previous graph exists, clear it
            if self.canvas:
                if not messagebox.askyesno("Confirmation", "Do you want to generate a new graph?"):
                    return
            
                self.canvas.get_tk_widget().destroy()
                plt.close('all') #clear prev figure
                messagebox.showwarning("Warning", "Previous graph cleared!")

            self.pos = nx.spring_layout(self.G, k=0.4, iterations=7) #initial node positions are stored in self.pos
            self.draw_graph()

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def draw_graph(self):
        fig, ax = plt.subplots(figsize=(10, 8))

        #calculate colourmap (based on node degrees)
        degrees = dict(self.G.degree())
        normalized = Normalize(vmin=1, vmax=max(degrees.values()))
        colormap = plt.cm.coolwarm

        #give unconnected nodes a distinct colour
        node_colors = [
            '#515151' if degrees[node] == 0 else colormap(normalized(degrees[node]))
            for node in self.G.nodes()
        ] #if node has connections, colour is determined by normalised colormap. lower bound is 1, upper bound is current maximum degree within the network (within the current iteration)

        labels = {node: f"ID: {node}" for node in self.G.nodes()}
        
        #draw network
        nx.draw(self.G, self.pos, ax=ax, with_labels=True, labels=labels, node_color=node_colors, node_size=500, font_size=8, edge_color='grey')

        #add colorbar
        scalarmap = plt.cm.ScalarMappable(cmap=colormap, norm=normalized)
        scalarmap.set_array([])
        colorbar = fig.colorbar(scalarmap, ax=ax, orientation='horizontal', pad=0.1)
        colorbar.set_label('Node Degree (Connections per Node)')

        self.canvas = FigureCanvasTkAgg(fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def delete_random_node(self):
        if self.G is None or len(self.G) == 0:
            messagebox.showwarning("Warning", "No graph exists!")
            return

        node_deletion_target = random.choice(list(self.G.nodes()))
        self.last_deleted_node = node_deletion_target
        self.last_deleted_node_neighbours_list = get_unique_neighbors(self.G, node_deletion_target)
        self.G.remove_node(node_deletion_target)

        if node_deletion_target in self.pos:
            del self.pos[node_deletion_target] #remove pos from dictionary

        plt.close('all') #clear prev figure
        self.canvas.get_tk_widget().destroy() #clear prev canvas
        self.draw_graph()

    def delete_max_node(self):
        if self.G is None or len(self.G) == 0:
            messagebox.showwarning("Warning", "No graph exists!")
            return
        
        max_node = max(self.G.degree, key=lambda x: x[1])[0] #get node with max edge count
        self.last_deleted_node = max_node
        self.last_deleted_node_neighbours_list = get_unique_neighbors(self.G, max_node)
        self.G.remove_node(max_node)

        if max_node in self.pos:
            del self.pos[max_node] #remove node's position from dictionary

        plt.close('all') #clear prev figure
        self.canvas.get_tk_widget().destroy() #clear prev canvas
        self.draw_graph()


    def delete_maxneighbour_node(self):
        print("dummy function!")

    #network healing (singular step) per Degree Assisted Self-Healing algorithm described by Dr Amitabh Trehan
    #currently unimplemented
    def DASH_healingstep(self):
        self.G = dash.dash(self.G, self.last_deleted_node, self.last_deleted_node_neighbours_list)

        plt.close('all') #clear prev figure
        self.canvas.get_tk_widget().destroy() #clear prev canvas
        self.draw_graph()

#main control loop
if __name__ == "__main__":
    root = tk.Tk()
    app = NetGraph(root)
    root.mainloop()
