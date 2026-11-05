import sys, random, math
import pygame

# ---------- constants ----------
SCREEN_W, SCREEN_H = 800, 600
FPS = 60
GRAVITY = 0.6
PLAYER_SPEED = 5
JUMP_POWER = -12
TILE = 40

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 60, 60)
GREEN = (80, 220, 100)
BLUE = (80, 140, 255)
PURPLE = (180, 80, 255)
YELLOW = (255, 240, 80)
ORANGE = (255, 160, 50)
CYAN = (0, 220, 220)

# ---------- player ----------
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 28, 36)
        self.vx = 0
        self.vy = 0
        self.gravity_dir = 1
        self.grounded = False
        self.alive = True
        self.coins = 0
        self.facing = 1
        self.star_timer = 0

    def update(self, platforms, moving_platforms):
        if not self.alive:
            return
        self.rect.x += self.vx
        all_plat = platforms + [p.rect for p in moving_platforms]
        for p in all_plat:
            if self.rect.colliderect(p):
                if self.vx > 0:
                    self.rect.right = p.left
                elif self.vx < 0:
                    self.rect.left = p.right

        self.vy += GRAVITY * self.gravity_dir
        self.rect.y += self.vy
        self.grounded = False
        for p in all_plat:
            if self.rect.colliderect(p):
                if self.gravity_dir > 0 and self.vy > 0:
                    self.rect.bottom = p.top
                    self.vy = 0
                    self.grounded = True
                elif self.gravity_dir < 0 and self.vy < 0:
                    self.rect.top = p.bottom
                    self.vy = 0
                    self.grounded = True

        for mp in moving_platforms:
            if self.rect.colliderect(mp.rect):
                if self.gravity_dir > 0 and self.vy >= 0:
                    self.rect.bottom = mp.rect.top
                    self.vy = 0
                    self.grounded = True
                    self.rect.x += mp.vx
                elif self.gravity_dir < 0 and self.vy <= 0:
                    self.rect.top = mp.rect.bottom
                    self.vy = 0
                    self.grounded = True
                    self.rect.x += mp.vx

        if self.rect.top > 900 or self.rect.bottom < -300:
            self.alive = False
        if self.star_timer > 0:
            self.star_timer -= 1

    def jump(self):
        if self.alive and self.grounded:
            self.vy = JUMP_POWER * self.gravity_dir
            self.grounded = False

    def flip(self):
        if not self.alive:
            return
        self.gravity_dir *= -1
        self.vy = 0

    def draw(self, screen, flip_anim, flash):
        if flip_anim > 0 and flip_anim % 2 == 0:
            self.gravity_dir *= -1
            self.vy = 0
        x, y = self.rect.x, self.rect.y
        w, h = self.rect.w, self.rect.h
        if self.star_timer > 0:
            body_color = [YELLOW, ORANGE, PURPLE][(self.star_timer // 6) % 3]
        else:
            body_color = RED
        pygame.draw.rect(screen, BLACK, (x - 2, y - 8, w + 4, h + 10), 2)
        pygame.draw.rect(screen, body_color, (x - 2, y - 6, w + 4, 10))
        pygame.draw.rect(screen, body_color, (x + 2, y - 10, 14, 6))
        pygame.draw.rect(screen, (255, 200, 150), (x + 3, y + 2, w - 6, 14))
        pygame.draw.rect(screen, BLUE, (x, y + 16, w, h - 16))
        eye_x = x + 19 if self.facing > 0 else x + 5
        pygame.draw.circle(screen, BLACK, (eye_x, y + 8), 3)

# ---------- moving platform ----------
class MovingPlatform:
    def __init__(self, rect, axis, dist, speed):
        self.rect = rect
        self.axis = axis  # 'x' or 'y'
        self.dist = dist
        self.speed = speed
        self.start = rect.x if axis == 'x' else rect.y

    def update(self):
        if self.axis == 'x':
            self.rect.x += self.speed
            if self.rect.x > self.start + self.dist or self.rect.x < self.start:
                self.speed *= -1
        else:
            self.rect.y += self.speed
            if self.rect.y > self.start + self.dist or self.rect.y < self.start:
                self.speed *= -1
        self.vx = self.speed if self.axis == 'x' else 0

# ---------- particles ----------
class Particle:
    def __init__(self, x, y, color, spread=3):
        self.x = x
        self.y = y
        self.vx = random.uniform(-spread, spread)
        self.vy = random.uniform(-spread, spread)
        self.life = random.randint(15, 30)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1

    def draw(self, screen):
        if self.life > 0:
            s = max(2, self.life // 6)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), s)

# ---------- level data ----------
def make_levels():
    L = []
    # Level 1: Tutorial
    L.append({
        'name': 'Tutorial',
        'platforms': [pygame.Rect(-200, 560, 1200, 40),
                      pygame.Rect(-200, 40, 600, 40)],
        'moving': [],
        'spikes': [pygame.Rect(500, 520, 40, 40), pygame.Rect(540, 520, 40, 40)],
        'coins': [pygame.Rect(300, 480, 20, 20), pygame.Rect(420, 480, 20, 20),
                  pygame.Rect(640, 480, 20, 20), pygame.Rect(700, 480, 20, 20)],
        'springs': [],
        'stars': [],
        'goal': pygame.Rect(760, 480, 20, 80),
        'player_start': (100, 480),
        'theme': ('down', (60, 120, 220), (200, 230, 255)),
    })
    # Level 2: Moving platforms + springs
    L.append({
        'name': 'Sky Drift',
        'platforms': [pygame.Rect(-200, 560, 500, 40),
                      pygame.Rect(-200, 40, 400, 40),
                      pygame.Rect(500, 560, 120, 40)],
        'moving': [MovingPlatform(pygame.Rect(320, 400, 100, 30), 'x', 200, 2),
                   MovingPlatform(pygame.Rect(600, 320, 100, 30), 'y', 120, 2)],
        'spikes': [pygame.Rect(450, 520, 40, 40), pygame.Rect(490, 520, 40, 40)],
        'coins': [pygame.Rect(350, 370, 20, 20), pygame.Rect(400, 370, 20, 20),
                  pygame.Rect(630, 290, 20, 20), pygame.Rect(580, 290, 20, 20)],
        'springs': [pygame.Rect(200, 520, 30, 40)],
        'stars': [],
        'goal': pygame.Rect(760, 480, 20, 80),
        'player_start': (100, 480),
        'theme': ('up', (120, 30, 60), (255, 150, 80)),
    })
    # Level 3: Challenge
    L.append({
        'name': 'Gauntlet',
        'platforms': [pygame.Rect(-200, 560, 350, 40),
                      pygame.Rect(300, 560, 200, 40),
                      pygame.Rect(600, 560, 300, 40),
                      pygame.Rect(-200, 40, 500, 40)],
        'moving': [MovingPlatform(pygame.Rect(380, 420, 90, 30), 'x', 150, 2)],
        'spikes': [pygame.Rect(280, 520, 40, 40), pygame.Rect(320, 520, 40, 40),
                   pygame.Rect(550, 520, 40, 40), pygame.Rect(590, 520, 40, 40)],
        'coins': [pygame.Rect(400, 390, 20, 20), pygame.Rect(440, 390, 20, 20),
                  pygame.Rect(680, 480, 20, 20)],
        'springs': [pygame.Rect(120, 520, 30, 40)],
        'stars': [pygame.Rect(500, 440, 20, 20)],
        'goal': pygame.Rect(760, 480, 20, 80),
        'player_start': (100, 480),
        'theme': ('down', (20, 60, 120), (120, 180, 240)),
    })
    return L

# ---------- main ----------
def run_game(test_mode=False):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption('Gravity Flip')
    clock = pygame.time.Clock()

    levels = make_levels()
    current_level = 0
    level = levels[0]
    player = Player(*level['player_start'])
    particles = []
    flip_anim = 0
    flash = 0
    running = True
    frames = 0

    def load_level(idx):
        nonlocal level, player
        level = levels[idx]
        player = Player(*level['player_start'])

    while running:
        clock.tick(FPS)
        frames += 1
        if test_mode and frames > 300:
            print('TEST_PASS')
            pygame.quit()
            sys.exit(0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.flip()
                    flip_anim = 12
                    flash = 8
                    for _ in range(20):
                        particles.append(Particle(player.rect.centerx, player.rect.centery, CYAN, 5))
                elif event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        player.vx = 0
        if keys[pygame.K_LEFT]:
            player.vx = -PLAYER_SPEED
            player.facing = -1
        if keys[pygame.K_RIGHT]:
            player.vx = PLAYER_SPEED
            player.facing = 1
        if keys[pygame.K_UP]:
            player.jump()

        player.update(level['platforms'], level['moving'])
        for mp in level['moving']:
            mp.update()

        for s in level['spikes']:
            if player.rect.colliderect(s):
                player.alive = False

        for sp in level['springs']:
            if player.rect.colliderect(sp):
                player.vy = -18 * player.gravity_dir
                player.grounded = False
                for _ in range(12):
                    particles.append(Particle(sp.centerx, sp.centery, ORANGE, 4))

        for st in level['stars'][:]:
            if player.rect.colliderect(st):
                level['stars'].remove(st)
                player.star_timer = 300
                for _ in range(25):
                    particles.append(Particle(st.centerx, st.centery, YELLOW, 6))

        for c in level['coins'][:]:
            if player.rect.colliderect(c):
                level['coins'].remove(c)
                player.coins += 1
                for _ in range(8):
                    particles.append(Particle(c.centerx, c.centery, YELLOW))

        if player.rect.colliderect(level['goal']):
            if current_level < len(levels) - 1:
                current_level += 1
                load_level(current_level)
                flash = 15
            else:
                print('ALL_LEVELS_COMPLETE')
                running = False

        if not player.alive:
            player = Player(*level['player_start'])
            player.lives = getattr(player, 'lives', 3) - 1
            if not hasattr(player, 'lives'):
                player.lives = 3

        if flip_anim > 0:
            flip_anim -= 1
        if flash > 0:
            flash -= 1
        particles = [p for p in particles if p.life > 0]
        for p in particles:
            p.update()

        # ---- draw ----
        theme_label, top_c, bot_c = level['theme']
        if player.gravity_dir > 0:
            bg_top, bg_bottom = top_c, bot_c
            floor_color, ceiling_color = GREEN, BLUE
        else:
            bg_top, bg_bottom = bot_c, top_c
            floor_color, ceiling_color = BLUE, GREEN

        for y in range(SCREEN_H):
            t = y / SCREEN_H
            col = tuple(int(bg_top[i] + (bg_bottom[i] - bg_top[i]) * t) for i in range(3))
            pygame.draw.line(screen, col, (0, y), (SCREEN_W, y))

        for p in level['platforms']:
            if p.y < 100:
                pygame.draw.rect(screen, ceiling_color, p)
                pygame.draw.rect(screen, (0, 40, 100), (p.x, p.y, p.w, 8))
            else:
                pygame.draw.rect(screen, floor_color, p)
                pygame.draw.rect(screen, (0, 80, 30), (p.x, p.y, p.w, 8))

        for mp in level['moving']:
            pygame.draw.rect(screen, PURPLE, mp.rect)
            pygame.draw.rect(screen, (100, 40, 160), (mp.rect.x, mp.rect.y, mp.rect.w, 6))

        for s in level['spikes']:
            if player.gravity_dir > 0:
                pts = [(s.x, s.bottom), (s.centerx, s.top), (s.right, s.bottom)]
            else:
                pts = [(s.x, s.top), (s.centerx, s.bottom), (s.right, s.top)]
            pygame.draw.polygon(screen, RED, pts)

        for sp in level['springs']:
            pygame.draw.rect(screen, ORANGE, sp)
            pygame.draw.rect(screen, YELLOW, (sp.x + 4, sp.y + sp.h - 16, sp.w - 8, 12))

        for st in level['stars']:
            cx, cy = st.center
            pts = []
            for i in range(10):
                ang = math.pi * i / 5 - math.pi / 2
                r = 12 if i % 2 == 0 else 6
                pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
            pygame.draw.polygon(screen, YELLOW, pts)

        for c in level['coins']:
            pygame.draw.circle(screen, YELLOW, c.center, 10)
            pygame.draw.circle(screen, (255, 250, 180), c.center, 6)

        pygame.draw.rect(screen, RED, level['goal'])
        player.draw(screen, flip_anim, flash)
        for p in particles:
            p.draw(screen)

        if flash > 0 and flash % 4 == 0:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 80))
            screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 32)
        grav_text = font.render(f'Level {current_level+1}/3 — Gravity: {"DOWN" if player.gravity_dir > 0 else "UP"}', True, WHITE)
        screen.blit(grav_text, (10, 10))
        hint = font.render('SPACE = flip gravity | Arrows = move | UP = jump', True, WHITE)
        screen.blit(hint, (10, 50))
        coin_text = font.render(f'Coins: {player.coins}', True, WHITE)
        screen.blit(coin_text, (10, 90))

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    test_mode = '--test' in sys.argv
    run_game(test_mode)
