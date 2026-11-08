import sys, os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
sys.path.insert(0, '.')
import game
import graphics

pygame.init()
screen = pygame.display.set_mode((900, 650))

# Test all draw functions with dummy objects
player = game.Player(100, 500)
player.shield = True
player.star = 100
player.dash_timer = 5
player.facing = 1
graphics.draw_player(screen, player, 0, 0)
print('DRAW_PLAYER_OK')

enemy = game.FlyEnemy(200, 300)
graphics.draw_fly_enemy(screen, enemy, 0, 100)
print('DRAW_FLY_ENEMY_OK')

saw = game.Saw(300, 300)
graphics.draw_saw(screen, saw, 0, 100)
print('DRAW_SAW_OK')

mp = game.MovingPlatform(pygame.Rect(100, 400, 100, 30), 'x', 100, 2)
graphics.draw_moving_platform(screen, mp, 0, 100)
print('DRAW_MOVING_PLATFORM_OK')

portal = game.PortalFlip(400, 300)
graphics.draw_portal(screen, portal, 0, 100)
print('DRAW_PORTAL_OK')

phase = game.PhasePlatform(pygame.Rect(200, 300, 120, 30))
graphics.draw_phase_platform(screen, phase, 0, 100)
print('DRAW_PHASE_PLATFORM_OK')

shield = game.Shield(500, 300)
graphics.draw_shield_pickup(screen, shield, 0, 100)
print('DRAW_SHIELD_PICKUP_OK')

boss = game.Boss(600, 300)
boss.shots.append([500, 400, 0, 0])
graphics.draw_boss(screen, boss, 0, 100)
print('DRAW_BOSS_OK')

coin = pygame.Rect(300, 300, 20, 20)
graphics.draw_coin(screen, coin, 0, 100)
print('DRAW_COIN_OK')

star_rect = pygame.Rect(400, 300, 20, 20)
graphics.draw_star_pickup(screen, star_rect, 0, 100)
print('DRAW_STAR_OK')

spring = pygame.Rect(500, 300, 30, 40)
graphics.draw_spring(screen, spring, 0, 100)
print('DRAW_SPRING_OK')

spike = pygame.Rect(600, 300, 40, 40)
graphics.draw_spike(screen, spike, 0, 1)
graphics.draw_spike(screen, spike, 0, -1)
print('DRAW_SPIKE_OK')

goal = pygame.Rect(700, 100, 24, 500)
graphics.draw_goal_flag(screen, goal, 0, 100)
print('DRAW_GOAL_FLAG_OK')

platform = pygame.Rect(-300, 580, 1500, 40)
graphics.draw_platform(screen, platform, 0, 100)
ceiling = pygame.Rect(-300, 30, 1500, 40)
graphics.draw_platform(screen, ceiling, 0, 100)
print('DRAW_PLATFORM_OK')

level = game.make_levels()[0]
graphics.draw_hud(screen, player, level, 0, 9, 100)
print('DRAW_HUD_OK')

print('ALL_GRAPHICS_TESTS_PASS')