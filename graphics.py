"""
Enhanced graphics module for Gravity Flip — better sprites, animations, glow effects.
"""
import math
import random
import pygame

# Color palette
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (230,60,60)
GREEN = (70,200,90)
BLUE = (70,130,255)
PURPLE = (170,70,255)
YELLOW = (255,225,70)
ORANGE = (255,150,50)
CYAN = (0,210,210)
GRAY = (110,110,110)
DARK_GRAY = (60,60,70)
SKIN = (255,200,150)
SKIN_DARK = (230,170,120)
BROWN = (139,69,19)
SCREEN_W = 900
SCREEN_H = 650


_glow_cache = {}

def draw_glow_circle(screen, color, pos, radius, alpha=60):
    """Draw a soft glow around a point (cached for performance)."""
    radius = max(2, int(radius))
    key = (radius, color, alpha)
    if key not in _glow_cache:
        size = radius * 4
        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(3):
            r = radius * (1 - i*0.25)
            a = alpha // (i+1)
            pygame.draw.circle(glow, (*color, a), (radius*2, radius*2), int(r))
        _glow_cache[key] = glow
    glow = _glow_cache[key]
    screen.blit(glow, (pos[0]-radius*2, pos[1]-radius*2), special_flags=pygame.BLEND_ADD)


