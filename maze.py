import pygame
import menu
import builder
import agent

class Main:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.state = "menu"
        self.window = menu.MazeMenu(self.screen_width, self.screen_height)
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.state = self.handle_input(event)
                    
            self.window.draw()
                
            pygame.display.update()
        
        pygame.quit()
    
    def handle_input(self, event):
        if self.state == "menu":
            self.window = menu.MazeMenu(self.screen_width, self.screen_height)
        elif self.state == "build":
            self.window = builder.MazeBuilder(self.screen_width, self.screen_height)
        elif self.state == "train":
            self.window = agent.train(self.screen_width, self.screen_height, 10)
        elif self.state == "play":
            self.window = agent.play(self.screen_width, self.screen_height, 10)

        return self.window.handle_input(event)


if __name__ == "__main__":
    Main().run()