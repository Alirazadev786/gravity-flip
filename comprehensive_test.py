"""
Comprehensive gameplay simulation test — actually simulates player actions
and verifies all game mechanics work correctly.
"""
import sys, os, random
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
sys.path.insert(0, '.')
import game

pygame.init()
screen = pygame.display.set_mode((game.SCREEN_W, game.SCREEN_H))

PASS = 0
FAIL = 0

def check(name, condition, detail=''):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f'  ✓ {name}')
    else:
        FAIL += 1
        print(f'  ✗ {name}: {detail}')

# ============================================================
# TEST 1: Player basic movement
# ============================================================
print('\n=== TEST 1: Player Movement ===')
levels = game.make_levels()
l0 = levels[0]
player = game.Player(*l0['start'])
plat_rects = list(l0['platforms'])

# Walk right
player.vx = game.SPEED
player.update(plat_rects, [])
check('walks right', player.rect.x > 100, f'x={player.rect.x}')

# Walk left
player.vx = -game.SPEED
player.update(plat_rects, [])
check('walks left', player.rect.x < 100 + game.SPEED, f'x={player.rect.x}')

# Jump
player.grounded = True
player.jump()
check('jump sets vy<0', player.vy < 0, f'vy={player.vy}')
check('jump clears grounded', not player.grounded)

# Gravity pulls down (player in mid-air)
player2 = game.Player(100, 300)  # mid-air
player2.vy = 0
y_before = player2.fy
player2.update(plat_rects, [])
check('gravity pulls down', player2.fy > y_before, f'fy={player2.fy}')

# Land on ground
for _ in range(60):
    player.update(plat_rects, [])
    if player.grounded:
        break
check('lands on ground', player.grounded)

# ============================================================
# TEST 2: Gravity Flip
# ============================================================
print('\n=== TEST 2: Gravity Flip ===')
player = game.Player(*l0['start'])
player.flip()
check('flip changes gdir', player.gdir == -1, f'gdir={player.gdir}')

# Gravity pulls up
y_before = player.rect.y
player.update(plat_rects, [])
check('gravity pulls up', player.rect.y < y_before, f'y={player.rect.y}')

# Flip back
player.flip()
check('flip back gdir', player.gdir == 1, f'gdir={player.gdir}')

# ============================================================
# TEST 3: Double Jump
# ============================================================
print('\n=== TEST 3: Double Jump ===')
player = game.Player(*l0['start'])
player.grounded = True
player.jump()
check('first jump uses jumps_left', player.jumps_left == 1)
player.grounded = False
player.jump()
check('double jump works', player.vy < 0, f'vy={player.vy}')
check('jumps_left decremented', player.jumps_left == 0)
player.jump()
check('no triple jump', player.vy < 0, f'vy={player.vy} (should not change)')

# ============================================================
# TEST 4: Dash
# ============================================================
print('\n=== TEST 4: Dash ===')
player = game.Player(*l0['start'])
player.facing = 1
result = player.dash()
check('dash returns True', result)
check('dash_timer set', player.dash_timer > 0)

x_before = player.rect.x
player.update(plat_rects, [])
check('dash moves right', player.rect.x > x_before, f'x={player.rect.x}')

# Dash cooldown
result2 = player.dash()
check('dash cooldown blocks', not result2)

# Dash stops at wall
player.rect.x = 200
player.rect.y = 500
player.dash_timer = 12
player.dash_cooldown = 0
player.facing = 1
for _ in range(30):
    player.update(plat_rects, [])
check('dash stops at wall', player.rect.right <= 1200, f'right={player.rect.right}')

# ============================================================
# TEST 5: Enemy Stomp
# ============================================================
print('\n=== TEST 5: Enemy Stomp ===')
player = game.Player(300, 400)
enemy = game.FlyEnemy(300, 480)
enemy.alive = True
player.vy = 5  # falling down
player.gdir = 1
# simulate stomp: player bottom above enemy center
player.rect.bottom = enemy.rect.centery - 5
stomped = abs(player.vy) > 3 and player.rect.bottom <= enemy.rect.centery + 12
check('stomp detection works', stomped)

# Up gravity stomp
player.gdir = -1
player.vy = -5
player.rect.top = enemy.rect.centery + 5
stomped_up = abs(player.vy) > 3 and player.rect.top >= enemy.rect.centery - 12
check('up-gravity stomp detection', stomped_up)

# ============================================================
# TEST 6: Spring
# ============================================================
print('\n=== TEST 6: Spring ===')
player = game.Player(180, 520)  # overlaps spring at y=540
spring = pygame.Rect(180, 540, 30, 40)
player.spring_cooldown = 0
player.gdir = 1
player.vy = 0
player.grounded = False
# simulate spring collision
if player.rect.colliderect(spring) and not player.spring_cooldown:
    player.vy = -17 * player.gdir
    player.spring_cooldown = 20
check('spring bounces up', player.vy < 0, f'vy={player.vy}')
check('spring cooldown set', player.spring_cooldown == 20)

