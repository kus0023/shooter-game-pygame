import pygame

pygame_variable = pygame.init()
print("pygame initialised", pygame_variable)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter Game")

# Frame rate
clock = pygame.time.Clock()
FPS = 45

# Game variable
GRAVITY = 0.75


# movement
moving_left = False
moving_right = False

# Colors
BG = (144, 201, 120)
RED = (255, 0, 0)


def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        # character properties
        self.char_type = char_type
        self.is_alive = True

        # movement properties
        self.speed = speed
        self.direction = 1
        self.flip = False

        # jump propterties
        self.jump = False
        self.vel_y = 0
        self.in_air = True

        # animation properties
        self.animation_dict = self.__get_animation_dict(scale)
        self.action = "Idle"
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        # image properties
        self.image = self.animation_dict[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Jump
        if self.jump and not self.in_air:
            self.jump = False
            self.vel_y = -11
            self.in_air = True
        # gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # collision on ground
        if self.rect.bottom + dy > 300:
            dy = 0
            self.vel_y = 0
            self.in_air = False

        self.rect.x += dx
        self.rect.y += dy

    def __get_animation_dict(self, scale: int):
        # It will create a dictionary of all images I have for all the actions
        # for example
        # animation_dict = { "idle": [images...], "run": [images..], ...so on}
        animation_dict = {}

        # generic function to load all images of action and add it to dictionary
        def load_image_from_asset(name, size, scale=scale):
            animation_dict[name] = list()
            for i in range(size):
                path = f"src/assets/img/{self.char_type}/{name}/{i}.png"
                img = pygame.image.load(path)
                # scale up the image
                width = int(img.get_width() * scale)
                height = int(img.get_height() * scale)
                img = pygame.transform.scale(img, (width, height))
                # add to dictionary
                animation_dict[name].append(img)

        load_image_from_asset("Idle", 5)
        load_image_from_asset("Death", 8)
        load_image_from_asset("Jump", 1)
        load_image_from_asset("Run", 6)

        return animation_dict

    def update_action(self, new_action: str):
        if new_action not in self.animation_dict.keys():
            raise Exception(f"new_action={new_action} is not a valid action")
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.image = self.animation_dict[self.action][self.frame_index]

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_dict[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            self.frame_index %= len(self.animation_dict[self.action])

    def draw(self):
        img = pygame.transform.flip(self.image, self.flip, False)
        screen.blit(img, self.rect)


x = 200
y = 200
scale = 3
player = Soldier("enemy", x, y, scale, 5)

run = True
while run:
    clock.tick(45)

    draw_bg()

    player.draw()

    player.update_animation()

    if player.is_alive:
        if player.in_air:
            player.update_action("Jump")
        elif (moving_left or moving_right) and player.vel_y == 0:
            player.update_action("Run")
        else:
            player.update_action("Idle")

        player.move(moving_left, moving_right)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w and player.is_alive:
                player.jump = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
    pygame.display.flip()

pygame.quit()
