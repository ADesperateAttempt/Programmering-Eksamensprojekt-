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

class Player:
    def __init__(self, image_path):
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.topleft = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT)
        self.x_velocity = 0
        self.y_velocity = 0
        self.on_ground = False

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x_velocity = -PLAYER_SPEED
        elif keys[pygame.K_RIGHT]:
            self.x_velocity = PLAYER_SPEED
        else:
            self.x_velocity = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.y_velocity = -JUMP_HEIGHT
            self.on_ground = False

    def apply_gravity(self):
        self.y_velocity += GRAVITY

    def update_position(self):
        self.rect.x += self.x_velocity
        self.rect.y += self.y_velocity

        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.y_velocity = 0
            self.on_ground = True

    def draw(self, screen, scroll_x):
        screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))

class GameManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Platformer Game")
        self.clock = pygame.time.Clock()
        self.player = Player('mario smol.png')
        self.scroll_x = 0
        self.running = True

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.player.handle_keys()
        self.player.apply_gravity()
        self.player.update_position()
        self.update_scroll()

    def update_scroll(self):
        if self.player.rect.right > SCREEN_WIDTH:
            self.scroll_x += self.player.rect.right - SCREEN_WIDTH
            self.player.rect.right = SCREEN_WIDTH
        elif self.player.rect.left < 0:
            self.scroll_x += self.player.rect.left
            self.player.rect.left = 0

    def draw(self):
        background_color = BACKGROUND_COLORS[(self.scroll_x // SCREEN_WIDTH) % len(BACKGROUND_COLORS)]
        self.screen.fill(background_color)
        self.player.draw(self.screen, self.scroll_x)
        pygame.draw.rect(self.screen, (0, 0, 0), self.screen.get_rect(), 5)  # Border
        pygame.display.flip()

if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run()