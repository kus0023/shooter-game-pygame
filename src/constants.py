SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

FPS = 45

# Game variable
GRAVITY = 0.75
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
SCROLL_THRESH = 200
MAX_LEVEL = 3
level = 1
screen_scroll = 0
bg_scroll = 0
start_game = False
start_intro_transition = True

# movement
moving_left = False
moving_right = False
# bullets
shoot = False
# grenade
grenade = False


# Colors
BG = (144, 201, 120)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (2, 48, 32)
