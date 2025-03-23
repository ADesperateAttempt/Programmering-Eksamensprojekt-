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
BACKGROUND_COLOR = (50, 50, 50)

# Screen Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")
clock = pygame.time.Clock()

# Load tileset image
tileset_image = pygame.image.load("tilemap.png").convert_alpha()

# Dictionary for caching tile surfaces
tile_textures = {}

def get_tile_surface(tile_id):
    if tile_id in tile_textures:
        return tile_textures[tile_id]
    else:
        tiles_per_row = tileset_image.get_width() // TILE_SIZE
        tile_x = (tile_id % tiles_per_row) * TILE_SIZE
        tile_y = (tile_id // tiles_per_row) * TILE_SIZE
        tile_surface = tileset_image.subsurface(pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE))
        tile_textures[tile_id] = tile_surface
        return tile_surface

# Load TileMap from CSV
def load_tile_map(csv_path):
    tile_map = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            tile_map.append([int(cell) for cell in row])
    return tile_map

# --- LOAD MAP DATA ---
tile_map = load_tile_map("map_2_Tile Layer 1.csv")       # collision tiles
decoration_map = load_tile_map("map_2_Tile Layer 2.csv") # decorations (no collision)

# --- BUILD COLLISION TILES ---
tiles = []
player_start = (100, 100)
for row_index, row in enumerate(tile_map):
    for col_index, tile_id in enumerate(row):
        if tile_id != -1:
            tile_rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tiles.append((tile_rect, tile_id))
            if player_start == (100, 100):
                player_start = (col_index * TILE_SIZE, row_index * TILE_SIZE - TILE_SIZE)

# --- BUILD DECORATION TILES (no collision) ---
decoration_tiles = []
for row_index, row in enumerate(decoration_map):
    for col_index, tile_id in enumerate(row):
        if tile_id != -1:
            tile_rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            decoration_tiles.append((tile_rect, tile_id))

# --- PLAYER CLASS ---
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

        # Load animation frames
        walk1 = pygame.image.load("pixil-frame-1.png").convert_alpha()
        walk2 = pygame.image.load("pixil-frame-2.png").convert_alpha()
        walk3 = pygame.image.load("pixil-frame-3.png").convert_alpha()

        # Animation order: 1 → 2 → 3 → 2 → repeat
        self.walk_right = [walk1, walk2, walk3, walk2]
        self.walk_left = [pygame.transform.flip(f, True, False) for f in self.walk_right]

        self.current_frame = 0
        self.animation_timer = 0
        self.frame_duration = 120  # ms per frame
        self.facing_right = True
        self.image = self.walk_right[0]

    def move(self, keys):
        self.vel_x = 0
        if keys[K_a]:
            self.vel_x = -5
            self.facing_right = False
        if keys[K_d]:
            self.vel_x = 5
            self.facing_right = True
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

        # Teleport if fallen off screen
        if self.rect.top > HEIGHT:
            self.rect.x, self.rect.y = player_start
            self.vel_y = 0

        # Animation update
        if self.vel_x != 0:
            self.animation_timer += clock.get_time()
            if self.animation_timer >= self.frame_duration:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_right)
        else:
            self.current_frame = 1  # idle pose

        self.image = self.walk_right[self.current_frame] if self.facing_right else self.walk_left[self.current_frame]

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

# Initialize player
player = Player(*player_start)

# --- GAME LOOP ---
running = True
while running:
    screen.fill(BACKGROUND_COLOR)

    # Handle events
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    # Draw background decoration layer (Layer 2)
    for deco_rect, deco_id in decoration_tiles:
        deco_texture = get_tile_surface(deco_id)
        screen.blit(deco_texture, deco_rect.topleft)

    # Update player
    player.move(keys)
    player.update()

    # Draw collision tiles (Layer 1)
    for tile_rect, tile_id in tiles:
        texture = get_tile_surface(tile_id)
        screen.blit(texture, tile_rect.topleft)

    # Draw player
    player.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
