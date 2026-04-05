import pygame, random, csv

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
level = 1
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21


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

# Tiles
tile_img_list = []

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
for i in range(TILE_TYPES):
    img = pygame.image.load(f"src/assets/img/tile/{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    tile_img_list.append(img)

item_boxes = {
    "Health": health_box_img,
    "Ammo": ammo_box_img,
    "Grenade": grenade_box_img,
}


def draw_bg():
    screen.fill(BG)


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

        # Bot movement
        self.start_pos = x
        self.is_idle = False
        self.rest_time = pygame.time.get_ticks()
        self.player_detection_distance = TILE_SIZE * 2

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
        width = self.image.get_width()
        height = self.image.get_height()
        for tile in world.obstacle_list:
            # collision in horizontal direction
            if tile[1].colliderect(dx + self.rect.x, self.rect.y, width, height):
                dx = 0
            # collision in vertical direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, width, height):
                dy = 0
                # if jumping - below tile
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:  # falling - above ground
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom
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
            grenade = Grenade(self.rect.centerx, self.rect.centery, self.direction)
            grenade_group.add(grenade)
            self.grenades -= 1

    def bot_movement(self):
        if self.is_alive:

            # check if player is in sight meaning in front of enemy at certain distance
            # if so, Stop the enemy and shoot in direction of player
            size = (self.player_detection_distance, 1)
            temp_rect = pygame.Rect((0, 0), size)
            if self.direction == 1:
                temp_rect.midleft = self.rect.midright
            else:
                temp_rect.midright = self.rect.midleft

            if player.rect.colliderect(temp_rect):
                self.move(False, False)
                self.shoot()
                self.update_action("Idle")
                return  # don't Run the below code Just stop and shoot

            # choose random time from 1 to 15 second
            # then either move the bot or stop the bot
            if pygame.time.get_ticks() - self.rest_time > random.randint(1000, 15000):
                self.rest_time = pygame.time.get_ticks()
                if not self.is_idle:  # if moving then stop the bot
                    self.is_idle = True
                else:  # if not moving then move the bot in random direction
                    self.direction = random.choice([1, -1])
                    self.is_idle = False

            # move to and fro in certain distance
            if self.direction == 1:  # moving Right
                if abs(self.rect.right - self.start_pos) >= TILE_SIZE * 4:
                    self.direction *= -1
            if self.direction == -1:  # moving Left
                if abs(self.rect.left - self.start_pos) >= TILE_SIZE * 4:
                    self.direction *= -1

            # control the animation
            if self.is_idle:
                self.move(False, False)
                self.update_action("Idle")
            elif self.direction == 1:
                self.move(False, True)
                self.update_action("Run")
            elif self.direction == -1:
                self.move(True, False)
                self.update_action("Run")

            self.rest_time += 1

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


class World:
    def __init__(self):
        # Tuple of (tile_image, tile_rect)
        self.obstacle_list: list[tuple[pygame.Surface, pygame.Rect]] = []

    def process_data(self, world_data):
        # iterating through all the top left point of tile

        player = None
        scale = 1.75
        for row_idx, row in enumerate(world_data):  # Row means Y
            for col_idx, tile in enumerate(row):  # Col means X
                pt_x = col_idx * TILE_SIZE
                pt_y = row_idx * TILE_SIZE
                tile_img = tile_img_list[tile]
                if isinstance(tile_img, pygame.Surface):
                    tile_rect = tile_img.get_rect()
                    tile_rect.topleft = (pt_x, pt_y)
                else:
                    raise Exception("Wrong image of Tile")

                if tile == -1:
                    continue
                elif tile >= 0 and tile <= 8:
                    self.obstacle_list.append((tile_img, tile_rect))
                elif tile == 9 or tile == 10:  # water
                    Water(tile_img, decoration_group, topleft=tile_rect.topleft)
                elif tile >= 11 and tile <= 14:  # stone, box, grass decoration
                    Decorations(tile_img, decoration_group, topleft=tile_rect.topleft)
                elif tile == 15:  # player
                    player = Soldier("player", pt_x, pt_y, scale, 5, 20)
                elif tile == 16:  # enemy
                    enemy_group.add(Soldier("enemy", pt_x, pt_y, scale, 2, 20))
                elif tile == 17:  # ammo box
                    item_box_group.add(ItemBox("Ammo", pt_x, pt_y))
                elif tile == 18:  # Grenade box
                    item_box_group.add(ItemBox("Grenade", pt_x, pt_y))
                elif tile == 19:  # Health box
                    item_box_group.add(ItemBox("Health", pt_x, pt_y))
                elif tile == 20:  # exit
                    Exit(tile_img, decoration_group, topleft=tile_rect.topleft)

        return player

    def draw(self):
        for obs in self.obstacle_list:
            screen.blit(obs[0], obs[1])


class Decorations(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, *groups, **position):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(**position)


class Water(Decorations):
    def __init__(self, image, *groups, **position):
        super().__init__(image, *groups, **position)


class Exit(Decorations):
    def __init__(self, image, *groups, **position):
        super().__init__(image, *groups, **position)


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

        # collision with obstacle tiles
        for tile in world.obstacle_list:
            # collision in horizontal direction
            if tile[1].colliderect(self.rect):
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
        dx = self.direction * self.speed
        dy = self.vel_y

        # check collision with ground
        width = self.image.get_width()
        height = self.image.get_height()
        for tile in world.obstacle_list:
            # collision in horizontal direction
            if tile[1].colliderect(dx + self.rect.x, self.rect.y, width, height):
                self.direction *= -1
                dx = self.direction * self.speed
            # collision in vertical direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, width, height):
                self.speed = 0
                # if throwing - means below tile
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:  # falling - above ground
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

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
decoration_group = pygame.sprite.Group()


ammo_ui = AmmoUI()

# Load level
world_data = []
with open(f"src/assets/level{level}_data.csv", mode="r", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    prev = reader.line_num
    # copy all rows list
    for row in reader:
        world_data.append(row)
    # conver string data into int
    world_data = [[int(c) for c in r] for r in world_data]
world = World()
player = world.process_data(world_data)
if player == None:
    raise Exception("There is no player object present in map data.")

run = True
while run:
    clock.tick(45)

    draw_bg()
    world.draw()
    decoration_group.draw(screen)
    player.update()
    player.draw()

    enemy_group.update()
    for enemy in enemy_group:
        enemy.bot_movement()
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
