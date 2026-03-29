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


# movement
moving_left = False
moving_right = False

# Colors
BG = (144, 201, 120)


def draw_bg():
    screen.fill(BG)


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.flip = False

        # images load
        img = pygame.image.load(f"src/assets/img/{self.char_type}/Idle/0.png")
        self.image = pygame.transform.scale(
            img,
            (int(img.get_width() * scale), int(img.get_height() * scale)),
        )
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

        self.rect.x += dx
        self.rect.y += dy

    def draw(self):
        img = pygame.transform.flip(self.image, self.flip, False)
        screen.blit(img, self.rect)


x = 200
y = 200
scale = 3
soldier = Soldier("player", x, y, scale, 5)
enemy = Soldier("enemy", x + 40, y + 40, scale, 5)

run = True
while run:
    clock.tick(45)

    draw_bg()
    soldier.draw()
    soldier.move(moving_left, moving_right)
    enemy.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
    pygame.display.flip()

pygame.quit()