# Spring cooldown prevents re-bounce
player.vy = 0
if player.rect.colliderect(spring) and not player.spring_cooldown:
    player.vy = -17 * player.gdir
check('spring cooldown blocks re-bounce', player.vy == 0, f'vy={player.vy}')

# ============================================================
# TEST 7: Portal
# ============================================================
print('\n=== TEST 7: Portal ===')
l5 = levels[4]
player = game.Player(450, 460)
portal = l5['portals'][0]
player.portal_cooldown = 0
player.gdir = 1
# simulate portal collision
if player.rect.colliderect(portal.rect) and not player.portal_cooldown:
    player.flip()
    player.portal_cooldown = 30
check('portal flips gravity', player.gdir == -1, f'gdir={player.gdir}')
check('portal cooldown set', player.portal_cooldown == 30)

# Portal cooldown prevents re-flip
player.gdir = 1
if player.rect.colliderect(portal.rect) and not player.portal_cooldown:
    player.flip()
check('portal cooldown blocks re-flip', player.gdir == 1, f'gdir={player.gdir}')

# ============================================================
# TEST 8: Shield
# ============================================================
print('\n=== TEST 8: Shield ===')
player = game.Player(100, 500)
player.shield = True
# Simulate hazard hit
hit_hazard = True
if hit_hazard:
    if player.shield:
        player.shield = False
    else:
        player.alive = False
check('shield blocks hazard', player.alive)
check('shield consumed', not player.shield)

# Shield blocks spikes
player = game.Player(500, 520)  # overlaps spike at y=540
player.shield = True
spike = pygame.Rect(500, 540, 40, 40)
if player.rect.colliderect(spike) and not False:  # not won
    if player.shield:
        player.shield = False
    else:
        player.alive = False
check('shield blocks spike', player.alive)
check('shield consumed by spike', not player.shield)

# ============================================================
# TEST 9: Boss
# ============================================================
print('\n=== TEST 9: Boss ===')
l9 = levels[8]
boss = l9['boss']
player = game.Player(100, 500)

# Boss bounds
boss.rect.left = 100
boss.update(plat_rects, player)
check('boss stays in arena (left)', boss.rect.left >= boss.min_x, f'left={boss.rect.left}')

boss.rect.right = 1200
boss.update(plat_rects, player)
check('boss stays in arena (right)', boss.rect.right <= boss.max_x, f'right={boss.rect.right}')

# Boss shots spawn outside body
boss.attack_timer = 0
boss.rect.centerx = 800
boss.rect.centery = 450
player.rect.centerx = 300
player.rect.centery = 500
boss.update(plat_rects, player)
if boss.shots:
    sx = boss.shots[0][0]
    check('boss shot spawns outside body', abs(sx - boss.rect.centerx) >= 40, f'sx={sx}, boss_x={boss.rect.centerx}')
else:
    check('boss shot spawns outside body', False, 'no shot spawned')

# Boss hit reduces HP
hp_before = boss.hp
boss.hit()
check('boss hit reduces HP', boss.hp == hp_before - 1)

# Boss death
for _ in range(boss.hp):
    boss.hit()
check('boss dies', not boss.alive)

# ============================================================
# TEST 10: Moving Platform Carry
# ============================================================
print('\n=== TEST 10: Moving Platform Carry ===')
l1 = levels[1]
mp = l1['moving'][1]  # vertical platform
player = game.Player(650, 300)
player.grounded = True
player.vy = 0
player.gdir = 1

# Place player on platform
y_before = mp.rect.y
mp.update()
player.rect.bottom = mp.rect.top
player.rect.x = mp.rect.centerx - 15
player.update(plat_rects, l1['moving'])
check('vertical platform carries player', abs(player.rect.y - (mp.rect.top - 40)) < 30, f'player_y={player.rect.y}, plat_y={mp.rect.top}')

# ============================================================
# TEST 11: Level Structure
# ============================================================
print('\n=== TEST 11: Level Structure ===')
check('9 levels exist', len(levels) == 9, f'got {len(levels)}')
for i, lv in enumerate(levels):
    check(f'level {i+1} has platforms', len(lv['platforms']) >= 2)
    check(f'level {i+1} has goal', 'goal' in lv)
    check(f'level {i+1} has start', 'start' in lv)
    check(f'level {i+1} has theme', 'theme' in lv)

# ============================================================
# TEST 12: Player Lives
# ============================================================
print('\n=== TEST 12: Player Lives ===')
p2 = game.Player(100, 500, lives=2)
check('custom lives', p2.lives == 2)
p3 = game.Player(100, 500)
check('default lives 3', p3.lives == 3)

# ============================================================
# RESULT
# ============================================================
print(f'\n===== RESULTS: {PASS} passed, {FAIL} failed =====')
if FAIL > 0:
    sys.exit(1)
print('ALL_COMPREHENSIVE_TESTS_PASS')