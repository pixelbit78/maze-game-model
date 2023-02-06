import pygame
import pickle
import game
from enum import Enum

class DrawObject(Enum):
    WALL = 1
    TARGET = 2
    PLAYER = 3

class MazeBuilder:
    def __init__(self, w=800, h=600):
        self.w = w
        self.h = h

        # init display
        self.maze_rects = []
        self.draw_object = None
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Maze Builder')

    def open_builder(self):
        # Initialize pygame and create the window
        pygame.init()

        # Load the maze rects from the file
        with open("data/maze_rects.pkl", "rb") as f:
            maze_rects = pickle.load(f)

        # Create a flag to indicate when the maze is being drawn
        drawing = False

        wall_color = (255, 0, 0)
        target_color = (0, 255, 0)
        player_color = (0, 0, 255)
        color = wall_color

        # Set up the main loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # Check if the key pressed is the "t" key
                    if event.key == pygame.K_t and self.draw_object != DrawObject.TARGET:
                        self.draw_object = DrawObject.TARGET
                    elif event.key == pygame.K_w and self.draw_object != DrawObject.WALL:
                        self.draw_object = DrawObject.WALL
                        maze_rects.pop()
                    elif event.key == pygame.K_c:
                        self.draw_object = DrawObject.WALL
                        maze_rects = []
                    elif event.key == pygame.K_u:
                        maze_rects.pop()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.draw_object != None:
                    if self.draw_object == DrawObject.TARGET:
                        color = target_color
                    elif self.draw_object == DrawObject.PLAYER:
                        color = player_color
                    else:
                        color = wall_color

                    start_pos = pygame.mouse.get_pos()
                    drawing = True
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.draw_object != None:
                    if self.draw_object == DrawObject.TARGET:
                        color = target_color
                    elif self.draw_object == DrawObject.PLAYER:
                        color = player_color
                    else:
                        color = wall_color

                    end_pos = pygame.mouse.get_pos()
                    drawing = False
                    x = (start_pos[0]//game.BLOCK_SIZE)*game.BLOCK_SIZE
                    y = (start_pos[1]//game.BLOCK_SIZE)*game.BLOCK_SIZE
                    rect = pygame.Rect(x, y, end_pos[0] - x, end_pos[1] - y)
                    maze_rects.append(rect)

            self.display.fill((0, 0, 0))
            for rect in maze_rects:
                if maze_rects.index(rect) == len(maze_rects)-1:
                    pygame.draw.rect(self.display, player_color, rect, 1)
                elif maze_rects.index(rect) == len(maze_rects)-2:
                    pygame.draw.rect(self.display, target_color, rect, 1)
                else:
                    pygame.draw.rect(self.display, wall_color, rect, 1)

            if drawing:
                end_pos = pygame.mouse.get_pos()
                x = (start_pos[0]//game.BLOCK_SIZE)*game.BLOCK_SIZE
                y = (start_pos[1]//game.BLOCK_SIZE)*game.BLOCK_SIZE
                rect = pygame.Rect(x, y, end_pos[0] - x, end_pos[1] - y)
                pygame.draw.rect(self.display, color, rect, 1)

            pygame.display.update()

        # Save the maze rects to a file
        with open("data/maze_rects.pkl", "wb") as f:
            pickle.dump(maze_rects, f)

        # Quit pygame
        pygame.quit()
