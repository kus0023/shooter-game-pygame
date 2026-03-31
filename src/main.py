import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter Game")

# Frame rate
clock = pygame.time.Clock()
FPS = 45

# Game variable
GRAVITY = 0.75
TILE_SIZE = 40


# movement
moving_left = False
moving_right = False
# bullets
shoot = False
# grenade
grenade = False

# Font
FONT_FUTURA = pygame.font.SysFont("futurawindows", 16)

# Colors
BG = (144, 201, 120)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (2, 48, 32)

# images
bullet_img = pygame.image.load("src/assets/img/icons/bullet.png").convert_alpha()
grenade_img = pygame.image.load("src/assets/img/icons/grenade.png").convert_alpha()
health_box_img = pygame.image.load(
    "src/assets/img/icons/health_box.png"
).convert_alpha()
ammo_box_img = pygame.image.load("src/assets/img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load(
    "src/assets/img/icons/grenade_box.png"
).convert_alpha()

item_boxes = {
    "Health": health_box_img,
    "Ammo": ammo_box_img,
    "Grenade": grenade_box_img,
}


def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenade_count=5):
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

        # bullet propeties
        self.shoot_cooldown = 0
        self.ammo = ammo
        self.max_ammo = ammo

        # health properties
        self.health = 100
        self.max_health = self.health

        # grenade properties
        self.grenades = grenade_count
        self.max_grenades = self.grenades

        # animation properties
        self.animation_dict = self.__get_animation_dict(scale)
        self.action = "Idle"
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        # image properties
        self.image: pygame.Surface = self.animation_dict[self.action][self.frame_index]
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        self.check_alive()
        # update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # player die
        if not self.is_alive:
            # if dead animation is done then kill the object
            if self.frame_index >= len(self.animation_dict["Death"]) - 1:
                self.kill()

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
        if moving_left and moving_right:
            dx = 0

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

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20

            # this value because bullet should not hit shooter player itself when created
            self_harm_protection = 10

            # create bullet in right if player is facing right or moving right
            # else create bullete in left
            x = self.rect.right if self.direction == 1 else self.rect.left
            self_harm_protection = (
                self_harm_protection if self.direction == 1 else -self_harm_protection
            )
            bullet = Bullet(x + self_harm_protection, self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1

    def throw_grenade(self):
        if self.grenades > 0:

            # this value because bullet should not hit shooter player itself when created
            self_harm_protection = 10

            # create grenade in right if player is facing right or moving right
            # else create grenade in left
            x = self.rect.right if self.direction == 1 else self.rect.left
            self_harm_protection = (
                self_harm_protection if self.direction == 1 else -self_harm_protection
            )
            grenade = Grenade(
                x + self_harm_protection, self.rect.centery, self.direction
            )
            grenade_group.add(grenade)
            self.grenades -= 1

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
                img = pygame.image.load(path).convert_alpha()
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
            length = len(self.animation_dict[self.action])
            if self.frame_index == length:
                if self.action == "Death":
                    self.frame_index = length - 1
                else:
                    self.frame_index %= length

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.is_alive = False
            self.update_action("Death")

    def draw_health_bar(self):
        # Health Bar
        border = pygame.Surface(((self.rect.width + 4), 14))
        border.fill(BLACK)
        health_bg_surf = pygame.Surface((self.rect.width, 10))
        health_bg_surf.fill(RED)
        ratio = self.health / self.max_health
        health_surf = pygame.Surface((self.rect.width * ratio, 10))
        health_surf.fill(GREEN)
        health_rect = health_bg_surf.get_rect()
        health_rect.bottomleft = self.rect.topleft
        x = health_rect.x - 2
        y = health_rect.y - 2
        screen.blit(border, (x, y))
        screen.blit(health_bg_surf, health_rect)
        screen.blit(health_surf, health_rect)

    def draw(self):
        img = pygame.transform.flip(self.image, self.flip, False)
        screen.blit(img, self.rect)

        self.draw_health_bar()


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image: pygame.Surface = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.height))

    def update(self):
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == "Health":
                player.health = min(player.health + 25, player.max_health)
            if self.item_type == "Ammo":
                player.ammo = min(player.ammo + 15, player.max_ammo)
            if self.item_type == "Grenade":
                player.grenades = min(player.grenades + 5, player.max_grenades)

            self.kill()


