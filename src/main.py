import pygame

pygame_variable = pygame.init()
print("pygame initialised", pygame_variable)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter Game")


class Soldier(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("src/assets/img/player/Idle/0.png").convert()
        self.image = pygame.transform.scale(
            img,
            (int(img.get_width() * scale), int(img.get_height() * scale)),
        )
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self):
        screen.blit(self.image, self.rect)


x = 200
y = 200
scale = 3
soldier = Soldier(x, y, scale)

run = True
while run:

    soldier.draw()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

pygame.quit()
