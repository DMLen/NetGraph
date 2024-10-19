import os
import imageio.v2 as imageio
import re

directory = 'auto_output'

def numerical_sort(value):
    parts = re.split(r'(\d+)', value)
    return [int(part) if part.isdigit() else part for part in parts]

filenames = sorted([os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.png')], key=numerical_sort, reverse=True)

print(filenames)

images = []
for filename in filenames:
    images.append(imageio.imread(filename))

imageio.mimsave('output.gif', images, loop=0, fps=2)