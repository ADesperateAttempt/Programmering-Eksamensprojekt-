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
tutorial_tileset = pygame.image.load("ad-tutorial.png").convert_alpha()

DEBUG_MODE = False  # Set to True for debugging

# Load heart images
heart_images = [
    pygame.image.load("heart_0.png").convert_alpha(),
    pygame.image.load("heart_1.png").convert_alpha(),
    pygame.image.load("heart_2.png").convert_alpha(),
    pygame.image.load("heart_3.png").convert_alpha()
]

# --- PLAYER START LOCATION (x,y) ---
player_start = (32, 288)

# --- CHECKPOINT POSITIONS ---
checkpoint_positions = [
    (1950,416)                  # Checkpoint position (x, y)
]

# --- ENEMY SPAWN SETUP ---
enemy_data = [
    (6, 8.65, 6, 11),
    (37, 10.65, 37, 41),
    (13, 6.65, 13, 16),
    (30, 6.65, 30, 35),
    (55, 13.65, 55, 60),
]

# Font Setup
pause_font = pygame.font.Font("Und_Font_Short.ttf", 36)
confirm_font = pygame.font.Font("Und_Font_Short.ttf", 20)
big_font = pygame.font.Font("Und_Font_Short.ttf", 72)
small_font = pygame.font.Font("Und_Font_Short.ttf", 28)

# Pause Menu State
paused = False
pause_options = ["Resume","Restart", "Settings", "Main Menu"]
pause_index = 0
confirm_main_menu = False

# Settings Menu State
settings_open = False
settings_options = ["Return", "Save", "DEBUG"]
settings_index = 0


# Game State Variables
def reset_full_game_state():
    global player, enemies, checkpoints, current_checkpoint
    global player_lives, kill_count, paused, confirm_main_menu
    global death_state, show_game_over, confirm_quit, game_active
    global flicker_timer, show_flicker, game_over_selection, settings_open, DEBUG_MODE

    player_lives = 3
    kill_count = 0
    paused = False
    settings_open = False 
    confirm_main_menu = False
    death_state = False
    show_game_over = False
    confirm_quit = False
    flicker_timer = 0
    show_flicker = True
    game_active = False
    game_over_selection = 0
    DEBUG_MODE = False

    current_checkpoint = player_start
    player = Player(*player_start)
    player.input_blocked_until = pygame.time.get_ticks() + 500
    enemies = [Enemy(x * TILE_SIZE, y * TILE_SIZE, (start * TILE_SIZE, end * TILE_SIZE)) for x, y, start, end in enemy_data]
    checkpoints = [Checkpoint(x, y) for x, y in checkpoint_positions]


# Tile Map Loaders
def get_tile_surface(tile_id, tileset):
    try:
        tile_id = int(tile_id)
    except:
        return None
    if tile_id == -1:
        return None
    tiles_per_row = tileset.get_width() // TILE_SIZE
    tile_x = (tile_id % tiles_per_row) * TILE_SIZE
    tile_y = (tile_id // tiles_per_row) * TILE_SIZE
    try:
        return tileset.subsurface(pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE))
    except:
        return None

def load_tile_map(csv_path):
    tile_map = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            tile_row = [int(cell.strip()) if cell.strip().isdigit() else -1 for cell in row]
            tile_map.append(tile_row)
    return tile_map

# Load maps
tile_map = load_tile_map("New Long Map 2_Main_Structure.csv")
decoration_map = load_tile_map("New Long Map 2_Decorations.csv")
tutorial_map = load_tile_map("TutorialDecorations_2.csv")
MAP_WIDTH_IN_TILES = len(tile_map[0])
MAP_HEIGHT_IN_TILES = len(tile_map)

# Build tiles
tiles = []
for row_index, row in enumerate(tile_map):
    for col_index, tile_id in enumerate(row):
        if tile_id != -1:
            tile_rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tiles.append((tile_rect, tile_id))

