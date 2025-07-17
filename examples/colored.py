import time

from barnone import ColoredProgressBar

# Basic Example
pb = ColoredProgressBar(50)
for _ in range(50):
    time.sleep(0.1)
    pb.update()
