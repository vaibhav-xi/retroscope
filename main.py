import sys
import pygame

WIDTH = 800
HEIGHT = 480

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("RetroScope")

clock = pygame.time.Clock()

background = (6, 12, 6)
green = (0, 255, 90)

font = pygame.font.SysFont("monospace", 42, bold=True)

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    screen.fill(background)

    text = font.render("RETROSCOPE v0.1", True, green)

    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    screen.blit(text, rect)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()
