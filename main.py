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
BLUE = (0, 0, 255)
BACKGROUND_COLOR = (50, 50, 50)

# Screen Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")
clock = pygame.time.Clock()

# Load tileset image
tileset_image = pygame.image.load("tilemap.png").convert_alpha()

# Create a dictionary to hold individual tile images
tile_textures = {}

def get_tile_surface(tile_id):
    if tile_id in tile_textures:
        return tile_textures[tile_id]
    else:
        # Vi antager at tileset er 8 tiles pr række
        tiles_per_row = tileset_image.get_width() // TILE_SIZE
        tile_x = (tile_id % tiles_per_row) * TILE_SIZE
        tile_y = (tile_id // tiles_per_row) * TILE_SIZE
        tile_surface = tileset_image.subsurface(pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE))
        tile_textures[tile_id] = tile_surface
        return tile_surface

# Load TileMap from CSV File
def load_tile_map(csv_path):
    tile_map = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            tile_map.append([int(cell) for cell in row])
    return tile_map

# Load the map
tile_map = load_tile_map("map_2_Tile Layer 1.csv")

# Create a list of tile rects and corresponding tile IDs
tiles = []
player_start = (100, 100)

for row_index, row in enumerate(tile_map):
    for col_index, tile_id in enumerate(row):
        if tile_id != -1:  # -1 means empty
            tile_rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tiles.append((tile_rect, tile_id))
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
        self.vel_y += GRAVITY

        # Move X
        self.rect.x += self.vel_x
        for tile, _ in tiles:
            if self.rect.colliderect(tile):
                if self.vel_x > 0:
                    self.rect.right = tile.left
                elif self.vel_x < 0:
                    self.rect.left = tile.right

        # Move Y
        self.rect.y += self.vel_y
        self.on_ground = False
        for tile, _ in tiles:
            if self.rect.colliderect(tile):
                if self.vel_y > 0:
                    self.rect.bottom = tile.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = tile.bottom
                    self.vel_y = 0
        
        # Teleport if fallen below screen
        if self.rect.top > HEIGHT:
            self.rect.x, self.rect.y = player_start
            self.vel_y = 0

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

# Initialize Player
player = Player(*player_start)

# Game Loop
running = True
while running:
    screen.fill(BACKGROUND_COLOR)
    
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    player.move(keys)
    player.update()
    player.draw(screen)

    # Draw all tiles with textures
    for tile_rect, tile_id in tiles:
        texture = get_tile_surface(tile_id)
        screen.blit(texture, tile_rect.topleft)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
