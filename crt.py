"""
CRT Effects Engine
"""

import random
import pygame

import config


# --------------------------------------------------------
# Glow
# --------------------------------------------------------

def draw_glow(trace_surface, glow_surface):
    """
    Fast glow using multi-scale additive blending.
    Much faster than a Gaussian blur on the Pi.
    """

    # Small blur
    small = pygame.transform.smoothscale(
        trace_surface,
        (
            config.WIDTH // 2,
            config.HEIGHT // 2,
        ),
    )

    small = pygame.transform.smoothscale(
        small,
        (
            config.WIDTH,
            config.HEIGHT,
        ),
    )

    small.set_alpha(70)

    glow_surface.blit(
        small,
        (0, 0),
        special_flags=pygame.BLEND_ADD,
    )

    # Large blur

    tiny = pygame.transform.smoothscale(
        trace_surface,
        (
            config.WIDTH // 4,
            config.HEIGHT // 4,
        ),
    )

    tiny = pygame.transform.smoothscale(
        tiny,
        (
            config.WIDTH,
            config.HEIGHT,
        ),
    )

    tiny.set_alpha(35)

    glow_surface.blit(
        tiny,
        (0, 0),
        special_flags=pygame.BLEND_ADD,
    )


# --------------------------------------------------------
# Scanlines
# --------------------------------------------------------

def draw_scanlines(surface):

    color = (0, 0, 0)

    for y in range(0, config.HEIGHT, 2):

        pygame.draw.line(
            surface,
            color,
            (0, y),
            (config.WIDTH, y),
        )

    surface.set_alpha(config.SCANLINE_ALPHA)


# --------------------------------------------------------
# Noise
# --------------------------------------------------------

def draw_noise(surface):

    for _ in range(config.NOISE_PIXELS):

        x = random.randrange(config.WIDTH)

        y = random.randrange(config.HEIGHT)

        brightness = random.randint(10, 40)

        surface.set_at(
            (x, y),
            (
                0,
                brightness,
                0,
                20,
            ),
        )


# --------------------------------------------------------
# Vignette
# --------------------------------------------------------

def draw_vignette(surface):

    w = config.WIDTH
    h = config.HEIGHT

    steps = 14

    for i in range(steps):

        alpha = int(i * 5)

        rect = pygame.Rect(
            i * 8,
            i * 5,
            w - i * 16,
            h - i * 10,
        )

        overlay = pygame.Surface(
            rect.size,
            pygame.SRCALPHA,
        )

        overlay.fill((0, 0, 0, alpha))

        surface.blit(
            overlay,
            rect.topleft,
            special_flags=pygame.BLEND_RGBA_SUB,
        )


# --------------------------------------------------------
# Boot flash (future)
# --------------------------------------------------------

def boot_flash(surface, strength):

    overlay = pygame.Surface(
        (
            config.WIDTH,
            config.HEIGHT,
        )
    )

    overlay.fill(
        (
            strength,
            strength,
            strength,
        )
    )

    surface.blit(
        overlay,
        (0, 0),
        special_flags=pygame.BLEND_ADD,
    )