class AmmoUI(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 50))
        self.image.fill(DARK_GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (10, 10)

    def update(self, soldier: Soldier):
        self.image.fill(DARK_GREEN)
        padding = 5
        # create surface for bullets
        bullet_surf = FONT_FUTURA.render(f"Bullet: {soldier.ammo}", True, WHITE)

        # create surface for grenades
        grenade_surf = FONT_FUTURA.render(f"Grenades: {soldier.grenades}", True, WHITE)

        self.image.blits(
            [
                (bullet_surf, (padding, padding)),
                (grenade_surf, (padding, padding + bullet_surf.get_rect().bottom)),
            ]
        )
        screen.blit(self.image, self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += self.speed * self.direction
        # check if bullet is off the screen then destory it
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.is_alive:
                player.health -= 5
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.is_alive:
                    enemy.health -= 25
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 7
        self.vel_y = -11
        self.explode_timer = 100
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10

        # check collision with ground
        if self.rect.bottom + self.speed > 300:
            self.vel_y = 0
            self.speed = 0

        dx = self.speed * self.direction
        dy = self.vel_y

        self.rect.x += dx
        self.rect.y += dy

        # explode grenade
        self.explode_timer -= 1
        if self.explode_timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery)
            explosion_group.add(explosion)
            # do damage to player if nearby
            max_distance = TILE_SIZE * 2
            distance_x = abs(self.rect.centerx - player.rect.centerx)
            distance_y = abs(self.rect.centery - player.rect.centery)
            if distance_x < max_distance and distance_y < max_distance:
                player.health -= 30

            # do damage to enemies if nearby
            for enemy in enemy_group:
                distance_x = abs(self.rect.centerx - enemy.rect.centerx)
                distance_y = abs(self.rect.centery - enemy.rect.centery)
                if distance_x < max_distance and distance_y < max_distance:
                    enemy.health -= 50


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.frame_index = 0
        self.animation_update_time = pygame.time.get_ticks()
        self.images = self.__animation_images_list()
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def animation_update(self):
        ANIMATION_COOLDOWN = 50
        if pygame.time.get_ticks() - self.animation_update_time > ANIMATION_COOLDOWN:
            self.animation_update_time = pygame.time.get_ticks()
            self.image = self.images[self.frame_index]
            self.frame_index += 1
            self.frame_index %= len(self.images)

    def update(self):
        self.animation_update()
        if self.frame_index >= len(self.images) - 1:
            self.kill()

    def __animation_images_list(self):
        list = []
        for i in range(1, 6):
            path = f"src/assets/img/explosion/exp{i}.png"
            img = pygame.image.load(path).convert_alpha()
            list.append(img)
        return list


# create sprite group
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

x = 200
y = 200
scale = 3
player = Soldier("player", x, y, scale, 5, 20)
enemy_group.add(
    [
        Soldier("enemy", x + 100, y, scale, 5, 20),
        Soldier("enemy", x - 100, y, scale, 5, 20),
    ]
)
item_box_group.add(
    [
        ItemBox("Health", 200, 100),
        ItemBox("Ammo", 400, 100),
        ItemBox("Grenade", 600, 100),
    ]
)
ammo_ui = AmmoUI()

enemy_moving_left = True
enemy_moving_right = False

run = True
while run:
    clock.tick(45)

    draw_bg()

    player.update()
    player.draw()

    enemy_group.update()
    for enemy in enemy_group:
        enemy.draw()

    bullet_group.update()
    bullet_group.draw(screen)

    grenade_group.update()
    grenade_group.draw(screen)

    explosion_group.update()
    explosion_group.draw(screen)
    item_box_group.update()
    item_box_group.draw(screen)

    ammo_ui.update(player)

    if player.is_alive:
        # shoot bullets
        if shoot:
            player.shoot()
        elif grenade:
            player.throw_grenade()
            grenade = False
        if player.in_air:
            player.update_action("Jump")
        elif moving_left and moving_right:
            player.update_action("Idle")
        elif (moving_left or moving_right) and not player.in_air:
            player.update_action("Run")
        else:
            player.update_action("Idle")

        player.move(moving_left, moving_right)

    for enemy in enemy_group:
        if enemy.is_alive:
            if enemy.rect.left <= 0:
                enemy_moving_left = False
                enemy_moving_right = True
            if enemy.rect.right >= SCREEN_WIDTH:
                enemy_moving_left = True
                enemy_moving_right = False

            if enemy_moving_left and enemy_moving_right:
                enemy.update_action("Idle")
            elif (enemy_moving_left or enemy_moving_right) and not enemy.in_air:
                enemy.update_action("Run")
            else:
                enemy.update_action("Idle")
            enemy.move(enemy_moving_left, enemy_moving_right)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_f:
                grenade = True
            if event.key == pygame.K_w and player.is_alive:
                player.jump = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()

pygame.quit()
