import pygame
from pygame.locals import *
import csv

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32
GRAVITY = 0.6
JUMP_STRENGTH = -14

# Colors
BACKGROUND_COLOR = (252,223,205,255)

# Screen Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")
clock = pygame.time.Clock()

# Load tileset image
tileset_image = pygame.image.load("tilemap.png").convert_alpha()

DEBUG_MODE = False  # Skift til False for at slå debug fra

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
                    cell = cell.strip()  # fjerner mellemrum og usynlige tegn
                    tile_row.append(int(cell))
                except:
                    tile_row.append(-1)  # hvis tomt eller fejl → ingen blok
            tile_map.append(tile_row)
    return tile_map

def main_menu():
    font_path = "Und_Font_Short.ttf"  # ← Opdater til dit fontnavn!
    font_path2 = "Und_Font_Long.ttf"  # ← Opdater til dit fontnavn!
    try:
        title_font = pygame.font.Font(font_path, 72)
        instruction_font = pygame.font.Font(font_path2, 28)
    except:
        print("Kunne ikke indlæse font – bruger standard i stedet.")
        title_font = pygame.font.SysFont(None, 72)
        instruction_font = pygame.font.SysFont(None, 28)

    menu_running = True

    while menu_running:
        screen.fill((0, 0, 0))  # sort baggrund

        # Titel (øverst centreret)
        title_text = title_font.render("Space Type Shi", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title_text, title_rect)

        # Instruktion (nederst centreret)
        instruction_text = instruction_font.render("Press Any Button To Start", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        screen.blit(instruction_text, instruction_rect)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                menu_running = False  # Starter spillet

        pygame.display.flip()
        clock.tick(60)


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
        self.jump_pressed = False
        self.coyote_time = 75 # milliseconds of coyote time
        self.coyote_timer = 0

        # Double jump
        self.max_jumps = 2
        self.jumps_remaining = self.max_jumps

        # Load animation frames
        walk1 = pygame.image.load("pixil-frame-1.png").convert_alpha()
        walk2 = pygame.image.load("pixil-frame-2.png").convert_alpha()
        walk3 = pygame.image.load("pixil-frame-3.png").convert_alpha()

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

        if keys[K_SPACE]:
            if not self.jump_pressed and self.jumps_remaining > 0:
                # First jump = full, second = weaker
                if self.jumps_remaining == self.max_jumps:
                    self.vel_y = JUMP_STRENGTH
                else:
                    self.vel_y = JUMP_STRENGTH * 0.6
                self.jumps_remaining -= 1
                self.jump_pressed = True
        else:
            self.jump_pressed = False

    def update(self):
        print(f"vel_y: {self.vel_y}, jumps_left: {self.jumps_remaining}, on_ground: {self.on_ground}")
        self.vel_y += GRAVITY  # gravity is positive

        # Horizontal movement
        self.rect.x += self.vel_x
        for tile, _ in tiles:
            if self.rect.colliderect(tile):
                if self.vel_x > 0:
                    self.rect.right = tile.left
                elif self.vel_x < 0:
                    self.rect.left = tile.right

        # Vertical movement
        self.rect.y += self.vel_y
        self.on_ground = False
        # Decrease coyote timer
            # Decrease coyote timer if we're not on ground
        if not self.on_ground:
            self.coyote_timer -= clock.get_time()

            # If we’ve fallen off and haven't jumped yet, only allow 1 jump
            if self.coyote_timer <= 0 and self.jumps_remaining == self.max_jumps:
                self.jumps_remaining = 1
        for tile, _ in tiles:
            if self.rect.colliderect(tile):
                if self.vel_y > 0:
                    self.rect.bottom = tile.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jumps_remaining = self.max_jumps  # reset double jump
                    self.coyote_timer = self.coyote_time # reset coyote time
                elif self.vel_y < 0:
                    self.rect.top = tile.bottom
                    self.vel_y = 0

        # Respawn if falling off screen
        if self.rect.top > HEIGHT:
            self.rect.x, self.rect.y = player_start
            self.vel_y = 0
            self.jumps_remaining = self.max_jumps

        # Animation
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

        if DEBUG_MODE:
            pygame.draw.rect(screen, (0, 255, 0), (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1], self.rect.width, self.rect.height), 1)

# Init player
player = Player(*player_start)

main_menu()

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
    print(f"Player Pos: {player.rect.x}, {player.rect.y}")

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

    # --- DRAW COLLISION TILES ---
    for tile_rect, tile_id in tiles:
        texture = get_tile_surface(tile_id)
        if texture:
            screen.blit(texture, (tile_rect.x - camera_offset[0], tile_rect.y - camera_offset[1]))

        if DEBUG_MODE:
            debug_rect = pygame.Rect(
                tile_rect.x - camera_offset[0],
                tile_rect.y - camera_offset[1],
                TILE_SIZE, TILE_SIZE
            )
            pygame.draw.rect(screen, (255, 0, 0, 100), debug_rect, 2)  # rød outline


    # --- DRAW PLAYER ---
    player.draw(screen, camera_offset)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
