import sys

import pygame   # Import the pygame library                 
# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer")

# Load character image
character_image = pygame.image.load('path/to/character_image.png')
character_rect = character_image.get_rect()
character_rect.topleft = (50, SCREEN_HEIGHT - character_rect.height - 10)

# Platform
platform_rect = pygame.Rect(0, SCREEN_HEIGHT - 10, SCREEN_WIDTH, 10)

# Character movement variables
character_speed = 5
jump_speed = 15
gravity = 1
velocity_y = 0
is_jumping = False

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get keys pressed
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        character_rect.x -= character_speed
    if keys[pygame.K_RIGHT]:
        character_rect.x += character_speed
    if keys[pygame.K_SPACE] and not is_jumping:
        is_jumping = True
        velocity_y = -jump_speed

    # Apply gravity
    if is_jumping:
        velocity_y += gravity
        character_rect.y += velocity_y

        # Check for collision with platform
        if character_rect.colliderect(platform_rect):
            character_rect.y = platform_rect.top - character_rect.height
            is_jumping = False
            velocity_y = 0

    # Fill the screen with white
    screen.fill(WHITE)

    # Draw the platform
    pygame.draw.rect(screen, BLACK, platform_rect)

    # Draw the character
    screen.blit(character_image, character_rect.topleft)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()