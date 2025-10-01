import pygame
from collections import deque
import random

pygame.init()

WIDTH, HEIGHT = 560, 620
TILE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Ghost AI Example")

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 50)

level = [
    "1111111111111111111111111111",
    "1000000000110000000000000001",
    "1011111110110111111111111101",
    "1011111110110111111111111101",
    "1011111110110111111111111101",
    "1000000000000000000000000001",
    "1011110111110111110111110101",
    "1000000100000000000100000001",
    "1111110110111111110101111111",
    "0000010000000900000001000000",
    "1111011110111111101111011111",
    "1000000000110000000000000001",
    "1011111111110111111111111101",
    "1000000000000000000000000001",
    "1111111111111111111111111111"
]

ROWS = len(level)
COLS = len(level[0])

def get_walkable_tiles():
    tiles = []
    for r in range(ROWS):
        for c in range(COLS):
            if level[r][c] != "1":
                tiles.append((c, r))
    return tiles

def init_dots():
    dots = []
    for r in range(ROWS):
        for c in range(COLS):
            if level[r][c] == "0":
                dots.append((c*TILE+TILE//2, r*TILE+TILE//2))
    return dots

def spawn_pacman():
    walkable = get_walkable_tiles()
    c, r = random.choice(walkable)
    return c*TILE+TILE//2, r*TILE+TILE//2

# Ghosts spawn
ghost_colors = [RED, PINK, CYAN, ORANGE]
ghost_names = ["Blinky","Pinky","Inky","Clyde"]
def spawn_ghosts():
    ghosts = []
    positions = [(13,7),(14,7),(13,8),(14,8)]
    for i,pos in enumerate(positions):
        ghosts.append({
            "x": pos[0]*TILE,
            "y": pos[1]*TILE,
            "color": ghost_colors[i],
            "speed": 2,
            "name": ghost_names[i]
        })
    return ghosts

def draw_board(pacman_x, pacman_y, ghosts, dots):
    screen.fill(BLACK)
    for r in range(ROWS):
        for c in range(COLS):
            if level[r][c] == "1":
                pygame.draw.rect(screen, BLUE, (c*TILE, r*TILE, TILE, TILE))
    for dot in dots:
        pygame.draw.circle(screen, WHITE, dot, 3)
    pygame.draw.ellipse(screen, YELLOW, (pacman_x-TILE//2, pacman_y-TILE//2, TILE, TILE))
    for g in ghosts:
        pygame.draw.circle(screen, g["color"], (g["x"], g["y"]), TILE//2-2)

def can_move_grid(r, c, ignore_tunnel=False):
    if r < 0 or r >= ROWS: return False
    if c < 0 or c >= COLS:
        return ignore_tunnel
    return level[r][c] != "1"

def bfs(start, goal, ignore_tunnel=False):
    sr, sc = start
    gr, gc = goal
    queue = deque([(sr, sc)])
    visited = {(sr, sc): None}
    while queue:
        r, c = queue.popleft()
        if (r, c) == (gr, gc): break
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r+dr, c+dc
            if can_move_grid(nr, nc, ignore_tunnel) and (nr,nc) not in visited:
                visited[(nr,nc)] = (r,c)
                queue.append((nr,nc))
    path = []
    node = (gr,gc)
    while node and node in visited:
        path.append(node)
        node = visited[node]
    path.reverse()
    if len(path)>1:
        return path[1]
    return (sr, sc)

def game_over_screen():
    screen.fill(BLACK)
    text = font.render("Game Over", True, RED)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 60))
    button_rect = pygame.Rect(WIDTH//2 - 80, HEIGHT//2, 160, 50)
    pygame.draw.rect(screen, GRAY, button_rect)
    btn_text = font.render("Play Again", True, WHITE)
    screen.blit(btn_text, (WIDTH//2 - btn_text.get_width()//2, HEIGHT//2+5))
    pygame.display.flip()
    return button_rect

def main():
    pacman_x, pacman_y = spawn_pacman()
    pacman_speed = 4
    direction = [0,0]
    dots = init_dots()
    ghosts = spawn_ghosts()
    running = True
    game_over = False

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if game_over:
            button_rect = game_over_screen()
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            if click[0] and button_rect.collidepoint(mouse):
                main()
                return
            continue

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: direction = [-pacman_speed,0]
        if keys[pygame.K_RIGHT]: direction = [pacman_speed,0]
        if keys[pygame.K_UP]: direction = [0,-pacman_speed]
        if keys[pygame.K_DOWN]: direction = [0,pacman_speed]

        # Move Pac-Man
        new_x = pacman_x + direction[0]
        new_y = pacman_y + direction[1]

        # Tunnel wrap around
        if new_x < 0: pacman_x = WIDTH - TILE//2
        elif new_x > WIDTH: pacman_x = TILE//2
        elif can_move_grid(new_y//TILE, new_x//TILE, ignore_tunnel=True):
            pacman_x, pacman_y = new_x, new_y

        for dot in dots[:]:
            if (pacman_x-dot[0])**2 + (pacman_y-dot[1])**2 < 10**2:
                dots.remove(dot)

        pacman_cell = (pacman_y//TILE, pacman_x//TILE)

        for g in ghosts:
            ghost_cell = (g["y"]//TILE, g["x"]//TILE)

            # Different ghost algorithms
            if g["name"] == "Blinky":  # Direct chase
                target_cell = pacman_cell
            elif g["name"] == "Pinky":  # 4 tiles ahead of Pac-Man
                dir_r = direction[1]//TILE if direction[1]!=0 else 0
                dir_c = direction[0]//TILE if direction[0]!=0 else 0
                target_cell = (pacman_cell[0]+4*dir_r, pacman_cell[1]+4*dir_c)
            elif g["name"] == "Inky":  # midpoint between Pac-Man and Blinky
                blinky = next(x for x in ghosts if x["name"]=="Blinky")
                blinky_cell = (blinky["y"]//TILE, blinky["x"]//TILE)
                target_cell = ((pacman_cell[0]+blinky_cell[0])//2, (pacman_cell[1]+blinky_cell[1])//2)
            elif g["name"] == "Clyde":  # Scatter if close, chase if far
                dist = abs(pacman_cell[0]-ghost_cell[0]) + abs(pacman_cell[1]-ghost_cell[1])
                if dist < 5:  # scatter corner
                    target_cell = (ROWS-2, 1)
                else:
                    target_cell = pacman_cell
            else:
                target_cell = pacman_cell

            next_cell = bfs(ghost_cell, target_cell)
            gx, gy = g["x"], g["y"]
            nx, ny = next_cell[1]*TILE, next_cell[0]*TILE
            if gx < nx: g["x"] += g["speed"]
            elif gx > nx: g["x"] -= g["speed"]
            if gy < ny: g["y"] += g["speed"]
            elif gy > ny: g["y"] -= g["speed"]

            if (pacman_x - g["x"])**2 + (pacman_y - g["y"])**2 < 20**2:
                game_over = True

        draw_board(pacman_x, pacman_y, ghosts, dots)
        pygame.display.flip()

main()
pygame.quit()
