import pygame
import builder, agent

# Initialize Pygame and create the window
pygame.init()
screen = pygame.display.set_mode((500, 500))
buttons = []
button_texts = [
    "Build",
    "Train AI",
    "AI Play"
]

button_events = [0,0,0]

# Define the font to be used for the button text
font = pygame.font.Font(None, 20)

for btext in button_texts:
    start_pos = 50
    bwidth = 100
    idx = button_texts.index(btext)

    if idx == 0:
        buttons.append(pygame.Rect(start_pos, 50, 100, 50))
    else:
        x = 125+(buttons[idx-1].x)
        buttons.append(pygame.Rect(x, 50, 100, 50))

# Define the button's color
button_color = (255, 255, 255)

# Set up the main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            for button in buttons:
                # Check if the mouse was released over the button
                if button.collidepoint(event.pos):
                    # If it was, set the button_clicked flag to True
                    button_events[buttons.index(button)] = 1
                    running = False

    # Fill the screen with a background color
    screen.fill((0, 0, 0))

    for button in buttons:
        # Check if the mouse is hovering over the button
        if button.collidepoint(pygame.mouse.get_pos()):
            # Draw the button
            pygame.draw.rect(screen, (200, 200, 200), button)
        else:
            # Draw the button
            pygame.draw.rect(screen, button_color, button)

        # Draw the button text
        button_text = font.render(button_texts[buttons.index(button)], True, (0, 0, 0))
        brect = button_text.get_rect()
        brect.center = button.center
        screen.blit(button_text, brect)

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()

if button_events[0]:    # build
    builder.MazeBuilder().open_builder()
if button_events[1]:    # train ai
    agent.train(10)
if button_events[2]:    # play ai
    agent.play(10)
