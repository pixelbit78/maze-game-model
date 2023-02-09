import pygame
import random
from enum import Enum
from collections import namedtuple, deque
import numpy as np
import pickle
import math

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    UP_RIGHT = 5
    UP_LEFT = 6
    DOWN_LEFT = 7
    DOWN_RIGHT = 8

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 40

class MazeGameAI:

    def __init__(self, w=800, h=600, game_time=30):
        self.w = w
        self.h = h
        self.game_time = game_time
        self.record = 0
        pygame.init()
        self.font = pygame.font.SysFont('arial', 25)

        # init display
        self.walls = []
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Maze Game')
        self.clock = pygame.time.Clock()
        self.reset()


    def reset(self):
        # init game state
        self.direction = Direction.RIGHT
        self.move_count = deque(maxlen=4) # popleft()
        self.walls = []
        self.rects = []
        self.target = Point(self.w/2, self.h/2)
        self.score = 0
        self.player = None
        self._load_rects()
        self._place_walls()
        self._place_target()
        self._place_player()
        self.frame_iteration = 0
        self.start_time = pygame.time.get_ticks()

    def _load_rects(self):
        # Load the maze rects from the file
        with open("data/maze_rects.pkl", "rb") as f:
            self.rects = pickle.load(f)

    def _place_walls(self):
        for rect in self.rects:
            idx = self.rects.index(rect)

            if idx < len(self.rects)-2:
                x = (rect.x//BLOCK_SIZE)*BLOCK_SIZE
                y = (rect.y//BLOCK_SIZE)*BLOCK_SIZE
                self.walls.append(Point(x, y))

    def _place_target(self):
        rect = self.rects[len(self.rects)-2]
        x = (rect.x//BLOCK_SIZE)*BLOCK_SIZE
        y = (rect.y//BLOCK_SIZE)*BLOCK_SIZE
        self.target = Point(x, y)
        print(self.target)

    def _place_player(self):
        rect = self.rects[len(self.rects)-1]
        x = (rect.x//BLOCK_SIZE)*BLOCK_SIZE
        y = (rect.y//BLOCK_SIZE)*BLOCK_SIZE
        self.player = Point(x, y)

    def get_elapsed_time(self):
        return (pygame.time.get_ticks() - self.start_time) / 1000

    def get_distance(self, source, target):
        x1, y1 = source
        x2, y2 = target
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def train_step(self, action):
        clock_wise = [Direction.RIGHT.value, Direction.DOWN.value, Direction.LEFT.value, Direction.UP.value]
        counter_clock_wise = [Direction.RIGHT.value, Direction.UP.value, Direction.LEFT.value, Direction.DOWN.value]

        self.frame_iteration += 1

        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move
        self._move(action) # update the player

        # 3. check if game over
        reward = 0
        game_over = False
        if list(self.move_count) == clock_wise or list(self.move_count) == counter_clock_wise:
            print("standing still")
            game_over = True
            reward = -10
            return reward, game_over, self.score

        if self.is_collision() or self.get_elapsed_time() > self.game_time:
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. check visible
        if self.is_visible() and self.get_distance(self.player, self.target) < 100:
            print("target is visible and close")
            reward = 5

        # 5. place new target or just move
        if self.player == self.target:
            self.score += 1
            reward = 10
            self._place_player()
            self.start_time = pygame.time.get_ticks()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. return game over and score
        return reward, game_over, self.score

    def play_step(self, action):
        self.frame_iteration += 1

        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move
        self._move(action) # update the player

        # 3. check if game over
        game_over = False
        if self.is_collision() or self.get_elapsed_time() > self.game_time:
            game_over = True
            return game_over, self.score

        # 5. place new target or just move
        if self.player == self.target:
            self.score += 1
            self._place_player()
            self.start_time = pygame.time.get_ticks()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. return game over and score
        return game_over, self.score


    def is_collision(self, pt=None):
        colided = False

        if pt is None:
            pt = self.player

        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            colided = True

        # hits walls
        for wall in self.walls:
            idx = self.walls.index(wall)
            rect = self.rects[idx]

            if pygame.Rect(wall.x, wall.y, rect.width, rect.height).collidepoint(pt):
                colided = True

        return colided

    def is_visible(self, pt=None):
        if pt is None:
            pt = self.player

        # Create a list to store the points on the line
        points = []

        # Get the x and y distance between the start and end positions
        x_dist = self.target.x - pt.x
        y_dist = self.target.y - pt.y

        # Get the number of steps to take along the line
        steps = round(max(abs(x_dist), abs(y_dist)))

        # Calculate the x and y increment for each step
        x_inc = x_dist / (steps + .001)
        y_inc = y_dist / (steps + .001)

        # Starting at the start position, calculate the x and y coordinates for each step
        for step in range(steps):
            x = pt.x + (x_inc * step)
            y = pt.y + (y_inc * step)
            points.append((int(x), int(y)))

        # Check if any of the points on the line are blocked by a wall
        for point in points:
            for wall in self.walls:
                idx = self.walls.index(wall)
                rect = self.rects[idx]
                if pygame.Rect(wall.x, wall.y, rect.width, rect.height).collidepoint(point):
                    return False

        return True

    def _update_ui(self):
        self.display.fill(BLACK)

        pygame.draw.rect(self.display, BLUE1, pygame.Rect(self.player.x, self.player.y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(self.display, GREEN, pygame.Rect(self.target.x, self.target.y, BLOCK_SIZE, BLOCK_SIZE))
        for wall in self.walls:
            idx = self.walls.index(wall)
            rect = self.rects[idx]
            pygame.draw.rect(self.display, RED, pygame.Rect(wall.x, wall.y, rect.width, rect.height))

        text = self.font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()


    def _move(self, action):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)
        #new_dir = clock_wise[(np.argmax(action)+1) % 4]
        #new_dir = clock_wise[np.argmax(action)]

        #"""_summary_
        if np.array_equal(action, [1, 0, 0]) or np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d
        #"""

        self.direction = new_dir

        x = self.player.x
        y = self.player.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
        elif self.direction == Direction.UP_LEFT:
            x -= BLOCK_SIZE
            y -= BLOCK_SIZE
        elif self.direction == Direction.UP_RIGHT:
            x += BLOCK_SIZE
            y -= BLOCK_SIZE
        elif self.direction == Direction.DOWN_LEFT:
            x -= BLOCK_SIZE
            y += BLOCK_SIZE
        elif self.direction == Direction.DOWN_RIGHT:
            x += BLOCK_SIZE
            y += BLOCK_SIZE

        self.player = Point(x, y)

        self.move_count.append(self.direction.value)