import sys, random, math
import pygame
import sounds
import graphics

SCREEN_W, SCREEN_H = 900, 650
FPS = 60
GRAVITY = 0.5
SPEED = 5.0
JUMP = -11
TILE = 40

WHITE = (255,255,255); BLACK = (0,0,0)
RED = (230,60,60); GREEN = (70,200,90); BLUE = (70,130,255)
PURPLE = (170,70,255); YELLOW = (255,225,70); ORANGE = (255,150,50)
CYAN = (0,210,210); GRAY = (110,110,110)
ICE_BLUE = (180,220,255); LAVA_RED = (255,80,30)
DARK_GRAY = (60,60,70)

class Player:
    def __init__(self, x, y, lives=3):
        self.rect = pygame.Rect(x, y, 30, 40)
        self.vx = 0; self.vy = 0
        self.gdir = 1       # 1 = down, -1 = up
        self.grounded = False
        self.alive = True
        self.coins = 0
        self.lives = lives
        self.facing = 1
        self.star = 0
        self.shield = False
        self.jumps_left = 1
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.portal_cooldown = 0
        self.spring_cooldown = 0

    def update(self, rects, movs):
        if not self.alive:
            return
        dash_vx = 0
        dashing = self.dash_timer > 0
        if dashing:
            self.dash_timer -= 1
            dash_vx = self.facing * 14
            self.rect.x += dash_vx
        else:
            self.rect.x += self.vx
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        effective_vx = dash_vx if dashing else self.vx
        for r in rects + [m.rect for m in movs]:
            if self.rect.colliderect(r):
                if effective_vx > 0:
                    self.rect.right = r.left
                    if dashing: self.dash_timer = 0
                elif effective_vx < 0:
                    self.rect.left = r.right
                    if dashing: self.dash_timer = 0

        self.vy += GRAVITY * self.gdir
        self.rect.y += self.vy
        self.grounded = False
        for r in rects + [m.rect for m in movs]:
            if self.rect.colliderect(r):
                if self.gdir > 0 and self.vy > 0:
                    self.rect.bottom = r.top; self.vy = 0; self.grounded = True
                elif self.gdir < 0 and self.vy < 0:
                    self.rect.top = r.bottom; self.vy = 0; self.grounded = True

        for m in movs:
            if self.rect.colliderect(m.rect):
                if self.gdir > 0 and self.vy >= 0:
                    self.rect.bottom = m.rect.top; self.vy = 0; self.grounded = True
                    self.rect.x += m.dx
                    self.rect.y += m.dy
                elif self.gdir < 0 and self.vy <= 0:
                    self.rect.top = m.rect.bottom; self.vy = 0; self.grounded = True
                    self.rect.x += m.dx
                    self.rect.y += m.dy

        if self.rect.top > 1100 or self.rect.bottom < -500:
            self.alive = False
        if self.star > 0:
            self.star -= 1

    def jump(self):
        if not self.alive:
            return
        if self.grounded:
            self.vy = JUMP * self.gdir
            self.grounded = False
            self.jumps_left = 1
        elif self.jumps_left > 0:
            self.vy = JUMP * 0.85 * self.gdir
            self.jumps_left -= 1

    def dash(self):
        if self.dash_cooldown > 0 or not self.alive:
            return False
        self.dash_timer = 12
        self.dash_cooldown = 45
        return True

    def flip(self):
        if not self.alive:
            return
        self.gdir *= -1
        self.vy = 0
        self.jumps_left = 1

    def draw(self, screen, cam, time=0):
        graphics.draw_player(screen, self, cam, time)

class FlyEnemy:
    def __init__(self, x, y, amp=60, speed=1.5, vertical=False):
        self.rect = pygame.Rect(x, y, 34, 30)
        self.start_x = x; self.start_y = y
        self.amp = amp; self.speed = speed; self.vertical = vertical
        self.t = random.uniform(0, 6.28)
        self.alive = True
    def update(self):
        self.t += self.speed / 30
        if self.vertical:
            self.rect.y = self.start_y + math.sin(self.t) * self.amp
        else:
            self.rect.x = self.start_x + math.sin(self.t) * self.amp
    def draw(self, screen, cam, time=0):
        graphics.draw_fly_enemy(screen, self, cam, time)

class Saw:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 44, 44)
        self.ang = 0
    def update(self):
        self.ang += 6
    def draw(self, screen, cam, time=0):
        graphics.draw_saw(screen, self, cam, time)

