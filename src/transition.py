import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from enum import Enum


class ScreenFadeType(Enum):
    TOP_TO_DOWN_CLOSE = 1
    MIDDLE_SQUARE_OPEN = 2


class ScreenFade:

    def __init__(self, type: ScreenFadeType, color, speed):
        self.type = type
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self, screen):
        fade_completed = False
        self.fade_counter += self.speed

        if self.type == ScreenFadeType.TOP_TO_DOWN_CLOSE:
            pygame.draw.rect(
                screen, self.color, (0, 0, SCREEN_WIDTH, self.fade_counter)
            )
            if self.fade_counter > SCREEN_HEIGHT:
                fade_completed = True
                self.fade_counter = SCREEN_HEIGHT

        if self.type == ScreenFadeType.MIDDLE_SQUARE_OPEN:
            pygame.draw.rect(
                screen,
                self.color,
                (-self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT),
            )
            pygame.draw.rect(
                screen,
                self.color,
                (
                    (SCREEN_WIDTH // 2) + self.fade_counter,
                    0,
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT,
                ),
            )
            pygame.draw.rect(
                screen,
                self.color,
                (0, -self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2),
            )
            pygame.draw.rect(
                screen,
                self.color,
                (
                    0,
                    (SCREEN_HEIGHT // 2) + self.fade_counter,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT // 2,
                ),
            )

            if self.fade_counter > SCREEN_WIDTH:
                fade_completed = True
                self.fade_counter = 0

        return fade_completed
