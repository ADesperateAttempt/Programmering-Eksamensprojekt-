import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_SPEED = 5
JUMP_HEIGHT = 10
GRAVITY = 1

# Colors
BACKGROUND_COLORS = [(135, 206, 235), (34, 139, 34)]

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer Game")

# Player setup
player_image = pygame.image.load('mario smol.png')  # Replace with your player image
player_rect = player_image.get_rect()
player_rect.topleft = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT)

# Variables
x_velocity = 0
y_velocity = 0
on_ground = False
scroll_x = 0

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key presses
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        x_velocity = -PLAYER_SPEED
    elif keys[pygame.K_RIGHT]:
        x_velocity = PLAYER_SPEED
    else:
        x_velocity = 0

    if keys[pygame.K_SPACE] and on_ground:
        y_velocity = -JUMP_HEIGHT
        on_ground = False

    # Apply gravity
    y_velocity += GRAVITY

    # Update player position
    player_rect.x += x_velocity
    player_rect.y += y_velocity

    # Check for ground collision
    if player_rect.bottom >= SCREEN_HEIGHT:
        player_rect.bottom = SCREEN_HEIGHT
        y_velocity = 0
        on_ground = True

    # Screen scrolling
    if player_rect.right > SCREEN_WIDTH:
        scroll_x += player_rect.right - SCREEN_WIDTH
        player_rect.right = SCREEN_WIDTH
    elif player_rect.left < 0:
        scroll_x += player_rect.left
        player_rect.left = 0

    # Background color change
    background_color = BACKGROUND_COLORS[(scroll_x // SCREEN_WIDTH) % len(BACKGROUND_COLORS)]

    # Draw everything
    screen.fill(background_color)
    screen.blit(player_image, (player_rect.x - scroll_x, player_rect.y))
    pygame.draw.rect(screen, (0, 0, 0), screen.get_rect(), 5)  # Border

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()