class MovingPlatform:
    def __init__(self, r, axis, dist, speed):
        self.rect = r; self.axis = axis; self.dist = dist; self.speed = speed
        self.start = r.x if axis == 'x' else r.y
        self.vx = speed if axis == 'x' else 0
        self.vy = speed if axis == 'y' else 0
        self.dx = 0
        self.dy = 0
    def update(self):
        self.dx = 0; self.dy = 0
        if self.axis == 'x':
            self.rect.x += self.speed; self.vx = self.speed; self.dx = self.speed
            if self.rect.x > self.start + self.dist or self.rect.x < self.start:
                self.speed *= -1
        else:
            self.rect.y += self.speed; self.vx = 0; self.vy = self.speed; self.dy = self.speed
            if self.rect.y > self.start + self.dist or self.rect.y < self.start:
                self.speed *= -1


class PortalFlip:
    def __init__(self, x, y, w=40, h=90):
        self.rect = pygame.Rect(x, y, w, h)
        self.pulse = 0
    def update(self):
        self.pulse += 1
    def draw(self, screen, cam, time=0):
        graphics.draw_portal(screen, self, cam, time)

class PhasePlatform:
    def __init__(self, rect, on_time=90, off_time=60):
        self.rect = rect
        self.on_time = on_time
        self.off_time = off_time
        self.timer = 0
        self.state = True
    def update(self):
        if self.state:
            self.timer += 1
            if self.timer >= self.on_time:
                self.state = False; self.timer = 0
        else:
            self.timer += 1
            if self.timer >= self.off_time:
                self.state = True; self.timer = 0
    def draw(self, screen, cam, time=0):
        graphics.draw_phase_platform(screen, self, cam, time)


class Shield:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.pulse = 0
    def update(self):
        self.pulse += 1
    def draw(self, screen, cam, time=0):
        graphics.draw_shield_pickup(screen, self, cam, time)

class Boss:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x, y, 90, 90)
        self.hp = 10
        self.max_hp = 10
        self.vx = 2
        self.vy = 0
        self.t = 0
        self.attack_timer = 0
        self.alive = True
        self.hit_flash = 0
        self.shots = []
        self.min_x = 200
        self.max_x = 1100
    def update(self, platforms, player):
        if not self.alive:
            return
        self.t += 1
        if player.alive:
            dx = player.rect.centerx - self.rect.centerx
            if abs(dx) > 30:
                self.rect.x += self.vx if dx > 0 else -self.vx
        # keep boss in arena
        if self.rect.left < self.min_x:
            self.rect.left = self.min_x
        if self.rect.right > self.max_x:
            self.rect.right = self.max_x
        # horizontal collision with platforms (push out if overlapping)
        for r in platforms:
            if self.rect.colliderect(r):
                if self.rect.centerx < r.centerx:
                    self.rect.right = r.left
                else:
                    self.rect.left = r.right
        # vertical collision
        self.vy += GRAVITY
        self.rect.y += self.vy
        for r in platforms:
            if self.rect.colliderect(r):
                if self.vy > 0:
                    self.rect.bottom = r.top; self.vy = 0
                elif self.vy < 0:
                    self.rect.top = r.bottom; self.vy = 0
        self.attack_timer -= 1
        if self.attack_timer <= 0 and player.alive:
            self.attack_timer = 90
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            d = math.hypot(dx, dy) or 1
            # spawn shot just outside boss body to avoid self-collision
            spawn_x = self.rect.centerx + (1 if dx > 0 else -1) * 50
            spawn_y = self.rect.centery
            self.shots.append([spawn_x, spawn_y, dx/d*4, dy/d*4])
        for s in self.shots[:]:
            s[0] += s[2]; s[1] += s[3]
            # remove if off-screen OR hits a platform
            shot_rect = pygame.Rect(int(s[0]) - 8, int(s[1]) - 8, 16, 16)
            hit_platform = any(shot_rect.colliderect(r) for r in platforms)
            if hit_platform or s[0] < -100 or s[0] > 2000 or s[1] < -100 or s[1] > 1200:
                self.shots.remove(s)
        if self.hit_flash > 0:
            self.hit_flash -= 1
    def hit(self):
        self.hp -= 1
        self.hit_flash = 10
        if self.hp <= 0:
            self.alive = False
            return True
        return False
    def draw(self, screen, cam, time=0):
        graphics.draw_boss(screen, self, cam, time)

