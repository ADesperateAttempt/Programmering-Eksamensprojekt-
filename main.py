import pygame
from pygame.locals import *
import csv

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32
GRAVITY = 0.7
JUMP_STRENGTH = -14

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
BACKGROUND_COLOR = (50, 50, 50)

# Screen Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")
clock = pygame.time.Clock()

# Load TileMap from CSV File
def load_tile_map(csv_path):
    tile_map = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            tile_map.append([int(cell) for cell in row])
    return tile_map

# Replace with actual CSV file path
tile_map = load_tile_map("map_2_Tile Layer 1.csv")

tiles = []
player_start = (100, 100)  # Default position
for row_index, row in enumerate(tile_map):
    for col_index, tile in enumerate(row):
        if tile != -1:  # Any tile that is NOT -1 is a solid block
            tiles.append(pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            # Set player start position on the first solid ground found
            if player_start == (100, 100):
                player_start = (col_index * TILE_SIZE, row_index * TILE_SIZE - TILE_SIZE)

# Player Class
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def move(self, keys):
        self.vel_x = 0
        if keys[K_a]:
            self.vel_x = -5
        if keys[K_d]:
            self.vel_x = 5
        if keys[K_SPACE] and self.on_ground:
            self.vel_y = JUMP_STRENGTH

    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY

        # Move X
        self.rect.x += self.vel_x
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.vel_x > 0:
                    self.rect.right = tile.left
                if self.vel_x < 0:
                    self.rect.left = tile.right

        # Move Y
        self.rect.y += self.vel_y
        self.on_ground = False
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.vel_y > 0:
                    self.rect.bottom = tile.top
                    self.vel_y = 0
                    self.on_ground = True
                if self.vel_y < 0:
                    self.rect.top = tile.bottom
                    self.vel_y = 0

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

# Initialize Player at the first ground tile
player = Player(*player_start)

# Game Loop
running = True
while running:
    screen.fill(BACKGROUND_COLOR)
    
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    
    # Update and draw player
    player.move(keys)
    player.update()
    player.draw(screen)
    
    # Draw tiles
    for tile in tiles:
        pygame.draw.rect(screen, GRAY, tile)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()