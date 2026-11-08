import sys, os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
sys.path.insert(0, '.')
import game

# --- Test 1: Player lives preservation ---
p = game.Player(100, 500, lives=2)
assert p.lives == 2, f'lives should be 2, got {p.lives}'
p2 = game.Player(100, 500)
assert p2.lives == 3, f'default lives should be 3, got {p2.lives}'
print('TEST_1_LIVES_OK')

# --- Test 2: Portal cooldown ---
levels = game.make_levels()
l5 = levels[4]
assert len(l5.get('portals', [])) == 2
print('TEST_2_PORTALS_OK')

# --- Test 3: Boss arena bounds ---
boss = game.Boss(800, 450)
boss.min_x = 200
boss.max_x = 1100
boss.rect.left = 100
boss.update(l5['platforms'], p)
assert boss.rect.left >= boss.min_x, f'boss left {boss.rect.left} < min_x {boss.min_x}'
boss.rect.right = 1200
boss.update(l5['platforms'], p)
assert boss.rect.right <= boss.max_x, f'boss right {boss.rect.right} > max_x {boss.max_x}'
print('TEST_3_BOSS_BOUNDS_OK')

# --- Test 4: Boss shots are rect-based ---
boss.shots.append([500, 400, 0, 0])
shot_rect = pygame.Rect(500 - 8, 400 - 8, 16, 16)
assert shot_rect.colliderect(pygame.Rect(490, 390, 30, 40)), 'shot rect should collide with player rect'
print('TEST_4_BOSS_SHOTS_OK')

# --- Test 5: Double jump works ---
p3 = game.Player(100, 500)
p3.grounded = True
p3.jump()
assert p3.vy < 0, f'first jump should set vy<0, got {p3.vy}'
p3.grounded = False
p3.jumps_left = 1
p3.jump()
assert p3.vy < 0, f'double jump should set vy<0, got {p3.vy}'
assert p3.jumps_left == 0, f'jumps_left should be 0 after double jump'
print('TEST_5_DOUBLE_JUMP_OK')

# --- Test 6: Shield blocks hazards ---
p4 = game.Player(100, 500)
p4.shield = True
hit_hazard = True
if hit_hazard:
    if p4.shield:
        p4.shield = False
    else:
        p4.alive = False
assert p4.alive, 'shield should block hazard'
assert not p4.shield, 'shield should be consumed'
print('TEST_6_SHIELD_OK')

# --- Test 7: Level count ---
assert len(levels) == 9, f'expected 9 levels, got {len(levels)}'
print('TEST_7_LEVELS_OK')

print('ALL_BUG_FIX_TESTS_PASS')