import tkinter as tk
from tkinter import Frame, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

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

    def generate_graph(self):
        try:
            n = int(self.node_entry.get())
            if n <= 0:
                raise ValueError("Number of nodes must be positive.")

            #use networkx to generate a random graph. probability of edge creation is 0.3
            self.G = nx.erdos_renyi_graph(n=n, p=0.3)

            #if previous graph exists, clear it
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                plt.close('all')  # Close all existing figures
                messagebox.showwarning("Warning", "Previous graph cleared!")
                
            self.draw_graph()

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def draw_graph(self):
        fig, ax = plt.subplots(figsize=(10, 8))
        pos = nx.spring_layout(self.G)  # positions for all nodes
        nx.draw(self.G, pos, ax=ax, with_labels=True, node_color='lightblue', node_size=600, font_size=8)

        self.canvas = FigureCanvasTkAgg(fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def delete_random_node(self):
        if self.G is None or len(self.G) == 0:
            messagebox.showwarning("Warning", "No graph exists!")
            return

        node_deletion_target = random.choice(list(self.G.nodes()))
        self.G.remove_node(node_deletion_target)

        self.canvas.get_tk_widget().destroy() #clear previous canvas and redraw
        self.draw_graph()

#main control loop
if __name__ == "__main__":
    root = tk.Tk()
    app = NetGraph(root)
    root.mainloop()