def draw_player(screen, player, cam, time):
    """Draw the player with a proper character design."""
    x = player.rect.x - cam
    y = player.rect.y
    w, h = player.rect.w, player.rect.h
    facing = player.facing

    # Star invincibility flash
    if player.star > 0 and (player.star // 4) % 2 == 0:
        body_color = [YELLOW, ORANGE, PURPLE, CYAN][(player.star // 8) % 4]
    else:
        body_color = RED

    # Shadow
    pygame.draw.ellipse(screen, (0,0,0,40), (x-2, y+h-4, w+4, 8))

    # Dash trail
    if player.dash_timer > 0:
        for i in range(3):
            tx = x - facing * (i+1) * 8
            alpha = 80 - i*25
            trail = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(trail, (*CYAN, alpha), (0, 0, w, h), border_radius=8)
            screen.blit(trail, (tx, y))

    # Body (rounded)
    pygame.draw.rect(screen, BLACK, (x-2, y-8, w+4, h+10), border_radius=10)
    pygame.draw.rect(screen, body_color, (x-2, y-6, w+4, h+6), border_radius=8)

    # Hat
    hat_color = body_color
    pygame.draw.rect(screen, hat_color, (x-2, y-12, w+4, 10), border_radius=4)
    pygame.draw.rect(screen, hat_color, (x+2, y-16, 16, 8), border_radius=3)
    pygame.draw.rect(screen, WHITE, (x-2, y-6, w+4, 3))

    # Face
    pygame.draw.rect(screen, SKIN, (x+3, y+2, w-6, 14), border_radius=5)

    # Eye
    eye_x = x + 21 if facing > 0 else x + 5
    pygame.draw.circle(screen, BLACK, (eye_x, y+8), 3)
    pygame.draw.circle(screen, WHITE, (eye_x+1, y+7), 1)

    # Nose
    nose_x = x + 25 if facing > 0 else x + 2
    pygame.draw.circle(screen, SKIN_DARK, (nose_x, y+12), 3)

    # Body shirt
    shirt_h = h - 18
    pygame.draw.rect(screen, body_color, (x, y+16, w, shirt_h), border_radius=4)

    # Overalls
    pygame.draw.rect(screen, BLUE, (x, y+16+shirt_h-6, w, 10), border_radius=3)

    # Buttons
    pygame.draw.circle(screen, YELLOW, (x+8, y+16+shirt_h-2), 2)
    pygame.draw.circle(screen, YELLOW, (x+w-8, y+16+shirt_h-2), 2)

    # Arms
    arm_y = y + 18
    if facing > 0:
        pygame.draw.rect(screen, SKIN, (x-3, arm_y, 6, 12), border_radius=3)
        pygame.draw.rect(screen, SKIN, (x+w-3, arm_y, 6, 12), border_radius=3)
    else:
        pygame.draw.rect(screen, SKIN, (x-3, arm_y, 6, 12), border_radius=3)
        pygame.draw.rect(screen, SKIN, (x+w-3, arm_y, 6, 12), border_radius=3)

    # Legs / boots
    pygame.draw.rect(screen, BROWN, (x+2, y+h-8, 12, 8), border_radius=3)
    pygame.draw.rect(screen, BROWN, (x+w-14, y+h-8, 12, 8), border_radius=3)

    # Shield bubble
    if player.shield:
        pulse = 4 + int(math.sin(time / 8) * 2)
        draw_glow_circle(screen, CYAN, (x+w//2, y+h//2), w + pulse, 40)
        pygame.draw.circle(screen, (0,200,220), (x+w//2, y+h//2), w + pulse, 2)
        pygame.draw.circle(screen, (200,255,255), (x+w//2-6, y+h//2-8), 3)

    # Star aura
    if player.star > 0:
        draw_glow_circle(screen, YELLOW, (x+w//2, y+h//2), w+8, 50)


def draw_fly_enemy(screen, enemy, cam, time):
    """Draw flying enemy with animated wings."""
    x = enemy.rect.x - cam
    y = enemy.rect.y
    w, h = enemy.rect.w, enemy.rect.h

    # Body
    pygame.draw.ellipse(screen, (150,50,30), (x, y, w, h))
    pygame.draw.ellipse(screen, (120,35,20), (x+4, y+h-8, w-8, 8))

    # Wings (flapping)
    flap = math.sin(time * 0.3 + enemy.t) * 8
    wing_color = (200,180,160)
    # Left wing
    pygame.draw.polygon(screen, wing_color, [
        (x+2, y+8),
        (x-14, y+4 + flap),
        (x-10, y+16 + flap*0.5),
    ])
    # Right wing
    pygame.draw.polygon(screen, wing_color, [
        (x+w-2, y+8),
        (x+w+14, y+4 + flap),
        (x+w+10, y+16 + flap*0.5),
    ])

    # Eyes
    pygame.draw.circle(screen, WHITE, (x+8, y+9), 5)
    pygame.draw.circle(screen, WHITE, (x+w-8, y+9), 5)
    pygame.draw.circle(screen, BLACK, (x+10, y+10), 2)
    pygame.draw.circle(screen, BLACK, (x+w-6, y+10), 2)

    # Mouth
    pygame.draw.arc(screen, (100,30,20), (x+8, y+14, w-16, 10), 0, math.pi, 2)

    # Feet
    pygame.draw.polygon(screen, (255,200,150), [(x+2,y+h-4),(x-6,y+h+4),(x+2,y+h+2)])
    pygame.draw.polygon(screen, (255,200,150), [(x+w-2,y+h-4),(x+w+6,y+h+4),(x+w-2,y+h+2)])


def draw_saw(screen, saw, cam, time):
    """Draw saw with metallic shine and glow."""
    cx = saw.rect.centerx - cam
    cy = saw.rect.centery

    # Glow
    draw_glow_circle(screen, (200,200,200), (cx, cy), 26, 30)

    # Outer teeth
    pts = []
    for i in range(8):
        a = math.radians(saw.ang + i*45)
        r = 22 if i % 2 == 0 else 13
        pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    pygame.draw.polygon(screen, (160,160,170), pts)
    pygame.draw.polygon(screen, (80,80,90), pts, 2)

    # Inner disc
    pygame.draw.circle(screen, (200,200,210), (int(cx), int(cy)), 12)
    pygame.draw.circle(screen, (120,120,130), (int(cx), int(cy)), 12, 2)

    # Center hub
    pygame.draw.circle(screen, (60,60,70), (int(cx), int(cy)), 5)
    pygame.draw.circle(screen, BLACK, (int(cx), int(cy)), 3)

    # Shine highlight
    shine_a = math.radians(saw.ang)
    sx = cx + 8 * math.cos(shine_a)
    sy = cy + 8 * math.sin(shine_a)
    pygame.draw.circle(screen, (240,240,255), (int(sx), int(sy)), 3)


def draw_moving_platform(screen, m, cam, time):
    """Draw moving platform with glowing edges and bolts."""
    x = m.rect.x - cam
    y = m.rect.y
    w, h = m.rect.w, m.rect.h

    # Body
    pygame.draw.rect(screen, (90,60,140), (x, y, w, h), border_radius=6)
    pygame.draw.rect(screen, (60,40,100), (x, y, w, h), 2, border_radius=6)

    # Top surface highlight
    pygame.draw.rect(screen, (140,100,190), (x+3, y+3, w-6, 6), border_radius=3)

    # Bolts
    for bx in (x+8, x+w-8):
        pygame.draw.circle(screen, (200,200,210), (bx, y+h//2), 3)
        pygame.draw.circle(screen, (100,100,110), (bx, y+h//2), 3, 1)

    # Glowing edge
    glow_pulse = 0.5 + 0.5 * math.sin(time * 0.05)
    glow_color = (150, 100, 200 + int(55 * glow_pulse))
    pygame.draw.rect(screen, glow_color, (x-1, y-1, w+2, 4), border_radius=2)


def draw_portal(screen, portal, cam, time):
    """Draw portal with swirling energy effect."""
    x = portal.rect.x - cam
    y = portal.rect.y
    w, h = portal.rect.w, portal.rect.h
    cx = x + w//2
    cy = y + h//2

    # Outer glow
    draw_glow_circle(screen, CYAN, (cx, cy), w, 40)

    # Portal body
    pygame.draw.rect(screen, (0,80,100), (x, y, w, h), border_radius=12)
    pygame.draw.rect(screen, CYAN, (x+2, y+2, w-4, h-4), 2, border_radius=10)

    # Swirling energy rings
    for i in range(3):
        a = time * 0.08 + i * (2*math.pi/3)
        rx = w//2 - 6 - i*4
        ry = h//2 - 8 - i*5
        ex = cx + rx * math.cos(a)
        ey = cy + ry * math.sin(a)
        pygame.draw.circle(screen, (100,230,255), (int(ex), int(ey)), 4 - i)

    # Center core
    pulse = 5 + int(math.sin(time * 0.1) * 2)
    pygame.draw.circle(screen, (0,180,200), (cx, cy), pulse)
    pygame.draw.circle(screen, WHITE, (cx, cy), max(2, pulse-2))

    # Arrows indicating flip direction
    arrow_color = (200,255,255)
    pygame.draw.polygon(screen, arrow_color, [(cx-8, cy-14), (cx+8, cy-14), (cx, cy-22)])
    pygame.draw.polygon(screen, arrow_color, [(cx-8, cy+14), (cx+8, cy+14), (cx, cy+22)])


def draw_phase_platform(screen, ph, cam, time):
    """Draw phase platform with pulsing glow and warning state."""
    if not ph.state:
        return
    x = ph.rect.x - cam
    y = ph.rect.y
    w, h = ph.rect.w, ph.rect.h

    # Warning: about to vanish
    remaining = ph.on_time - ph.timer
    if remaining < 25:
        blink = (remaining // 4) % 2 == 0
        if blink:
            return

    # Body
    pygame.draw.rect(screen, PURPLE, (x, y, w, h), border_radius=6)
    pygame.draw.rect(screen, (100,40,160), (x, y, w, h), 2, border_radius=6)

    # Glowing top
    glow_pulse = 0.5 + 0.5 * math.sin(time * 0.08)
    glow_color = (180 + int(50*glow_pulse), 100, 220)
    pygame.draw.rect(screen, glow_color, (x+2, y+2, w-4, 5), border_radius=2)

    # Circuit pattern
    for i in range(3):
        cy = y + 10 + i*8
        pygame.draw.line(screen, (130,70,190), (x+6, cy), (x+w-6, cy), 1)
        pygame.draw.circle(screen, (180,120,230), (x+6 + i*10, cy), 2)


def draw_shield_pickup(screen, sh, cam, time):
    """Draw shield pickup with bubble effect."""
    x = sh.rect.x - cam
    y = sh.rect.y
    cx = x + 12
    cy = y + 12

    # Glow
    draw_glow_circle(screen, CYAN, (cx, cy), 16, 50)

    # Bubble
    r = 10 + int(math.sin(time * 0.1) * 2)
    pygame.draw.circle(screen, (0,150,180), (cx, cy), r, 3)
    pygame.draw.circle(screen, (0,200,220), (cx, cy), r-3, 2)

    # Shine
    pygame.draw.circle(screen, WHITE, (cx-4, cy-4), 2)

    # Shield icon
    pygame.draw.polygon(screen, CYAN, [
        (cx, cy-6),
        (cx+5, cy-3),
        (cx+5, cy+1),
        (cx, cy+5),
        (cx-5, cy+1),
        (cx-5, cy-3),
    ])


def draw_boss(screen, boss, cam, time):
    """Draw boss with more menacing design."""
    x = boss.rect.x - cam
    y = boss.rect.y
    w, h = boss.rect.w, boss.rect.h

    # Shadow
    pygame.draw.ellipse(screen, (0,0,0,60), (x-6, y+h-4, w+12, 10))

    # Hit flash
    if boss.hit_flash > 0 and boss.hit_flash // 2 % 2 == 0:
        body = (255,255,255)
        detail = (220,220,220)
    else:
        body = (180,40,40)
        detail = (120,20,20)

    # Glow aura
    draw_glow_circle(screen, (255,50,50), (x+w//2, y+h//2), w, 40)

    # Body
    pygame.draw.rect(screen, DARK_GRAY, (x-5, y-5, w+10, h+10), border_radius=14)
    pygame.draw.rect(screen, body, (x, y, w, h), border_radius=12)
    pygame.draw.rect(screen, detail, (x+10, y+10, w-20, h-20), border_radius=8)

    # Horns
    pygame.draw.polygon(screen, DARK_GRAY, [(x+10, y+8), (x+22, y-14), (x+28, y+8)])
    pygame.draw.polygon(screen, DARK_GRAY, [(x+w-10, y+8), (x+w-22, y-14), (x+w-28, y+8)])

    # Eyes (glowing)
    eye_glow = 0.5 + 0.5 * math.sin(time * 0.1)
    eye_color = (255, 200 + int(55*eye_glow), 50)
    pygame.draw.circle(screen, eye_color, (int(x+w//2-14), int(y+28)), 8)
    pygame.draw.circle(screen, eye_color, (int(x+w//2+14), int(y+28)), 8)
    pygame.draw.circle(screen, BLACK, (int(x+w//2-14), int(y+28)), 4)
    pygame.draw.circle(screen, BLACK, (int(x+w//2+14), int(y+28)), 4)

    # Mouth / teeth
    pygame.draw.rect(screen, (60,10,10), (x+20, y+48, w-40, 14), border_radius=4)
    for i in range(5):
        tx = x + 24 + i*12
        pygame.draw.polygon(screen, WHITE, [(tx, y+48), (tx+6, y+48), (tx+3, y+56)])

    # Arms
    pygame.draw.rect(screen, DARK_GRAY, (x-14, y+20, 16, 32), border_radius=6)
    pygame.draw.rect(screen, DARK_GRAY, (x+w-2, y+20, 16, 32), border_radius=6)
    # Fists
    pygame.draw.circle(screen, DARK_GRAY, (x-6, y+52), 9)
    pygame.draw.circle(screen, DARK_GRAY, (x+w+6, y+52), 9)

    # Legs
    pygame.draw.rect(screen, DARK_GRAY, (x+12, y+h-8, 22, 14), border_radius=5)
    pygame.draw.rect(screen, DARK_GRAY, (x+w-34, y+h-8, 22, 14), border_radius=5)

    # HP bar
    bar_w = 90; bar_h = 10
    bx = x + (w - bar_w)//2
    pygame.draw.rect(screen, BLACK, (bx-3, y-24, bar_w+6, bar_h+6), border_radius=4)
    hp_ratio = boss.hp / boss.max_hp
    hp_color = GREEN if hp_ratio > 0.5 else (ORANGE if hp_ratio > 0.25 else RED)
    pygame.draw.rect(screen, hp_color, (bx, y-21, int(bar_w * hp_ratio), bar_h), border_radius=3)
    pygame.draw.rect(screen, WHITE, (bx, y-21, bar_w, bar_h), 1, border_radius=3)

    # Shots
    for s in boss.shots:
        sx = s[0] - cam
        sy = s[1]
        draw_glow_circle(screen, (255,80,30), (int(sx), int(sy)), 10, 40)
        pygame.draw.circle(screen, (255,80,30), (int(sx), int(sy)), 8)
        pygame.draw.circle(screen, YELLOW, (int(sx), int(sy)), 4)
        pygame.draw.circle(screen, WHITE, (int(sx)-2, int(sy)-2), 2)


def draw_coin(screen, coin, cam, time):
    """Draw spinning coin animation."""
    x = coin.centerx - cam
    y = coin.centery

    # Spin: width oscillates
    spin = abs(math.sin(time * 0.08 + coin.x * 0.01))
    w = max(3, int(10 * spin))

    # Glow
    draw_glow_circle(screen, YELLOW, (int(x), int(y)), 12, 30)

    # Coin body
    pygame.draw.ellipse(screen, (200,160,0), (x - w, y - 10, w*2, 20))
    pygame.draw.ellipse(screen, YELLOW, (x - w + 2, y - 8, w*2 - 4, 16))
    pygame.draw.ellipse(screen, (255,250,180), (x - w + 3, y - 6, w*2 - 6, 12))

    # Inner detail
    if spin > 0.5:
        pygame.draw.circle(screen, (200,160,0), (int(x), int(y)), 4, 1)


def draw_star_pickup(screen, star, cam, time):
    """Draw star pickup with rotating animation and glow."""
    x = star.x - cam
    y = star.y
    cx = x + 12
    cy = y + 12

    # Glow
    draw_glow_circle(screen, YELLOW, (cx, cy), 18, 50)

    # Rotating star
    pts = []
    for i in range(10):
        a = math.pi * i / 5 - math.pi / 2 + time * 0.05
        r = 12 if i % 2 == 0 else 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pygame.draw.polygon(screen, YELLOW, pts)
    pygame.draw.polygon(screen, (255,240,100), pts, 2)

    # Sparkle
    sparkle = (time // 20) % 2 == 0
    if sparkle:
        pygame.draw.circle(screen, WHITE, (cx + 8, cy - 8), 2)


def draw_spring(screen, spring, cam, time):
    """Draw spring with compressed/expanded animation."""
    x = spring.x - cam
    y = spring.y
    w, h = spring.w, spring.h

    # Base
    pygame.draw.rect(screen, (120,120,130), (x, y+h-8, w, 8), border_radius=3)
    pygame.draw.rect(screen, (80,80,90), (x, y+h-8, w, 8), 1, border_radius=3)

    # Coil (zigzag)
    coil_color = (200,200,210)
    pts = []
    for i in range(5):
        cy = y + h - 8 - i * 7
        if i % 2 == 0:
            pts.append((x + 4, cy))
            pts.append((x + w - 4, cy - 3))
        else:
            pts.append((x + w - 4, cy))
            pts.append((x + 4, cy - 3))
    pygame.draw.lines(screen, coil_color, False, pts, 3)

    # Top plate
    pygame.draw.rect(screen, (180,180,190), (x-2, y, w+4, 8), border_radius=3)
    pygame.draw.rect(screen, (220,220,230), (x-2, y, w+4, 3), border_radius=2)

    # Arrow indicator
    pygame.draw.polygon(screen, ORANGE, [(x+w//2, y-8), (x+w//2-6, y-2), (x+w//2+6, y-2)])


def draw_spike(screen, spike, cam, player_gdir):
    """Draw spike with metallic gradient."""
    x = spike.x - cam
    y = spike.y
    w, h = spike.w, spike.h

    if player_gdir > 0:
        pts = [(x, y+h), (x+w//2, y), (x+w, y+h)]
        tip = (x+w//2, y)
    else:
        pts = [(x, y), (x+w//2, y+h), (x+w, y)]
        tip = (x+w//2, y+h)

    # Base
    pygame.draw.polygon(screen, (80,80,90), pts)
    # Highlight side (left)
    pygame.draw.polygon(screen, (140,140,150), [pts[0], tip, (x+w//2, y+h)])
    # Dark side (right)
    pygame.draw.polygon(screen, (50,50,60), [tip, pts[2], (x+w//2, y+h)])
    # Outline
    pygame.draw.polygon(screen, (30,30,40), pts, 1)


def draw_goal_flag(screen, goal, cam, time):
    """Draw goal pole with waving flag."""
    gx = goal.x - cam
    gy = goal.y
    gh = goal.h

    # Pole
    pygame.draw.rect(screen, (180,180,190), (gx, gy, 8, gh))
    pygame.draw.rect(screen, (220,220,230), (gx, gy, 3, gh))

    # Ball on top
    pygame.draw.circle(screen, YELLOW, (gx+4, gy+6), 10)
    pygame.draw.circle(screen, (255,250,180), (gx+2, gy+4), 4)

    # Waving flag
    wave = math.sin(time * 0.1) * 4
    pygame.draw.polygon(screen, RED, [
        (gx+8, gy+14),
        (gx+58, gy+20 + wave),
        (gx+50, gy+28 + wave*0.5),
        (gx+8, gy+36),
    ])
    pygame.draw.polygon(screen, (200,40,40), [
        (gx+8, gy+14),
        (gx+58, gy+20 + wave),
        (gx+54, gy+24 + wave*0.7),
        (gx+8, gy+22),
    ])

    # Checkered pattern on flag
    for i in range(3):
        for j in range(2):
            if (i+j) % 2 == 0:
                fx = gx + 14 + i*12
                fy = gy + 18 + j*6 + wave*0.3
                pygame.draw.rect(screen, WHITE, (fx, fy, 6, 4))


_platform_cache = {}

def _make_platform_texture(w, h, is_ceiling):
    """Pre-render platform texture for performance."""
    key = (w, h, is_ceiling)
    if key in _platform_cache:
        return _platform_cache[key]
    surf = pygame.Surface((w, h))
    if is_ceiling:
        surf.fill((100,110,130))
        pygame.draw.rect(surf, (70,80,100), (0, 0, w, h), 2)
        for i in range(w // 40):
            sx = i*40
            pygame.draw.line(surf, (80,90,110), (sx, 0), (sx, h), 1)
            if i % 2 == 0:
                pygame.draw.line(surf, (80,90,110), (sx, 20), (sx+40, 20), 1)
        pygame.draw.rect(surf, (140,150,170), (0, h-4, w, 4))
    else:
        surf.fill((139,100,60))
        pygame.draw.rect(surf, (110,75,45), (0, 0, w, h), 2)
        pygame.draw.rect(surf, GREEN, (0, 0, w, 10), border_radius=4)
        pygame.draw.rect(surf, (0,120,40), (0, 8, w, 4))
        for i in range(w // 8):
            gx = i*8 + 3
            blade_h = 4 + (i % 3)
            pygame.draw.line(surf, (50,180,70), (gx, 8), (gx+2, 8-blade_h), 2)
        for i in range(w // 20):
            dx = (i*17) % w
            dy = 16 + (i*13) % (h-20)
            pygame.draw.circle(surf, (90,60,35), (dx, dy), 2)
    _platform_cache[key] = surf
    return surf

def draw_platform(screen, p, cam, time):
    """Draw static platform with grass/stone texture (cached)."""
    x = p.x - cam
    y = p.y
    w, h = p.w, p.h
    is_ceiling = y < 100
    surf = _make_platform_texture(w, h, is_ceiling)
    screen.blit(surf, (x, y))


def draw_hud(screen, player, level, level_idx, total_levels, time):
    """Draw glassmorphism HUD with icons."""
    # Panel background
    hud = pygame.Surface((SCREEN_W, 120), pygame.SRCALPHA)
    pygame.draw.rect(hud, (10,10,30,160), (0, 0, SCREEN_W, 120), border_radius=16)
    pygame.draw.rect(hud, (255,255,255,20), (0, 0, SCREEN_W, 120), 1, border_radius=16)
    screen.blit(hud, (0, 0))

    font = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 20)

    # Level name + progress
    title = font.render(f'{level["name"]}', True, WHITE)
    screen.blit(title, (20, 12))
    progress = font_small.render(f'Level {level_idx+1}/{total_levels}', True, (180,180,200))
    screen.blit(progress, (20, 44))

    # Progress bar
    bar_w = 180
    bar_x = 20
    bar_y = 70
    pygame.draw.rect(screen, (40,40,60), (bar_x, bar_y, bar_w, 8), border_radius=4)
    fill = (level_idx + 1) / total_levels
    pygame.draw.rect(screen, CYAN, (bar_x, bar_y, int(bar_w * fill), 8), border_radius=4)

    # Gravity meter
    gtxt = font.render('GRAVITY: DOWN' if player.gdir > 0 else 'GRAVITY: UP', True, GREEN if player.gdir > 0 else ORANGE)
    screen.blit(gtxt, (220, 14))
    # Gravity arrow
    gx = 220
    gy = 52
    if player.gdir > 0:
        pygame.draw.polygon(screen, GREEN, [(gx, gy+14), (gx+14, gy+14), (gx+7, gy+26)])
    else:
        pygame.draw.polygon(screen, ORANGE, [(gx, gy+14), (gx+14, gy+14), (gx+7, gy+2)])

    # Controls hint
    hint = font_small.render('SPACE flip | ←→ move | ↑↓ jump | SHIFT dash', True, (180,180,200))
    screen.blit(hint, (220, 76))

    # Right side: hearts, coins, power-ups
    rx = SCREEN_W - 260

    # Hearts
    for i in range(player.lives):
        hx = rx + i*30
        hy = 20
        pygame.draw.polygon(screen, RED, [
            (hx+8, hy+16), (hx+2, hy+10), (hx+2, hy+5),
            (hx+8, hy+1), (hx+14, hy+5), (hx+14, hy+10),
        ])
        pygame.draw.polygon(screen, (255,120,120), [
            (hx+8, hy+16), (hx+2, hy+10), (hx+2, hy+5),
            (hx+8, hy+1), (hx+14, hy+5), (hx+14, hy+10),
        ], 1)
        pygame.draw.circle(screen, (255,180,180), (hx+5, hy+5), 2)

    # Coins
    coin_icon_x = rx + 100
    coin_icon_y = 24
    pygame.draw.circle(screen, YELLOW, (coin_icon_x, coin_icon_y), 9)
    pygame.draw.circle(screen, (255,240,100), (coin_icon_x, coin_icon_y), 6)
    pygame.draw.circle(screen, (200,150,0), (coin_icon_x, coin_icon_y), 9, 1)
    ctxt = font.render(str(player.coins), True, YELLOW)
    screen.blit(ctxt, (coin_icon_x + 14, coin_icon_y - 12))

    # Star timer
    if player.star > 0:
        stxt = font.render(f'STAR {player.star//60+1}s', True, YELLOW)
        screen.blit(stxt, (rx + 100, 48))

    # Shield
    if player.shield:
        pygame.draw.circle(screen, CYAN, (rx + 110, 78), 10, 2)
        pygame.draw.polygon(screen, CYAN, [
            (rx+110, 72), (rx+116, 76), (rx+116, 80),
            (rx+110, 84), (rx+104, 80), (rx+104, 76),
        ])
        shtxt = font_small.render('SHIELD', True, CYAN)
        screen.blit(shtxt, (rx + 124, 72))
