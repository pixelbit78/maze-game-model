import pygame
import builder, agent

class MazeMenu:
    def __init__(self, screen_width, screen_height):
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Maze MEnu")
        self.font = pygame.font.Font(None, 20)
        self.buttons = []
        self.button_texts = [
            "Build",
            "Train AI",
            "AI Play"
        ]
        self.button_events = [0,0,0]
        self.button_color = (255, 255, 255)
        self._initialize()
        
    def draw(self):
        self.screen.fill((0,0,0))
        for button in self.buttons:
            # Check if the mouse is hovering over the button
            if button.collidepoint(pygame.mouse.get_pos()):
                # Draw the button
                pygame.draw.rect(self.screen, (200, 200, 200), button)
            else:
                # Draw the button
                pygame.draw.rect(self.screen, self.button_color, button)

            # Draw the button text
            button_text = self.font.render(self.button_texts[self.buttons.index(button)], True, (0, 0, 0))
            brect = button_text.get_rect()
            brect.center = button.center
            self.screen.blit(button_text, brect)
        pygame.display.update()
        
    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            for button in self.buttons:
                # Check if the mouse was released over the button
                if button.collidepoint(event.pos):
                    # If it was, set the button_clicked flag to True
                    self.button_events[self.buttons.index(button)] = 1
        
            if self.button_events[0] == 1:
                return "build"
            elif self.button_events[1] == 1:
                return "train"
            elif self.button_events[2] == 1:
                return "play"

        return "menu"
                

    def _initialize(self):
        for btext in self.button_texts:
            start_pos = 50
            idx = self.button_texts.index(btext)

            if idx == 0:
                self.buttons.append(pygame.Rect(start_pos, 50, 100, 50))
            else:
                x = 125+(self.buttons[idx-1].x)
                self.buttons.append(pygame.Rect(x, 50, 100, 50))
