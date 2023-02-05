import numpy as np
import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)

def check_visibility(start_pos, end_pos, walls):
    # Create a list to store the points on the line
    points = []

    # Get the x and y distance between the start and end positions
    x_dist = end_pos[0] - start_pos[0]
    y_dist = end_pos[1] - start_pos[1]

    # Get the number of steps to take along the line
    steps = max(abs(x_dist), abs(y_dist))

    # Calculate the x and y increment for each step
    x_inc = x_dist / (steps + .001)
    y_inc = y_dist / (steps + .001)

    # Starting at the start position, calculate the x and y coordinates for each step
    for step in range(steps):
        x = start_pos[0] + (x_inc * step)
        y = start_pos[1] + (y_inc * step)
        points.append((int(x), int(y)))

    # Check if any of the points on the line are blocked by a wall
    for point in points:
        for wall in walls:
            if wall.collidepoint(point):
                return False
    return True
