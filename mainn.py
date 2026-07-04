import pygame
import time
import random

# Initialize Pygame
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

# Fonts - Using default, but sized for a "terminal" look
header_font = pygame.font.SysFont("couriernew", 32, bold=True)
data_font = pygame.font.SysFont("couriernew", 24)
clock = pygame.time.Clock()

# Colors
GREEN = (50, 255, 50)
DARK_GREEN = (0, 60, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Timing
TOTAL_DURATION = random.randint(80, 90) * 60
START_TIME = time.time()

def draw_grid():
    for x in range(0, WIDTH, 50):
        pygame.draw.line(screen, DARK_GREEN, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(screen, DARK_GREEN, (0, y), (WIDTH, y))

running = True
while running:
    current_time = time.time()
    elapsed = min(current_time - START_TIME, TOTAL_DURATION)
    progress = elapsed / TOTAL_DURATION
    remaining_seconds = TOTAL_DURATION - elapsed
    
    # Speed fluctuates slightly
    current_speed = max(0.1, 1.2 + random.uniform(-0.5, 0.5))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    screen.fill(BLACK)
    draw_grid()

    # Draw Popup Box
    box_w, box_h = 650, 220
    box_rect = pygame.Rect((WIDTH - box_w) // 2, (HEIGHT - box_h) // 2, box_w, box_h)
    pygame.draw.rect(screen, BLACK, box_rect)
    pygame.draw.rect(screen, GREEN, box_rect, 3)

    # Headers
    title = header_font.render("RETROSCOPE FW UPDATE: v4", True, GREEN)
    status = data_font.render("STATUS: DOWNLOADING...", True, GREEN)
    screen.blit(title, (box_rect.x + 20, box_rect.y + 20))
    screen.blit(status, (box_rect.x + 20, box_rect.y + 60))

    # Progress Bar
    bar_w = 600
    bar_x = box_rect.x + 25
    bar_y = box_rect.y + 110
    pygame.draw.rect(screen, DARK_GREEN, (bar_x, bar_y, bar_w, 20))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w * progress, 20))

    # Bottom Data
    speed_text = data_font.render(f"TX RATE: {current_speed:.2f} MB/s", True, GREEN)
    time_text = data_font.render(f"ETA: {int(remaining_seconds // 60)}:{int(remaining_seconds % 60):02d}", True, GREEN)
    
    screen.blit(speed_text, (bar_x, bar_y + 40))
    screen.blit(time_text, (bar_x + 400, bar_y + 40))

    pygame.display.flip()
    clock.tick(8) # Slight delay makes the fluctuating speed feel more like real-time data

pygame.quit()