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
        instruction_text = instruction_font.render("Press Enter To Start", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        screen.blit(instruction_text, instruction_rect)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == KEYDOWN and event.key == K_RETURN:
                menu_running = False  # Only start if ENTER is pressed

        pygame.display.flip()
        clock.tick(60)


# --- LOAD MAP DATA ---
tile_map = load_tile_map("New Long Map_Main_Structure.csv")
decoration_map = load_tile_map("New Long Map_Decorations.csv")

MAP_WIDTH_IN_TILES = len(tile_map[0])
MAP_HEIGHT_IN_TILES = len(tile_map)

# --- FIND PLAYER START: Øverste og venstre gyldige tile ---
player_start = (32,288)
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

# Add border on far left and right of map
for row in range(MAP_HEIGHT_IN_TILES):
    left_rect = pygame.Rect(0, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    right_rect = pygame.Rect((MAP_WIDTH_IN_TILES - 1) * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    tiles.append((left_rect, -999))   # -999 is just a dummy ID
    tiles.append((right_rect, -999))  # you can also assign a real texture if you want



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

        self.dash_power = 12         # speed of dash
        self.dash_duration = 135     # ms dash lasts
        self.dash_cooldown = 1000   # ms between dashes
        self.dashing = False
        self.dash_timer = 0
        self.dash_cooldown_timer = 0

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
            self.vel_x = -6
            self.facing_right = False
        if keys[K_d]:
            self.vel_x = 6
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
        
        # Handle dashing
        if keys[K_LSHIFT]:
            if not self.dashing and self.dash_cooldown_timer <= 0:
                self.dashing = True
                self.dash_timer = self.dash_duration
                self.dash_cooldown_timer = self.dash_cooldown

    def update(self):

        dt = clock.get_time()  # ms since last frame

        # Tick cooldown
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt

        # Tick dash timer
        if self.dashing:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dashing = False

        # print(f"vel_y: {self.vel_y}, jumps_left: {self.jumps_remaining}, on_ground: {self.on_ground}")
        print(player.rect.x, player.rect.y)
        self.vel_y += GRAVITY  # gravity is positive

        # Horizontal movement
        # Horizontal movement
        if self.dashing:
            direction = 1 if self.facing_right else -1
            self.rect.x += direction * self.dash_power
        else:
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

# Kill counter
kill_count = 0

# --- ENEMY CLASS ---
class Enemy:
    def __init__(self, x, y, patrol_range):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.direction = 1
        self.speed = 1
        self.dead = False
        self.patrol_range = patrol_range  # (min_x, max_x)

        self.frames = [
            pygame.image.load("enemy_1.png").convert_alpha(),
            pygame.image.load("enemy_2.png").convert_alpha()
        ]
        self.frame_index = 0
        self.animation_timer = 0
        self.frame_duration = 300

    def update(self):
        if self.dead:
            return

        self.rect.x += self.direction * self.speed

        # Patrol logic within range
        if self.rect.x < self.patrol_range[0] or self.rect.x > self.patrol_range[1]:
            self.direction *= -1
            self.rect.x += self.direction * self.speed

        # Animate
        self.animation_timer += clock.get_time()
        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, screen, camera_offset):
        if not self.dead:
            screen.blit(self.frames[self.frame_index], (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1]))
            if DEBUG_MODE:
                pygame.draw.rect(screen, (255, 0, 255), (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1], 32, 32), 1)

# --- ENEMY SPAWN SETUP (clean and editable) ---
enemy_data = [
    # (tile_x, tile_y, patrol_start_x, patrol_end_x)
    (6, 8.65, 6, 11),
    (37, 10.65, 37, 41),
    (13, 6.65, 13, 16),
    (30, 6.65, 30, 35),
    (52, 13.65, 52, 57),
]

enemies = [
    Enemy(x * TILE_SIZE, y * TILE_SIZE, (start * TILE_SIZE, end * TILE_SIZE))
    for x, y, start, end in enemy_data
]
# --- Init player ---
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

    # --- ENEMY LOGIC ---
    for enemy in enemies:
        enemy.update()

        if player.rect.colliderect(enemy.rect) and not enemy.dead:
            if player.vel_y > 0:  # Kill from above
                enemy.dead = True
                player.vel_y = JUMP_STRENGTH * 0.7
                kill_count += 1
            else:
                # Insta kill if player touches from side or bottom
                player.rect.x, player.rect.y = player_start
                player.vel_y = 0
                player.jumps_remaining = player.max_jumps

    # --- CAMERA FØLGER SPILLER ---
    camera_x = player.rect.centerx - WIDTH // 2
    camera_y = player.rect.centery - HEIGHT // 2
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
            pygame.draw.rect(screen, (255, 0, 0, 100), debug_rect, 2)

    # --- DRAW ENEMIES ---
    for enemy in enemies:
        enemy.draw(screen, camera_offset)

    # --- DRAW PLAYER ---
    player.draw(screen, camera_offset)

    # --- DRAW KILL COUNTER ---
    font = pygame.font.SysFont(None, 28)
    text = font.render(f"Kills: {kill_count}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()