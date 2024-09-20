import tkinter as tk
from tkinter import Frame, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

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

        #delete button
        self.delete_button = tk.Button(self.frame, text="Delete Random Node", command=self.delete_random_node)
        self.delete_button.pack()

        self.canvas = None
        self.G = None #g = graph
        self.pos = {} #dictionary to store node positions

    def generate_graph(self):
        try:
            nodenumber = int(self.node_entry.get())
            if nodenumber <= 0:
                raise ValueError("Number of nodes must be positive.")

            #use networkx to generate a random graph.
            self.G = nx.random_geometric_graph(n=nodenumber, radius=0.2)

            #if previous graph exists, clear it
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                plt.close('all') #clear prev figure
                messagebox.showwarning("Warning", "Previous graph cleared!")

            self.pos = nx.spring_layout(self.G) #initial node positions are stored in self.pos
            self.draw_graph()

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def draw_graph(self):
        fig, ax = plt.subplots(figsize=(10, 8))

        #calculate colourmap (based on node degrees)
        degrees = dict(self.G.degree())
        normalized = Normalize(vmin=0, vmax=max(degrees.values()))
        colormap = plt.cm.coolwarm
        node_colors = [colormap(normalized(degrees[node])) for node in self.G.nodes()]

        #draw network
        nx.draw(self.G, self.pos, ax=ax, with_labels=True, node_color=node_colors, node_size=500, font_size=8)

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
        self.G.remove_node(node_deletion_target)

        if node_deletion_target in self.pos:
            del self.pos[node_deletion_target] #remove pos from dictionary

        plt.close('all') #clear prev figure
        self.canvas.get_tk_widget().destroy() #clear prev canvas
        self.draw_graph()

#main control loop
if __name__ == "__main__":
    root = tk.Tk()
    app = NetGraph(root)
    root.mainloop()
