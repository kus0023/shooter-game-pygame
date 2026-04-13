import pygame
from constants import TILE_SIZE
from assets import tile_img_list
from decorations import Water, Exit, Decorations
from soldier import Soldier  # this line needs to be changed
from item_box import ItemBox
import sprite_group as groups


class World:
    def __init__(self):
        # Tuple of (tile_image, tile_rect)
        self.obstacle_list: list[tuple[pygame.Surface, pygame.Rect]] = []

    def process_data(self, world_data):
        self.level_length = len(world_data[0])
        # iterating through all the top left point of tile

        p = None
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
                    Water(
                        tile_img,
                        [groups.decoration_group, groups.water_group],
                        topleft=tile_rect.topleft,
                    )
                elif tile >= 11 and tile <= 14:  # stone, box, grass decoration
                    Decorations(
                        tile_img, groups.decoration_group, topleft=tile_rect.topleft
                    )
                elif tile == 15:  # player
                    p = Soldier("player", pt_x, pt_y, scale, 5, 20)
                elif tile == 16:  # enemy
                    groups.enemy_group.add(Soldier("enemy", pt_x, pt_y, scale, 2, 20))
                elif tile == 17:  # ammo box
                    groups.item_box_group.add(ItemBox("Ammo", pt_x, pt_y))
                elif tile == 18:  # Grenade box
                    groups.item_box_group.add(ItemBox("Grenade", pt_x, pt_y))
                elif tile == 19:  # Health box
                    groups.item_box_group.add(ItemBox("Health", pt_x, pt_y))
                elif tile == 20:  # exit
                    Exit(
                        tile_img,
                        [groups.decoration_group, groups.exit_group],
                        topleft=tile_rect.topleft,
                    )

        return p

    def draw(self, screen, screen_scroll):
        for obs in self.obstacle_list:
            obs[1].x += screen_scroll
            screen.blit(obs[0], obs[1])
