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
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Maze Builder")
        self.maze_rects = []
        self.draw_object = None

        # Create a flag to indicate when the maze is being drawn
        self.drawing = False

        self.wall_color = (255, 0, 0)
        self.target_color = (0, 255, 0)
        self.player_color = (0, 0, 255)
        self.color = self.wall_color
        self._initialize()

    def _initialize(self):
        # Load the maze rects from the file
        with open("data/maze_rects.pkl", "rb") as f:
            self.maze_rects = pickle.load(f)

    def _exit(self):
        # Save the maze rects to a file
        with open("data/maze_rects.pkl", "wb") as f:
            pickle.dump(self.maze_rects, f)
            
    def handle_input(self, event):
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or event.type == pygame.QUIT:
            self._exit()
            return "menu"

        if event.type == pygame.KEYDOWN:
            # Check if the key pressed is the "t" key
            if event.key == pygame.K_t and self.draw_object != DrawObject.TARGET:
                self.draw_object = DrawObject.TARGET
            elif event.key == pygame.K_w and self.draw_object != DrawObject.WALL:
                self.draw_object = DrawObject.WALL
                self.maze_rects.pop()
            elif event.key == pygame.K_c:
                self.draw_object = DrawObject.WALL
                self.maze_rects = []
            elif event.key == pygame.K_u:
                self.maze_rects.pop()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.draw_object != None:
            if self.draw_object == DrawObject.TARGET:
                self.color = self.target_color
            elif self.draw_object == DrawObject.PLAYER:
                self.color = self.player_color
            else:
                self.color = self.wall_color

            self.start_pos = pygame.mouse.get_pos()
            self.drawing = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.draw_object != None:
            if self.draw_object == DrawObject.TARGET:
                self.color = self.target_color
            elif self.draw_object == DrawObject.PLAYER:
                self.color = self.player_color
            else:
                self.color = self.wall_color

            self.end_pos = pygame.mouse.get_pos()
            self.drawing = False
            x = (self.start_pos[0]//game.BLOCK_SIZE)*game.BLOCK_SIZE
            y = (self.start_pos[1]//game.BLOCK_SIZE)*game.BLOCK_SIZE
            rect = pygame.Rect(x, y, self.end_pos[0] - x, self.end_pos[1] - y)
            self.maze_rects.append(rect)

    def draw(self):
        self.screen.fill((0, 0, 0))
        for rect in self.maze_rects:
            if self.maze_rects.index(rect) == len(self.maze_rects)-1:
                pygame.draw.rect(self.screen, self.player_color, rect, 1)
            elif self.maze_rects.index(rect) == len(self.maze_rects)-2:
                pygame.draw.rect(self.screen, self.target_color, rect, 1)
            else:
                pygame.draw.rect(self.screen, self.wall_color, rect, 1)

        if self.drawing:
            print("hello2")
            self.end_pos = pygame.mouse.get_pos()
            x = (self.start_pos[0]//game.BLOCK_SIZE)*game.BLOCK_SIZE
            y = (self.start_pos[1]//game.BLOCK_SIZE)*game.BLOCK_SIZE
            rect = pygame.Rect(x, y, self.end_pos[0] - x, self.end_pos[1] - y)
            pygame.draw.rect(self.screen, self.color, rect, 1)

        pygame.display.update()