class Particle:
    def __init__(self, x, y, color, spread=3, gdir=1):
        self.x = x; self.y = y
        self.vx = random.uniform(-spread, spread)
        self.vy = random.uniform(-spread, spread)
        self.life = random.randint(12, 28); self.color = color
        self.gdir = gdir
    def update(self):
        self.x += self.vx; self.y += self.vy; self.vy += 0.08 * self.gdir; self.life -= 1
    def draw(self, screen, cam=0):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x - cam), int(self.y)), max(2, self.life // 6))

def make_levels():
    L = []
    L.append({
        'name': 'Learning Ground',
        'platforms': [pygame.Rect(-300,580,1500,40), pygame.Rect(-300,30,1500,40)],
        'moving': [], 'enemies': [], 'saws': [],
        'spikes': [pygame.Rect(500,540,40,40), pygame.Rect(540,540,40,40),
                  pygame.Rect(500,30,40,40), pygame.Rect(540,30,40,40)],
        'springs': [], 'stars': [],
        'coins': [pygame.Rect(280,500,20,20), pygame.Rect(400,500,20,20), pygame.Rect(700,500,20,20)],
        'goal': pygame.Rect(1160,30,24,550),
        'start': (100,500), 'theme': (70,120,220,200,230,255),
    })
    L.append({
        'name': 'Sky Dance',
        'platforms': [pygame.Rect(-300,580,1500,40), pygame.Rect(-300,30,1500,40)],
        'moving': [MovingPlatform(pygame.Rect(280,440,100,30),'x',180,2),
                  MovingPlatform(pygame.Rect(650,330,100,30),'y',130,2.2)],
        'enemies': [FlyEnemy(400,480,50,1.6), FlyEnemy(700,420,45,1.4,True)],
        'saws': [Saw(800,460)],
        'spikes': [], 'springs': [pygame.Rect(180,540,30,40)],
        'stars': [],
        'coins': [pygame.Rect(330,400,20,20), pygame.Rect(370,400,20,20),
                  pygame.Rect(690,290,20,20)],
        'goal': pygame.Rect(1160,30,24,550),
        'start': (100,500), 'theme': (120,30,60,255,150,80),
    })
    L.append({
        'name': 'Blade Gauntlet',
        'platforms': [pygame.Rect(-300,580,1500,40), pygame.Rect(-300,30,1500,40)],
        'moving': [MovingPlatform(pygame.Rect(400,430,90,30),'x',160,2.2)],
        'enemies': [FlyEnemy(200,470,40,1.7), FlyEnemy(500,480,55,1.5), FlyEnemy(780,430,40,1.6,True)],
        'saws': [Saw(580,460)],
        'spikes': [pygame.Rect(120,540,40,40), pygame.Rect(160,540,40,40),
                  pygame.Rect(120,30,40,40), pygame.Rect(160,30,40,40)],
        'springs': [pygame.Rect(70,540,30,40)],
        'stars': [pygame.Rect(720,450,20,20)],
        'coins': [pygame.Rect(430,390,20,20), pygame.Rect(470,390,20,20)],
        'goal': pygame.Rect(1160,30,24,550),
        'start': (80,500), 'theme': (20,40,90,100,170,230),
    })
    L.append({
        'name': 'Gravity Sanctum',
        'platforms': [pygame.Rect(-300,580,1500,40), pygame.Rect(-300,30,1500,40)],
        'moving': [], 'enemies': [FlyEnemy(350,470,45,1.7), FlyEnemy(570,480,50,1.5), FlyEnemy(780,440,40,1.8,True)],
        'saws': [Saw(430,460), Saw(700,460)],
        'spikes': [pygame.Rect(200,540,40,40), pygame.Rect(240,540,40,40),
                   pygame.Rect(620,540,40,40), pygame.Rect(660,540,40,40),
                   pygame.Rect(200,30,40,40), pygame.Rect(240,30,40,40),
                   pygame.Rect(620,30,40,40), pygame.Rect(660,30,40,40)],
        'springs': [pygame.Rect(100,540,30,40)],
        'stars': [pygame.Rect(320,450,20,20)],
        'coins': [pygame.Rect(480,500,20,20), pygame.Rect(520,500,20,20), pygame.Rect(560,500,20,20)],
        'goal': pygame.Rect(1160,30,24,550),
        'start': (60,500), 'theme': (40,10,50,180,60,160),
    })
    # Level 5: Phase Factory
    L.append({
        'name': 'Phase Factory',
        'platforms': [pygame.Rect(-300,580,1500,40), pygame.Rect(-300,30,1500,40)],
        'moving': [],
        'enemies': [FlyEnemy(300,470,50,1.7), FlyEnemy(650,490,45,1.5), FlyEnemy(850,420,40,1.8,True)],
        'saws': [Saw(500,460)],
        'spikes': [pygame.Rect(150,540,40,40), pygame.Rect(190,540,40,40),
                   pygame.Rect(200,30,40,40), pygame.Rect(240,30,40,40)],
        'springs': [pygame.Rect(70,540,30,40)],
        'stars': [pygame.Rect(720,450,20,20)],
        'coins': [pygame.Rect(380,360,20,20), pygame.Rect(420,360,20,20),
                  pygame.Rect(680,240,20,20), pygame.Rect(560,500,20,20)],
        'goal': pygame.Rect(1160,30,24,550),
        'start': (100,500),
        'theme': (20,70,70,150,230,230),
        'portals': [PortalFlip(450,460), PortalFlip(800,30)],
        'phase': [PhasePlatform(pygame.Rect(350,360,120,30), 80, 50),
                  PhasePlatform(pygame.Rect(700,280,120,30), 70, 60)],
    })
    # Level 6: Ice World
    L.append({
        'name': 'Ice World',
        'platforms': [pygame.Rect(-300,580,1500,40), pygame.Rect(-300,30,1500,40)],
        'moving': [MovingPlatform(pygame.Rect(300,450,100,30),'x',200,2.5),
                  MovingPlatform(pygame.Rect(650,350,100,30),'y',150,2.8)],
        'enemies': [FlyEnemy(350,470,55,1.8), FlyEnemy(600,480,50,1.6), FlyEnemy(850,430,45,1.9,True)],
        'saws': [Saw(500,460), Saw(750,460)],
        'spikes': [pygame.Rect(150,540,40,40), pygame.Rect(190,540,40,40),
                   pygame.Rect(150,30,40,40), pygame.Rect(190,30,40,40),
                   pygame.Rect(550,540,40,40), pygame.Rect(590,540,40,40)],
        'springs': [pygame.Rect(80,540,30,40)],
        'stars': [pygame.Rect(400,450,20,20)],
        'shields': [Shield(550, 450)],
        'coins': [pygame.Rect(320,410,20,20), pygame.Rect(360,410,20,20),
                  pygame.Rect(680,310,20,20), pygame.Rect(720,310,20,20)],
        'goal': pygame.Rect(1160,30,24,550),
        'start': (100,500),
        'theme': (200,230,255,240,248,255),
        'portals': [PortalFlip(420,460), PortalFlip(780,30)],
        'phase': [PhasePlatform(pygame.Rect(280,380,120,30), 90, 40)],
    })
    # Level 7: Lava World
    L.append({
        'name': 'Lava World',
        'platforms': [pygame.Rect(-300,580,1500,40), pygame.Rect(-300,30,1500,40)],
        'moving': [MovingPlatform(pygame.Rect(350,430,90,30),'x',180,2.6)],
        'enemies': [FlyEnemy(250,470,50,1.9), FlyEnemy(550,480,55,1.7), FlyEnemy(800,440,45,2.0,True)],
        'saws': [Saw(450,460), Saw(700,460)],
        'spikes': [pygame.Rect(120,540,40,40), pygame.Rect(160,540,40,40),
                   pygame.Rect(120,30,40,40), pygame.Rect(160,30,40,40),
                   pygame.Rect(600,540,40,40), pygame.Rect(640,540,40,40),
                   pygame.Rect(600,30,40,40), pygame.Rect(640,30,40,40)],
        'springs': [pygame.Rect(70,540,30,40)],
        'stars': [pygame.Rect(500,450,20,20)],
        'shields': [Shield(300, 450)],
        'coins': [pygame.Rect(380,390,20,20), pygame.Rect(420,390,20,20),
                  pygame.Rect(720,400,20,20), pygame.Rect(760,400,20,20)],
        'goal': pygame.Rect(1160,30,24,550),
        'start': (80,500),
        'theme': (255,80,30,255,150,50),
        'portals': [PortalFlip(480,460), PortalFlip(820,30)],
    })
    # Level 8: Space World (zero-g feel, more portals)
    L.append({
        'name': 'Space World',
        'platforms': [pygame.Rect(-300,580,1500,40), pygame.Rect(-300,30,1500,40)],
        'moving': [MovingPlatform(pygame.Rect(250,420,100,30),'x',220,3.0),
                  MovingPlatform(pygame.Rect(600,320,100,30),'y',180,3.2)],
        'enemies': [FlyEnemy(300,470,60,2.0), FlyEnemy(650,480,55,1.8), FlyEnemy(880,430,50,2.1,True)],
        'saws': [Saw(520,460), Saw(780,460)],
        'spikes': [pygame.Rect(200,540,40,40), pygame.Rect(240,540,40,40),
                   pygame.Rect(200,30,40,40), pygame.Rect(240,30,40,40)],
        'springs': [pygame.Rect(60,540,30,40)],
        'stars': [pygame.Rect(420,450,20,20), pygame.Rect(700,450,20,20)],
        'shields': [Shield(550, 450)],
        'coins': [pygame.Rect(280,380,20,20), pygame.Rect(320,380,20,20),
                  pygame.Rect(680,280,20,20), pygame.Rect(720,280,20,20),
                  pygame.Rect(500,500,20,20)],
        'goal': pygame.Rect(1160,30,24,550),
        'start': (100,500),
        'theme': (10,10,40,40,20,80),
        'portals': [PortalFlip(350,460), PortalFlip(600,30), PortalFlip(850,460)],
        'phase': [PhasePlatform(pygame.Rect(450,360,120,30), 60, 40),
                  PhasePlatform(pygame.Rect(750,280,120,30), 50, 50)],
    })
    # Level 9: Boss Fight
    L.append({
        'name': 'Boss Arena',
        'platforms': [pygame.Rect(-300,580,1500,40), pygame.Rect(-300,30,1500,40)],
        'moving': [],
        'enemies': [FlyEnemy(250,470,45,1.8), FlyEnemy(700,480,45,1.6)],
        'saws': [Saw(600,460)],
        'spikes': [pygame.Rect(150,540,40,40), pygame.Rect(190,540,40,40),
                   pygame.Rect(150,30,40,40), pygame.Rect(190,30,40,40)],
        'springs': [pygame.Rect(70,540,30,40)],
        'stars': [pygame.Rect(400,450,20,20)],
        'coins': [pygame.Rect(350,500,20,20), pygame.Rect(500,500,20,20),
                  pygame.Rect(650,500,20,20)],
        'goal': pygame.Rect(1160,30,24,550),
        'start': (100,500),
        'theme': (40,10,30,120,20,60),
        'boss': Boss(800, 450),
    })
    return L

def run_game(test_mode=False):
    pygame.init()
    sounds.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption('Gravity Flip')
    clock = pygame.time.Clock()

    levels = make_levels()
    level_idx = 0
    level = levels[0]
    player = Player(*level['start'], lives=3)
    cam = 0; shake = 0; flash = 0
    fade = 0; particles = []
    running = True; frames = 0
    won = False
    paused = False
    started = False
    time = 0

    bg_cache = {}

    def render_bg(theme, gdir):
        key = (theme, gdir)
        if key in bg_cache:
            return bg_cache[key]
        surf = pygame.Surface((SCREEN_W, SCREEN_H))
        r,g,b,r2,g2,b2 = theme
        if gdir < 0:
            r,g,b,r2,g2,b2 = r2,g2,b2,r,g,b
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            c = (int(r+(r2-r)*t), int(g+(g2-g)*t), int(b+(b2-b)*t))
            pygame.draw.line(surf, c, (0,y), (SCREEN_W,y))
        for i in range(70):
            px = (i*137) % SCREEN_W
            py = (i*61) % SCREEN_H
            pygame.draw.circle(surf, WHITE, (px, py), 1)
        # decorative clouds
        for i, (cx, cy, cw) in enumerate([(80,90,90), (320,50,70), (600,110,80), (800,60,60)]):
            pygame.draw.ellipse(surf, (255,255,255,40), (cx, cy, cw, 30))
            pygame.draw.ellipse(surf, (255,255,255,40), (cx+15, cy-12, cw-20, 25))
        bg_cache[key] = surf
        return surf

    def load_level(idx, keep_lives=True):
        nonlocal level, player, cam, fade, shake, flash, particles
        old_lives = player.lives if keep_lives else 3
        level = levels[idx]
        player = Player(*level['start'], lives=old_lives)
        cam = 0; fade = 25; shake = 0; flash = 0; particles = []

    while running:
        clock.tick(FPS); frames += 1; time += 1
        if test_mode and frames > 420:
            print('TEST_PASS'); pygame.quit(); sys.exit(0)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if not started:
                    if e.key == pygame.K_RETURN or e.key == pygame.K_SPACE:
                        started = True; load_level(0); player.lives = 3
                    continue
                if paused:
                    if e.key == pygame.K_ESCAPE or e.key == pygame.K_p:
                        paused = False
                    continue
                if e.key == pygame.K_SPACE:
                    player.flip()
                    flash = 8
                    sounds.play('flip')
                    for _ in range(22):
                        particles.append(Particle(player.rect.centerx, player.rect.centery, CYAN, 5, player.gdir))
                elif e.key == pygame.K_LSHIFT or e.key == pygame.K_RSHIFT:
                    if player.dash():
                        sounds.play('dash')
                        for _ in range(12):
                            particles.append(Particle(player.rect.centerx, player.rect.centery, CYAN, 3, player.gdir))
                elif e.key == pygame.K_r and (not player.alive or won or player.lives <= 0):
                    levels = make_levels()
                    level_idx = 0
                    load_level(0, keep_lives=False); won = False
                elif e.key == pygame.K_ESCAPE:
                    paused = True

        keys = pygame.key.get_pressed()
        player.vx = 0
        if not started:
            # START SCREEN
            screen.blit(render_bg(level['theme'], player.gdir), (0,0))
            # Animated title with glow
            title_pulse = 0.5 + 0.5 * math.sin(time * 0.05)
            title_color = (100 + int(155 * title_pulse), 200, 255)
            font = pygame.font.Font(None, 80)
            title = font.render('GRAVITY FLIP', True, title_color)
            title_shadow = font.render('GRAVITY FLIP', True, (0,0,40))
            screen.blit(title_shadow, (SCREEN_W//2 - title.get_width()//2 + 4, 204))
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 200))
            graphics.draw_glow_circle(screen, CYAN, (SCREEN_W//2, 240), 120, 30)
            # Subtitle
            f2 = pygame.font.Font(None, 32)
            sub = f2.render('Press ENTER to start', True, YELLOW)
            sub_pulse = 0.5 + 0.5 * math.sin(time * 0.08)
            if sub_pulse > 0.7:
                screen.blit(sub, (SCREEN_W//2 - sub.get_width()//2, 320))
            # Controls
            f3 = pygame.font.Font(None, 24)
            hint = f3.render('SPACE = flip | LEFT/RIGHT = move | UP/DOWN = jump | SHIFT = dash', True, (220,220,220))
            screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, 380))
            # Level count
            lvl = f3.render(f'{len(levels)} Levels • Boss Fight • Shields • Double Jump', True, (180,180,200))
            screen.blit(lvl, (SCREEN_W//2 - lvl.get_width()//2, 420))
            pygame.display.flip()
            continue
        if paused:
            screen.blit(render_bg(level['theme'], player.gdir), (0,0))
            font = pygame.font.Font(None, 64)
            pt = font.render('PAUSED', True, WHITE)
            screen.blit(pt, (SCREEN_W//2 - pt.get_width()//2, 250))
            f2 = pygame.font.Font(None, 30)
            ph = f2.render('Press ESC to resume', True, YELLOW)
            screen.blit(ph, (SCREEN_W//2 - ph.get_width()//2, 340))
            pygame.display.flip()
            continue
        if not won and player.lives > 0:
            if keys[pygame.K_LEFT]:
                player.vx = -SPEED; player.facing = -1
            if keys[pygame.K_RIGHT]:
                player.vx = SPEED; player.facing = 1
            if keys[pygame.K_UP]:
                player.jump()
            if keys[pygame.K_DOWN]:
                player.jump()

        plat_rects = list(level['platforms'])
        for ph in level.get('phase', []):
            ph.update()
            if ph.state:
                plat_rects.append(ph.rect)
        if player.star > 0 and player.grounded and random.random() < 0.15 and not won and player.lives > 0:
            particles.append(Particle(player.rect.centerx, player.rect.bottom, YELLOW, 1.2, player.gdir))

        player.update(plat_rects, level['moving'])
        for m in level['moving']: m.update()
        for e in level['enemies']: e.update()
        for s in level['saws']: s.update()

        for s in level['spikes']:
            if player.rect.colliderect(s):
                player.alive = False
                sounds.play('death')
        for sp in level['springs']:
            if player.rect.colliderect(sp) and not player.spring_cooldown:
                player.vy = -17 * player.gdir; player.grounded = False
                player.spring_cooldown = 20
                sounds.play('spring')
                for _ in range(14): particles.append(Particle(sp.centerx, sp.centery, ORANGE, 4, player.gdir))
        if player.spring_cooldown > 0:
            player.spring_cooldown -= 1
        for st in level['stars'][:]:
            if player.rect.colliderect(st):
                level['stars'].remove(st); player.star = 360
                sounds.play('star')
                for _ in range(26): particles.append(Particle(st.centerx, st.centery, YELLOW, 6, player.gdir))
        for c in level['coins'][:]:
            if player.rect.colliderect(c):
                level['coins'].remove(c); player.coins += 1
                sounds.play('coin')
                for _ in range(10): particles.append(Particle(c.centerx, c.centery, YELLOW, 3, player.gdir))
        for sh in level.get('shields', [])[:]:
            sh.update()
            if player.rect.colliderect(sh.rect):
                level['shields'].remove(sh)
                player.shield = True
                sounds.play('shield')
                for _ in range(20):
                    particles.append(Particle(sh.rect.centerx, sh.rect.centery, CYAN, 5, player.gdir))

        # hazards: enemy / saw hits
        hit_hazard = False
        for e in level['enemies']:
            if e.alive and player.rect.colliderect(e.rect):
                # stomp check depends on gravity direction
                if player.gdir > 0:
                    stomped = abs(player.vy) > 3 and player.rect.bottom <= e.rect.centery + 12
                else:
                    stomped = abs(player.vy) > 3 and player.rect.top >= e.rect.centery - 12
                if stomped:
                    e.alive = False; player.vy = -9 * player.gdir; player.coins += 5
                    sounds.play('hit')
                    for _ in range(16): particles.append(Particle(e.rect.centerx, e.rect.centery, ORANGE, 4, player.gdir))
                elif player.star > 0:
                    e.alive = False; player.coins += 5
                    sounds.play('hit')
                    for _ in range(16): particles.append(Particle(e.rect.centerx, e.rect.centery, YELLOW, 4, player.gdir))
                else:
                    hit_hazard = True
        for s in level['saws']:
            if player.rect.colliderect(s.rect):
                if player.star > 0: shake = 14
                else: hit_hazard = True
        for pu in level.get('portals', []):
            pu.update()
            if player.rect.colliderect(pu.rect) and not player.portal_cooldown:
                player.flip()
                player.portal_cooldown = 30
                flash = 10
                sounds.play('portal')
                for _ in range(18):
                    particles.append(Particle(pu.rect.centerx, pu.rect.centery, CYAN, 5, player.gdir))
        if player.portal_cooldown > 0:
            player.portal_cooldown -= 1
        if hit_hazard:
            if player.shield:
                player.shield = False
                sounds.play('shield')
                flash = 15
                for _ in range(30):
                    particles.append(Particle(player.rect.centerx, player.rect.centery, CYAN, 6, player.gdir))
            else:
                player.alive = False
                sounds.play('death')

        # Boss fight
        if 'boss' in level and level['boss'].alive:
            boss = level['boss']
            boss.update(plat_rects, player)
            # boss collision
            if player.rect.colliderect(boss.rect):
                # stomp check depends on gravity direction
                if player.gdir > 0:
                    boss_stomped = abs(player.vy) > 4 and player.rect.bottom <= boss.rect.centery + 20
                else:
                    boss_stomped = abs(player.vy) > 4 and player.rect.top >= boss.rect.centery - 20
                if player.star > 0:
                    if boss.hit():
                        sounds.play('boss_hit')
                        player.coins += 50
                        for _ in range(40):
                            particles.append(Particle(boss.rect.centerx, boss.rect.centery, LAVA_RED, 7, player.gdir))
                elif boss_stomped:
                    if boss.hit():
                        sounds.play('boss_hit')
                        player.coins += 50
                        for _ in range(40):
                            particles.append(Particle(boss.rect.centerx, boss.rect.centery, LAVA_RED, 7, player.gdir))
                    player.vy = -12 * player.gdir
                else:
                    if player.shield:
                        player.shield = False
                        sounds.play('shield')
                        flash = 15
                    else:
                        player.alive = False
                        sounds.play('death')
            # boss shots
            for s in boss.shots[:]:
                shot_rect = pygame.Rect(int(s[0]) - 8, int(s[1]) - 8, 16, 16)
                if player.rect.colliderect(shot_rect):
                    boss.shots.remove(s)
                    if player.shield:
                        player.shield = False
                        sounds.play('shield')
                        flash = 15
                    else:
                        player.alive = False
                        sounds.play('death')
            if not boss.alive and not won:
                won = True; flash = 20
                sounds.play('win'); sounds.play('win2'); sounds.play('win3')
                print('BOSS_DEFEATED')
                if test_mode:
                    pygame.quit(); sys.exit(0)

        # Boss level: goal only works after boss is defeated
        boss_alive = 'boss' in level and level['boss'].alive
        if player.rect.colliderect(level['goal']) and not boss_alive:
            if level_idx < len(levels)-1:
                level_idx += 1; load_level(level_idx); flash = 15
                sounds.play('powerup')
            else:
                won = True; flash = 20
                sounds.play('win'); sounds.play('win2'); sounds.play('win3')
                print('ALL_LEVELS_COMPLETE')
                if test_mode:
                    pygame.quit(); sys.exit(0)

        if not player.alive and not won:
            player.lives -= 1
            if player.lives > 0:
                player.alive = True
            if player.lives <= 0:
                print('GAME_OVER')
                if test_mode:
                    pygame.quit(); sys.exit(0)
                player = Player(*level['start'], lives=0)
            else:
                player = Player(*level['start'], lives=player.lives)
                flash = 20
                # reset enemies to original positions and revive them
                for e in level['enemies']:
                    e.alive = True
                    e.rect.x = e.start_x
                    e.rect.y = e.start_y
                # reset boss HP
                if 'boss' in level:
                    boss = level['boss']
                    boss.alive = True
                    boss.hp = boss.max_hp
                    boss.shots = []
                    boss.rect.x = boss.start_x
                    boss.rect.y = boss.start_y

        target = player.rect.centerx - SCREEN_W//2
        cam += (target - cam) * 0.08
        cam = max(0, min(cam, max(0, (max(p.right for p in level['platforms']) - SCREEN_W))))
        if shake > 0:
            cam += random.randint(-3,3); shake -= 1
        if flash > 0: flash -= 1
        if fade > 0: fade -= 1
        particles = [p for p in particles if p.life > 0]
        for p in particles: p.update()

        # ---------- DRAW ----------
        screen.blit(render_bg(level['theme'], player.gdir), (0,0))

        for p in level['platforms']:
            graphics.draw_platform(screen, p, cam, time)
        for m in level['moving']:
            graphics.draw_moving_platform(screen, m, cam, time)
        for ph in level.get('phase', []):
            ph.draw(screen, cam, time)
        for s in level['spikes']:
            graphics.draw_spike(screen, s, cam, player.gdir)
        for sp in level['springs']:
            graphics.draw_spring(screen, sp, cam, time)
        for st in level['stars']:
            graphics.draw_star_pickup(screen, st, cam, time)
        for c in level['coins']:
            graphics.draw_coin(screen, c, cam, time)
        for e in level['enemies']:
            if e.alive: e.draw(screen, cam, time)
        for s in level['saws']: s.draw(screen, cam, time)
        for pu in level.get('portals', []):
            pu.draw(screen, cam, time)
        for sh in level.get('shields', []):
            sh.draw(screen, cam, time)
        if 'boss' in level and level['boss'].alive:
            level['boss'].draw(screen, cam, time)

        graphics.draw_goal_flag(screen, level['goal'], cam, time)

        player.draw(screen, cam, time)
        for p in particles: p.draw(screen, cam)

        if flash > 0 and flash % 4 == 0:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((255,255,255,70)); screen.blit(ov, (0,0))
        if fade > 0:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0,0,0, int(150 * fade/25))); screen.blit(ov, (0,0))

        # HUD panel
        graphics.draw_hud(screen, player, level, level_idx, len(levels), time)
        font = pygame.font.Font(None, 34)
        if won:
            wtxt = font.render('YOU WIN! Press R to restart', True, YELLOW)
            screen.blit(wtxt, (SCREEN_W//2 - 200, SCREEN_H//2))
        elif player.lives <= 0:
            otxt = font.render('GAME OVER — Press R', True, RED)
            screen.blit(otxt, (SCREEN_W//2 - 160, SCREEN_H//2))

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    run_game('--test' in sys.argv)