for row in range(MAP_HEIGHT_IN_TILES):
    left_rect = pygame.Rect(0, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    right_rect = pygame.Rect((MAP_WIDTH_IN_TILES - 1) * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    tiles.append((left_rect, -999))
    tiles.append((right_rect, -999))

# Placeholder lists (will be set during reset)
checkpoints = []
enemies = []

### Define Game Variables ###
def main_menu():
    reset_full_game_state()
    global game_active
    font_path2 = "Und_Font_Long.ttf"
    try:
        title_font = pygame.font.Font("Und_Font_Short.ttf", 72)
        instruction_font = pygame.font.Font(font_path2, 28)
    except:
        title_font = pygame.font.SysFont(None, 72)
        instruction_font = pygame.font.SysFont(None, 28)

    menu_running = True
    while menu_running:
        screen.fill((0, 0, 0))
        screen.blit(title_font.render("Space Type Shi", True, (255, 255, 255)), (WIDTH//2 - 200, HEIGHT//3))
        screen.blit(instruction_font.render("Press Enter To Start", True, (255, 255, 255)), (WIDTH//2 - 140, HEIGHT - 80))
        screen.blit(instruction_font.render("Press ESC To Quit", True, (255, 255, 255)), (WIDTH//2 - 130, HEIGHT - 40))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    menu_running = False
                    game_active = True
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    exit()
        pygame.display.flip()
        clock.tick(60)

# --- BUILD COLLISION TILES ---
tiles = []
for row_index, row in enumerate(tile_map):
    for col_index, tile_id in enumerate(row):
        if tile_id != -1:
            tile_rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tiles.append((tile_rect, tile_id))

# --- BUILD DECORATION TILE DATA ONLY ---
decoration_tiles = []
for row_index, row in enumerate(decoration_map):
    for col_index, tile_id in enumerate(row):
        if tile_id != -1:
            tile_rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            decoration_tiles.append((tile_rect, tile_id))

# --- BUILD TUTORIAL DECORATION TILE DATA ONLY ---
tutorial_deco_tiles = []
for row_index, row in enumerate(tutorial_map):
    for col_index, tile_id in enumerate(row):
        if tile_id != -1:
            tile_rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tutorial_deco_tiles.append((tile_rect, tile_id))

# Add map borders
for row in range(MAP_HEIGHT_IN_TILES):
    left_rect = pygame.Rect(0, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    right_rect = pygame.Rect((MAP_WIDTH_IN_TILES - 1) * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    tiles.append((left_rect, -999))
    tiles.append((right_rect, -999))


# --- BUILD DECORATION TILE DATA ONLY (don't draw yet) ---
decoration_tiles = []
for row_index, row in enumerate(decoration_map):
    for col_index, tile_id in enumerate(row):
        if tile_id != -1:
            tile_rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            decoration_tiles.append((tile_rect, tile_id))

# --- BUILD TUTORIAL DECORATION TILES (no collision) ---
tutorial_deco_tiles = []
for row_index, row in enumerate(tutorial_map):
    for col_index, tile_id in enumerate(row):
        if tile_id != -1:
            tile_rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tutorial_deco_tiles.append((tile_rect, tile_id))

# --- CHECKPOINT CLASS ---
class Checkpoint:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 64, 64)
        self.activated = False
        self.frames_red = [
            pygame.image.load(f"checkpoint_{i}.png").convert_alpha()
            for i in range(6)
        ]
        self.frames_green = [
            pygame.image.load(f"checkpoint_green_{i}.png").convert_alpha()
            for i in range(6)
        ]
        self.frame_index = 0
        self.animation_timer = 0
        self.frame_duration = 150  # ms
        self.display_message = False
        self.message_timer = 0

    def update(self):
        self.animation_timer += clock.get_time()
        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % 6

        if self.display_message:
            self.message_timer -= clock.get_time()
            if self.message_timer <= 0:
                self.display_message = False

    def draw(self, screen, camera_offset):
        frames = self.frames_green if self.activated else self.frames_red
        frame = frames[self.frame_index]
        screen.blit(frame, (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1]))

        if self.display_message:
            font = pygame.font.Font("Und_Font_Short.ttf", 24)
            message = font.render("Your Progress Has Been Saved", True, (0, 255, 0))
            msg_rect = message.get_rect(center=(WIDTH // 2, 40))
            screen.blit(message, msg_rect)


# --- PLAYER CLASS ---
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 29, 64)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.jump_pressed = False
        self.coyote_time = 75 # milliseconds of coyote time
        self.coyote_timer = 0
        self.input_blocked_until = 0  # Default value


        self.dash_power = 12            # speed of dash
        self.dash_duration = 200        # ms dash lasts
        self.dash_cooldown = 1000       # ms between dashes
        self.dashing = False
        self.dash_timer = 0
        self.dash_cooldown_timer = 0

        self.last_debug_time = 0
        

        # Double jump
        self.max_jumps = 2
        self.jumps_remaining = self.max_jumps

        # Load animation frames
        walk1 = pygame.image.load("player_0.png").convert_alpha()
        walk2 = pygame.image.load("player_1.png").convert_alpha()
        walk3 = pygame.image.load("player_2.png").convert_alpha()
        walk4 = pygame.image.load("player_3.png").convert_alpha()

        self.walk_right = [walk1, walk2, walk3, walk4, walk3, walk2]
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

        # --- Handle jumping (even during dash, to allow canceling dash) ---
        if keys[K_SPACE]:
            if not self.jump_pressed and self.jumps_remaining > 0:
                # Cancel dash if active
                if self.dashing:
                    self.dashing = False
                    self.dash_timer = 0

                if self.jumps_remaining == self.max_jumps:
                    self.vel_y = JUMP_STRENGTH
                else:
                    self.vel_y = JUMP_STRENGTH * 0.6

                self.jumps_remaining -= 1
                self.jump_pressed = True
        else:
            self.jump_pressed = False

        # --- Handle dashing ---
        if keys[K_LSHIFT]:
            if not self.dashing and self.dash_cooldown_timer <= 0:
                self.dashing = True
                self.dash_timer = self.dash_duration
                self.dash_cooldown_timer = self.dash_cooldown
                self.vel_y = 0  # zero vertical movement during dash

    def update(self):
        global player_lives, death_state, death_timer, current_checkpoint

        dt = clock.get_time()  # ms since last frame

        # Tick cooldown
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt

        # Tick dash timer
        if self.dashing:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dashing = False

        # And replace your debug print section with this
        current_time = pygame.time.get_ticks()
        if current_time - self.last_debug_time > 1000:  # 1000 ms = 1 second
            print(f"vel_y: {self.vel_y}, jumps_left: {self.jumps_remaining}, on_ground: {self.on_ground}")
            print(self.rect.x, self.rect.y)
            self.last_debug_time = current_time

        
        if self.dashing:
            self.vel_y += GRAVITY * 0.05  # Reduced gravity during dash
        else:
            self.vel_y += GRAVITY


        # Horizontal movement
        
        # DASHING MOVEMENT WITH COLLISION
        if self.dashing:
            direction = 1 if self.facing_right else -1
            dash_step = direction * self.dash_power

            for _ in range(abs(dash_step)):
                self.rect.x += direction
                for tile, _ in tiles:
                    if self.rect.colliderect(tile):
                        if direction > 0:
                            self.rect.right = tile.left
                        else:
                            self.rect.left = tile.right
                        self.dashing = False
                        break
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
        if player.rect.top > HEIGHT:
            player_lives -= 1
            if player_lives <= 0:
                death_state = True
                death_timer = pygame.time.get_ticks()
            else:
                player.rect.x, player.rect.y = current_checkpoint
                player.vel_y = 0
                player.jumps_remaining = player.max_jumps


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
        draw_x = self.rect.x - camera_offset[0] - (self.image.get_width() - self.rect.width) // 2
        draw_y = self.rect.y - camera_offset[1]
        screen.blit(self.image, (draw_x, draw_y))

        if DEBUG_MODE:
            pygame.draw.rect(screen, (0, 255, 0), (
                self.rect.x - camera_offset[0],
                self.rect.y - camera_offset[1],
                self.rect.width,
                self.rect.height), 1)

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
        if self.rect.x < self.patrol_range[0] or self.rect.x > self.patrol_range[1]:
            self.direction *= -1
            self.rect.x += self.direction * self.speed
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
    (55, 13.65, 55, 60),
]

enemies = [
    Enemy(x * TILE_SIZE, y * TILE_SIZE, (start * TILE_SIZE, end * TILE_SIZE))
    for x, y, start, end in enemy_data
]

current_checkpoint = player_start  # default spawn point

main_menu()

reset_full_game_state()

# --- GAME LOOP ---
running = True
while running:
    dt = clock.tick(60)
    screen.fill(BACKGROUND_COLOR)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                if settings_open:
                    settings_open = False
                elif paused:
                    paused = False
                else:
                    paused = True
                    confirm_main_menu = False
            elif settings_open:
                if event.key in [K_w, K_UP]:
                    settings_index = (settings_index - 1) % len(settings_options)
                elif event.key in [K_s, K_DOWN]:
                    settings_index = (settings_index + 1) % len(settings_options)
                elif event.key in [K_SPACE, K_RETURN]:
                    selected_setting = settings_options[settings_index]
                    if selected_setting == "Return":
                        settings_open = False
                    elif selected_setting == "DEBUG":
                        DEBUG_MODE = not DEBUG_MODE
            elif paused:
                if event.key in [K_w, K_UP]:
                    pause_index = (pause_index - 1) % len(pause_options)
                elif event.key in [K_s, K_DOWN]:
                    pause_index = (pause_index + 1) % len(pause_options)
                elif event.key in [K_SPACE, K_RETURN]:
                    selected = pause_options[pause_index]
                    if selected == "Resume":
                        paused = False
                    elif selected == "Restart":
                        reset_full_game_state()
                    elif selected == "Settings":
                        settings_open = True
                        settings_index = 0
                    elif selected == "Main Menu":
                        if confirm_main_menu:
                            reset_full_game_state()
                            main_menu()
                        else:
                            confirm_main_menu = True

    if not paused:
        # Update checkpoints
        for checkpoint in checkpoints:
            checkpoint.update()
            if player.rect.colliderect(checkpoint.rect) and not checkpoint.activated:
                checkpoint.activated = True
                current_checkpoint = (checkpoint.rect.x, checkpoint.rect.y)
                checkpoint.display_message = True
                checkpoint.message_timer = 2000  # ms

        if death_state:
            now = pygame.time.get_ticks()
            elapsed = now - death_timer

            if elapsed >= 4000 and not show_game_over:
                show_game_over = True
                fade_start = pygame.time.get_ticks()

        else:
            if pygame.time.get_ticks() >= player.input_blocked_until:
                player.move(keys)
            player.update()
            for enemy in enemies:
                enemy.update()
                if player.rect.colliderect(enemy.rect) and not enemy.dead:
                    if player.vel_y > 0:
                        enemy.dead = True
                        player.vel_y = JUMP_STRENGTH * 0.7
                        kill_count += 1
                        player.jumps_remaining = player.max_jumps  # <-- Regain double jumps
                    else:
                        if current_checkpoint == player_start:
                            player_lives -= 1
                            if player_lives <= 0:
                                death_state = True
                                death_timer = pygame.time.get_ticks()
                            else:
                                player.rect.x, player.rect.y = current_checkpoint
                                player.vel_y = 0
                                player.jumps_remaining = player.max_jumps

                        else:
                            player_lives -= 1
                            if player_lives <= 0:
                                death_state = True
                                death_timer = pygame.time.get_ticks()
                            else:
                                player.rect.x, player.rect.y = current_checkpoint
                                player.vel_y = 0
                                player.jumps_remaining = player.max_jumps



    camera_x = player.rect.centerx - WIDTH // 2
    camera_y = player.rect.centery - HEIGHT // 2
    camera_x = max(0, camera_x)
    camera_y = max(0, camera_y)
    camera_offset = (camera_x, camera_y)

    # Draw main decorations
    for deco_rect, deco_id in decoration_tiles:
        texture = get_tile_surface(deco_id, tileset_image)

        if texture:
            screen.blit(texture, (deco_rect.x - camera_offset[0], deco_rect.y - camera_offset[1]))

    # Draw tutorial decorations
    for deco_rect, deco_id in tutorial_deco_tiles:
        texture = get_tile_surface(deco_id, tutorial_tileset)
        if texture:
            screen.blit(texture, (deco_rect.x - camera_offset[0], deco_rect.y - camera_offset[1]))

            
    # Draw decorations from tutorial tileset
    for row_index, row in enumerate(tutorial_map):
        for col_index, tile_id in enumerate(row):
            if tile_id != -1:
                tile_rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                texture = get_tile_surface(tile_id, tutorial_tileset)
                if texture:
                    screen.blit(texture, (tile_rect.x - camera_offset[0], tile_rect.y - camera_offset[1]))


    for tile_rect, tile_id in tiles:
        texture = get_tile_surface(tile_id, tileset_image)

        if texture:
            screen.blit(texture, (tile_rect.x - camera_offset[0], tile_rect.y - camera_offset[1]))
        if DEBUG_MODE:
            debug_rect = pygame.Rect(tile_rect.x - camera_offset[0], tile_rect.y - camera_offset[1], TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (255, 0, 0, 100), debug_rect, 2)

    for enemy in enemies:
        enemy.draw(screen, camera_offset)

    for checkpoint in checkpoints:
            checkpoint.draw(screen, camera_offset)

    player.draw(screen, camera_offset)

    font = pygame.font.SysFont(None, 28)
    text = font.render(f"Kills: {kill_count}", True, (0, 0, 0))
    
    if not death_state:
        heart_index = max(0, 3 - player_lives)
        heart_img = heart_images[heart_index]
        screen.blit(heart_img, (WIDTH - 42, HEIGHT - 42))
        lives_text = font.render(f"{player_lives}/3", True, (0, 0, 0))
        screen.blit(lives_text, (WIDTH - 90, HEIGHT - 35))
    else:
        # Player is dead, flicker sad heart before broken heart
        elapsed = pygame.time.get_ticks() - death_timer
        if elapsed < 3000:
            flicker_timer += dt
            if flicker_timer >= 425:
                flicker_timer = 0
                show_flicker = not show_flicker
            if show_flicker:
                heart_img = heart_images[2]  # sad face heart (heart_2.png)
                screen.blit(heart_img, (WIDTH - 42, HEIGHT - 42))
                lives_text = font.render("0/3", True, (0, 0, 0))
                screen.blit(lives_text, (WIDTH - 90, HEIGHT - 35))
        else:
            heart_img = heart_images[3]  # broken heart (heart_3.png)
            screen.blit(heart_img, (WIDTH - 42, HEIGHT - 42))
            lives_text = font.render("0/3", True, (0, 0, 0))
            screen.blit(lives_text, (WIDTH - 90, HEIGHT - 35))



    screen.blit(text, (10, 10))

    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        if settings_open:
            for i, option in enumerate(settings_options):
                color = (255, 255, 255)
                rendered = pause_font.render(option + (" : ON" if option == "DEBUG" and DEBUG_MODE else " : OFF" if option == "DEBUG" else ""), True, color)
                rect = rendered.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 50))
                screen.blit(rendered, rect)
                if i == settings_index:
                    pygame.draw.rect(screen, (255, 255, 255), rect.inflate(10, 10), 2)
        else:
            for i, option in enumerate(pause_options):
                color = (255, 255, 255)
                rendered = pause_font.render(option, True, color)
                rect = rendered.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 50))
                screen.blit(rendered, rect)
                if i == pause_index:
                    pygame.draw.rect(screen, (255, 255, 255), rect.inflate(10, 10), 2)

            if confirm_main_menu and pause_options[pause_index] == "Main Menu":
                confirm_font = pygame.font.Font("Und_Font_Short.ttf", 20)
                msg = confirm_font.render("Press Enter again to return to menu", True, (255, 100, 100))
                screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + len(pause_options) * 60)))
                
    if show_game_over:
                fade_elapsed = pygame.time.get_ticks() - fade_start
                alpha = min(255, int((fade_elapsed / 2000) * 255))

                black_overlay = pygame.Surface((WIDTH, HEIGHT))
                black_overlay.fill((0, 0, 0))
                black_overlay.set_alpha(alpha)
                screen.blit(black_overlay, (0, 0))

                if fade_elapsed > 2000:
                    died_text = big_font.render("You Died", True, (255, 0, 0))
                    try_again = small_font.render("Continue or Quit?", True, (255, 255, 255))

                    screen.blit(died_text, died_text.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
                    screen.blit(try_again, try_again.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

                    options = ["Continue", "Quit"]
                    for i, option in enumerate(options):
                        color = (0, 255, 0) if i == 0 else (255, 0, 0)
                        if game_over_selection == i:
                            rendered = small_font.render(option, True, color)
                        else:
                            rendered = small_font.render(option, True, (255, 255, 255))
                        screen.blit(rendered, rendered.get_rect(center=(WIDTH // 2 - 100 + 200 * i, HEIGHT // 2 + 60)))

                    if confirm_quit and game_over_selection == 1:
                        warning = small_font.render("If you quit now, any progress will be lost.", True, (255, 100, 100))
                        screen.blit(warning, warning.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120)))

# Input handling during game over
    if show_game_over and fade_elapsed > 2000:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key in [K_a, K_LEFT]:
                    game_over_selection = (game_over_selection - 1) % 2
                elif event.key in [K_d, K_RIGHT]:
                    game_over_selection = (game_over_selection + 1) % 2
                elif event.key in [K_RETURN, K_SPACE]:
                    if game_over_selection == 0:
                        # Continue game
                        reset_full_game_state()
                    elif game_over_selection == 1:
                        if not confirm_quit:
                            confirm_quit = True
                        else:
                            reset_full_game_state()
                            main_menu()
                            
    pygame.display.flip()

pygame.quit()