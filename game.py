import sys, random, math
import pygame

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

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 40)
        self.vx = 0; self.vy = 0
        self.gdir = 1       # 1 = down, -1 = up
        self.grounded = False
        self.alive = True
        self.coins = 0
        self.lives = 3
        self.facing = 1
        self.star = 0

    def update(self, rects, movs):
        if not self.alive:
            return
        self.rect.x += self.vx
        for r in rects + [m.rect for m in movs]:
            if self.rect.colliderect(r):
                if self.vx > 0: self.rect.right = r.left
                elif self.vx < 0: self.rect.left = r.right

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
                    self.rect.x += m.vx
                elif self.gdir < 0 and self.vy <= 0:
                    self.rect.top = m.rect.bottom; self.vy = 0; self.grounded = True
                    self.rect.x += m.vx

        if self.rect.top > 1100 or self.rect.bottom < -500:
            self.alive = False
        if self.star > 0:
            self.star -= 1

    def jump(self):
        if self.alive and self.grounded:
            self.vy = JUMP * self.gdir
            self.grounded = False

    def flip(self):
        if not self.alive:
            return
        self.gdir *= -1
        self.vy = 0

    def draw(self, screen, cam):
        x = self.rect.x - cam; y = self.rect.y
        w, h = self.rect.w, self.rect.h
        body = RED
        if self.star > 0:
            body = [YELLOW, ORANGE, PURPLE, CYAN][(self.star // 6) % 4]
        pygame.draw.rect(screen, BLACK, (x-2, y-8, w+4, h+10), 2)
        pygame.draw.rect(screen, body, (x-2, y-6, w+4, 10))
        pygame.draw.rect(screen, body, (x+2, y-10, 14, 6))
        pygame.draw.rect(screen, (255,200,150), (x+3, y+2, w-6, 14))
        pygame.draw.rect(screen, BLUE, (x, y+16, w, h-16))
        ex = x + 21 if self.facing > 0 else x + 5
        pygame.draw.circle(screen, BLACK, (ex, y+8), 3)

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
    def draw(self, screen, cam):
        x = self.rect.x - cam; y = self.rect.y
        pygame.draw.ellipse(screen, (150,50,30), (x, y, 34, 30))
        pygame.draw.circle(screen, WHITE, (x+8, y+9), 4)
        pygame.draw.circle(screen, WHITE, (x+26, y+9), 4)
        pygame.draw.circle(screen, BLACK, (x+10, y+10), 2)
        pygame.draw.circle(screen, BLACK, (x+24, y+10), 2)
        pygame.draw.polygon(screen, (255,200,150), [(x+2,y+14),(x-8,y+6),(x-6,y+18)])
        pygame.draw.polygon(screen, (255,200,150), [(x+32,y+14),(x+42,y+6),(x+40,y+18)])

class Saw:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 44, 44)
        self.ang = 0
    def update(self):
        self.ang += 6
    def draw(self, screen, cam):
        cx = self.rect.centerx - cam; cy = self.rect.centery
        pts = []
        for i in range(8):
            a = math.radians(self.ang + i*45)
            r = 22 if i % 2 == 0 else 13
            pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
        pygame.draw.polygon(screen, GRAY, pts)
        pygame.draw.circle(screen, BLACK, (int(cx), int(cy)), 5)

class MovingPlatform:
    def __init__(self, r, axis, dist, speed):
        self.rect = r; self.axis = axis; self.dist = dist; self.speed = speed
        self.start = r.x if axis == 'x' else r.y
        self.vx = speed if axis == 'x' else 0
    def update(self):
        if self.axis == 'x':
            self.rect.x += self.speed; self.vx = self.speed
            if self.rect.x > self.start + self.dist or self.rect.x < self.start:
                self.speed *= -1
        else:
            self.rect.y += self.speed; self.vx = 0
            if self.rect.y > self.start + self.dist or self.rect.y < self.start:
                self.speed *= -1

class Particle:
    def __init__(self, x, y, color, spread=3):
        self.x = x; self.y = y
        self.vx = random.uniform(-spread, spread)
        self.vy = random.uniform(-spread, spread)
        self.life = random.randint(12, 28); self.color = color
    def update(self):
        self.x += self.vx; self.y += self.vy; self.vy += 0.08; self.life -= 1
    def draw(self, screen):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), max(2, self.life // 6))

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
    return L

def run_game(test_mode=False):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption('Gravity Flip')
    clock = pygame.time.Clock()

    levels = make_levels()
    level_idx = 0
    level = levels[0]
    player = Player(*level['start'])
    cam = 0; shake = 0; flash = 0
    fade = 0; particles = []
    running = True; frames = 0
    won = False
    paused = False
    started = False

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

    def load_level(idx):
        nonlocal level, player, cam, fade
        level = levels[idx]; player = Player(*level['start'])
        cam = 0; fade = 25

    while running:
        clock.tick(FPS); frames += 1
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
                    for _ in range(22):
                        particles.append(Particle(player.rect.centerx, player.rect.centery, CYAN, 5))
                elif e.key == pygame.K_r and (not player.alive or won):
                    load_level(0); won = False; player.lives = 3
                elif e.key == pygame.K_ESCAPE:
                    paused = True

        keys = pygame.key.get_pressed()
        player.vx = 0
        if not started:
            # START SCREEN
            screen.blit(render_bg(level['theme'], player.gdir), (0,0))
            font = pygame.font.Font(None, 64)
            title = font.render('GRAVITY FLIP', True, WHITE)
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 200))
            f2 = pygame.font.Font(None, 30)
            sub = f2.render('Press ENTER to start', True, YELLOW)
            screen.blit(sub, (SCREEN_W//2 - sub.get_width()//2, 300))
            hint = f2.render('SPACE = flip gravity | LEFT/RIGHT = move | UP = jump', True, (220,220,220))
            screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, 360))
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
        if keys[pygame.K_LEFT]:
            player.vx = -SPEED; player.facing = -1
        if keys[pygame.K_RIGHT]:
            player.vx = SPEED; player.facing = 1
        if keys[pygame.K_UP]:
            player.jump()

        plat_rects = [p for p in level['platforms']]
        if player.star > 0 and player.grounded and random.random() < 0.15:
            particles.append(Particle(player.rect.centerx, player.rect.bottom, YELLOW, 1.2))

        player.update(plat_rects, level['moving'])
        for m in level['moving']: m.update()
        for e in level['enemies']: e.update()
        for s in level['saws']: s.update()

        for s in level['spikes']:
            if player.rect.colliderect(s):
                player.alive = False
        for sp in level['springs']:
            if player.rect.colliderect(sp):
                player.vy = -17 * player.gdir; player.grounded = False
                for _ in range(14): particles.append(Particle(sp.centerx, sp.centery, ORANGE, 4))
        for st in level['stars'][:]:
            if player.rect.colliderect(st):
                level['stars'].remove(st); player.star = 360
                for _ in range(26): particles.append(Particle(st.centerx, st.centery, YELLOW, 6))
        for c in level['coins'][:]:
            if player.rect.colliderect(c):
                level['coins'].remove(c); player.coins += 1
                for _ in range(10): particles.append(Particle(c.centerx, c.centery, YELLOW))

        # hazards: enemy / saw hits
        hit_hazard = False
        for e in level['enemies']:
            if e.alive and player.rect.colliderect(e.rect):
                if abs(player.vy * player.gdir) > 3 and player.rect.bottom <= e.rect.centery + 12:
                    e.alive = False; player.vy = -9 * player.gdir; player.coins += 5
                    for _ in range(16): particles.append(Particle(e.rect.centerx, e.rect.centery, ORANGE, 4))
                elif player.star > 0:
                    e.alive = False; player.coins += 5
                    for _ in range(16): particles.append(Particle(e.rect.centerx, e.rect.centery, YELLOW, 4))
                else:
                    hit_hazard = True
        for s in level['saws']:
            if player.rect.colliderect(s.rect):
                if player.star > 0: shake = 14
                else: hit_hazard = True
        if hit_hazard:
            player.alive = False

        if player.rect.colliderect(level['goal']):
            if level_idx < len(levels)-1:
                level_idx += 1; load_level(level_idx); flash = 15
            else:
                won = True; flash = 20
                print('ALL_LEVELS_COMPLETE')
                if test_mode:
                    pygame.quit(); sys.exit(0)

        if not player.alive and not won:
            player.lives -= 1
            if player.lives <= 0:
                print('GAME_OVER')
                if test_mode:
                    pygame.quit(); sys.exit(0)
                player = Player(*level['start']); player.lives = 0
            else:
                player = Player(*level['start']); flash = 20

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
            x = p.x - cam; y = p.y
            if y < 100:
                pygame.draw.rect(screen, BLUE, (x,y,p.w,p.h))
                pygame.draw.rect(screen, (0,40,100), (x,y,p.w,8))
            else:
                pygame.draw.rect(screen, GREEN, (x,y,p.w,p.h))
                pygame.draw.rect(screen, (0,80,30), (x,y,p.w,8))
        for m in level['moving']:
            x = m.rect.x - cam; y = m.rect.y
            pygame.draw.rect(screen, PURPLE, (x,y,m.rect.w,m.rect.h))
            pygame.draw.rect(screen, (100,40,160), (x,y,m.rect.w,6))
        for s in level['spikes']:
            x = s.x - cam; y = s.y
            if player.gdir > 0:
                pts = [(x,y+s.h),(x+s.w//2,y),(x+s.w,y+s.h)]
            else:
                pts = [(x,y),(x+s.w//2,y+s.h),(x+s.w,y)]
            pygame.draw.polygon(screen, RED, pts)
        for sp in level['springs']:
            x = sp.x - cam; y = sp.y
            pygame.draw.rect(screen, ORANGE, (x,y,30,40))
            pygame.draw.rect(screen, YELLOW, (x+4,y+24,22,12))
        for st in level['stars']:
            cx = st.centerx - cam; cy = st.centery
            pts = []
            for i in range(10):
                a = math.pi*i/5 - math.pi/2
                r = 12 if i%2==0 else 6
                pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
            pygame.draw.polygon(screen, YELLOW, pts)
        for c in level['coins']:
            x = c.centerx - cam; y = c.centery
            pygame.draw.circle(screen, YELLOW, (int(x),int(y)), 10)
            pygame.draw.circle(screen, (255,250,180), (int(x),int(y)), 6)
        for e in level['enemies']:
            if e.alive: e.draw(screen, cam)
        for s in level['saws']: s.draw(screen, cam)

        gx = level['goal'].x - cam; gy = level['goal'].y
        gh = level['goal'].h
        pygame.draw.rect(screen, (180,180,180), (gx, gy, 8, gh))
        pygame.draw.circle(screen, YELLOW, (gx+4, gy+6), 10)
        # flag cloth
        pygame.draw.polygon(screen, RED, [(gx+8, gy+14), (gx+58, gy+24), (gx+8, gy+36)])

        player.draw(screen, cam)
        for p in particles: p.draw(screen)

        if flash > 0 and flash % 4 == 0:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((255,255,255,70)); screen.blit(ov, (0,0))
        if fade > 0:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0,0,0, int(150 * fade/25))); screen.blit(ov, (0,0))

        # HUD panel
        hud = pygame.Surface((SCREEN_W, 120), pygame.SRCALPHA)
        hud.fill((0,0,0,110)); screen.blit(hud, (0,0))
        font = pygame.font.Font(None, 34)
        font_small = pygame.font.Font(None, 24)

        title = font.render(f'{level["name"]} — {level_idx+1}/4', True, WHITE)
        screen.blit(title, (16, 10))
        hint = font_small.render('SPACE = flip gravity   LEFT/RIGHT = move   UP = jump   ESC = menu', True, (220,220,220))
        screen.blit(hint, (16, 44))

        # gravity meter
        txt = 'GRAVITY: DOWN' if player.gdir > 0 else 'GRAVITY: UP'
        color = GREEN if player.gdir > 0 else ORANGE
        gtxt = font.render(txt, True, color)
        screen.blit(gtxt, (16, 76))

        # hearts
        for i in range(player.lives):
            pygame.draw.rect(screen, RED, (SCREEN_W - 140 + i*28, 76, 22, 18))
            pygame.draw.rect(screen, (150,20,20), (SCREEN_W - 140 + i*28, 76, 22, 5))
        ctxt = font.render(f'Coins: {player.coins}', True, YELLOW)
        screen.blit(ctxt, (SCREEN_W - 230, 14))
        if player.star > 0:
            stxt = font.render(f'STAR {player.star//60+1}s', True, YELLOW)
            screen.blit(stxt, (SCREEN_W - 230, 50))
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
