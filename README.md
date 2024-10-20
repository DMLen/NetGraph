# NetGraph
A network/graph simulator tool for visualising randomly generated networks, and testing automated remediation (self-healing) strategies. Currently there's just one included, DASH, which stands for Degree Assisted Self-Healing and was originally described by Dr. Amitabh Trehan.

When using the Debug (Autoplay) option, node deletion and healing will be automated and snapshots of the graph will be saved to a new folder called `auto_output`. You can run gifmaker.py to turn this into an animated gif file. Some sample outputs can be viewed on [Imgur](https://imgur.com/a/netgraph-outputs-a9rGoyw).

![alt text](https://i.imgur.com/Gve4DcA.gif)

### Requirements
- Matplotlib (3.9.2)
- NetworkX (3.3)
- imageio (2.36.0) (Only if using gifmaker.py)

To install all requirements, run the command `pip install -r /path/to/requirements.txt`
