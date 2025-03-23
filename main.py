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
    try:
        tile_id = int(tile_id)
    except:
        return None
    if tile_id == -1:
        return None
    if tile_id in tile_textures:
        return tile_textures[tile_id]
    else:
        tiles_per_row = tileset_image.get_width() // TILE_SIZE
        tile_x = (tile_id % tiles_per_row) * TILE_SIZE
        tile_y = (tile_id // tiles_per_row) * TILE_SIZE
        try:
            tile_surface = tileset_image.subsurface(pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE))
            tile_textures[tile_id] = tile_surface
            return tile_surface
        except:
            return None

# Load TileMap from CSV with safe int conversion
def load_tile_map(csv_path):
    tile_map = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            tile_row = []
            for cell in row:
                try:
                    tile_row.append(int(cell))
                except:
                    tile_row.append(-1)
            tile_map.append(tile_row)
    return tile_map

# --- LOAD MAP DATA ---
tile_map = load_tile_map("New Long Map_Main_Structure.csv")
decoration_map = load_tile_map("New Long Map_Decorations.csv")

# --- FIND PLAYER START: Øverste og venstre gyldige tile ---
player_start = (0,13)
for row_index, row in enumerate(tile_map):
    for col_index, tile_id in enumerate(row):
        if tile_id != -1:
            player_start = (col_index * TILE_SIZE, row_index * TILE_SIZE - TILE_SIZE)
            break
    if player_start is not None:
        break

# --- BUILD COLLISION TILES ---
tiles = []
for row_index, row in enumerate(tile_map):
    for col_index, tile_id in enumerate(row):
        if tile_id != -1:
            tile_rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tiles.append((tile_rect, tile_id))



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
        self.frame_duration = 120
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

        self.rect.x += self.vel_x
        for tile, _ in tiles:
            if self.rect.colliderect(tile):
                if self.vel_x > 0:
                    self.rect.right = tile.left
                elif self.vel_x < 0:
                    self.rect.left = tile.right

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

        if self.rect.top > HEIGHT:
            self.rect.x, self.rect.y = player_start
            self.vel_y = 0

        if self.vel_x != 0:
            self.animation_timer += clock.get_time()
            if self.animation_timer >= self.frame_duration:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_right)
        else:
            self.current_frame = 1

        self.image = self.walk_right[self.current_frame] if self.facing_right else self.walk_left[self.current_frame]

    def draw(self, screen, camera_offset):
        screen.blit(self.image, (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1]))

# Init player
player = Player(*player_start)

# --- GAME LOOP ---
running = True
while running:
    screen.fill(BACKGROUND_COLOR)

    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    player.move(keys)
    player.update()

    # --- CAMERA FØLGER SPILLER ---
    camera_x = player.rect.centerx - WIDTH // 2
    camera_y = player.rect.centery - HEIGHT // 2

    # Valgfrit: Begræns kameraet så det ikke går udenfor venstre/top grænser
    camera_x = max(0, camera_x)
    camera_y = max(0, camera_y)

    camera_offset = (camera_x, camera_y)

    # --- DRAW DEKORATIONER ---
    for deco_rect, deco_id in decoration_tiles:
        texture = get_tile_surface(deco_id)
        if texture:
            screen.blit(texture, (deco_rect.x - camera_offset[0], deco_rect.y - camera_offset[1]))

    # --- DRAW KOLLISIONSTILES ---
    for tile_rect, tile_id in tiles:
        texture = get_tile_surface(tile_id)
        if texture:
            screen.blit(texture, (tile_rect.x - camera_offset[0], tile_rect.y - camera_offset[1]))

    # --- DRAW PLAYER ---
    player.draw(screen, camera_offset)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
