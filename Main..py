import pygame
import pytmx
import sys

# Initialize Pygame
pygame.init()

# Set the screen dimensions
screen_width, screen_height = 1920, 1080  # Adjust these values to match your desired screen size
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tiled Map Example")

# Load the Tiled map
tmx_data = pytmx.load_pygame("Tileset/tileset.tmx")

# Find the collision layer in the map
collision_layer = None
for layer in tmx_data.visible_layers:
    if isinstance(layer, pytmx.TiledTileLayer):
        if layer.name == "collision":  # Replace with the actual name of your collision layer
            collision_layer = layer
            break

# Set the zoom level and zoom factor (you can change these as needed)
zoom_level = 1
zoom_factor = 2


# Player character class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, collision_width=16, collision_height=32):
        super().__init__()
        self.animation_frames = {
            "right": [
                pygame.image.load("player animation/walk right (1).png").convert_alpha(),
                pygame.image.load("player animation/walk right (2).png").convert_alpha(),
                pygame.image.load("player animation/walk right (3).png").convert_alpha()
            ],
            "left": [
                pygame.image.load("player animation/walk left (1).png").convert_alpha(),
                pygame.image.load("player animation/walk left (2).png").convert_alpha(),
                pygame.image.load("player animation/walk left (3).png").convert_alpha()
            ],
            "idle": [pygame.image.load("player animation/idle (2).png").convert_alpha()]
        }
        self.direction = "idle"  # Initial direction is idle
        self.image = self.animation_frames[self.direction][0]
        self.rect = self.image.get_rect()
        self.collision_width = collision_width
        self.collision_height = collision_height
        self.collision_rect = pygame.Rect(0, 0, self.collision_width, self.collision_height)
        self.set_position(x, y)  # Set the starting position
        self.speed = 2.0  # Adjusted speed for smoother movement
        self.animation_frame = 0  # Current frame index
        self.animation_speed = 10  # Adjusted animation speed
        self.moving = False  # Track if the player is moving

        # Gravity and jump attributes
        self.gravity = 0.1
        self.jump_strength = -5  # Negative value to jump upwards
        self.vertical_velocity = 0  # Vertical velocity
        self.jumping = False  # Jump state

        # Create a timer for controlling animation speed
        self.animation_timer = 0

    def set_position(self, x, y):
        self.rect.topleft = (x, y)  # Set the starting position based on pixel coordinates
        self.collision_rect.topleft = (
        x + (self.rect.width - self.collision_width) / 2, y + self.rect.height - self.collision_height)

    def check_collisions(self):
        new_x = self.collision_rect.x
        new_y = self.collision_rect.y
        ground_y = screen_height - self.collision_height

        for x, y, gid in collision_layer:
            if gid:
                tile_rect = pygame.Rect(x * tmx_data.tilewidth, y * tmx_data.tileheight, tmx_data.tilewidth,
                                        tmx_data.tileheight)

                if tile_rect.colliderect(self.collision_rect):
                    if self.vertical_velocity > 0:
                        new_y = tile_rect.top - self.collision_height
                        self.jumping = False
                        self.vertical_velocity = 0
                    elif self.vertical_velocity < 0:
                        new_y = tile_rect.bottom
                        self.vertical_velocity = 0

                    if self.speed > 0:
                        new_x = tile_rect.left - self.collision_width
                    elif self.speed < 0:
                        new_x = tile_rect.right

        x_collision = False
        for x, y, gid in collision_layer:
            if gid:
                tile_rect = pygame.Rect(x * tmx_data.tilewidth, y * tmx_data.tileheight, tmx_data.tilewidth,
                                        tmx_data.tileheight)
                if tile_rect.colliderect(self.collision_rect.move(new_x - self.collision_rect.x, 0)):
                    x_collision = True

        if not x_collision:
            self.collision_rect.x = new_x

        self.collision_rect.y = new_y

        if self.collision_rect.y > ground_y:
            self.collision_rect.y = ground_y
            self.vertical_velocity = 0
            self.jumping = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.collision_rect.x += self.speed
            self.direction = "right"
            self.moving = True
        elif keys[pygame.K_a]:
            self.collision_rect.x -= self.speed
            self.direction = "left"
            self.moving = True
        else:
            self.moving = False

        if keys[pygame.K_SPACE] and not self.jumping:
            self.jumping = True
            self.vertical_velocity = self.jump_strength

        self.vertical_velocity += self.gravity
        self.collision_rect.y += self.vertical_velocity

        self.check_collisions()

        if self.moving:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames[self.direction])
                self.image = self.animation_frames[self.direction][self.animation_frame]
                self.animation_timer = 0
        else:
            self.direction = "idle"
            self.image = self.animation_frames[self.direction][0]


# Set the desired starting position for the player character in pixels
player_start_x = 0
player_start_y = 250

# Create a player instance with the specified starting position and collision box size
player = Player(player_start_x, player_start_y, collision_width=46, collision_height=32)

# Create a Pygame sprite group for tiles and the player
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Camera variables
camera_x, camera_y = 0, 0

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_PLUS]:
        zoom_level = min(2, zoom_level + 0.1)
    if keys[pygame.K_MINUS]:
        zoom_level = max(0.5, zoom_level - 0.1)

    zoomed_screen_width = int(screen_width * zoom_level)
    zoomed_screen_height = int(screen_height * zoom_level)
    zoomed_screen = pygame.transform.scale(screen, (zoomed_screen_width, zoomed_screen_height))

    all_sprites.update()

    player_x = player.collision_rect.x
    player_y = player.collision_rect.y

    camera_x = player_x - (screen_width // 2)
    camera_y = player_y - (screen_height // 2)

    camera_x = max(0, min(camera_x, tmx_data.width * tmx_data.tilewidth - screen_width))
    camera_y = max(0, min(camera_y, tmx_data.height * tmx_data.tileheight - screen_height))

    zoomed_view = pygame.Surface((screen_width, screen_height))
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen_x = x * tmx_data.tilewidth - camera_x
                    screen_y = y * tmx_data.tileheight - camera_y
                    zoomed_view.blit(tile, (screen_x, screen_y))

    screen.fill((0, 0, 0))
    screen.blit(zoomed_view, (0, 0))

    player_x -= camera_x
    player_y -= camera_y
    screen.blit(player.image, (player_x, player_y))

    pygame.display.flip()

pygame.quit()
sys.exit()
