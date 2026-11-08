import sys, os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
sys.path.insert(0, '.')
import game

# verify new classes
assert hasattr(game, 'PortalFlip'), 'PortalFlip missing'
assert hasattr(game, 'PhasePlatform'), 'PhasePlatform missing'

levels = game.make_levels()
assert len(levels) == 5, f'expected 5 levels, got {len(levels)}'
l5 = levels[-1]
assert l5['name'] == 'Phase Factory', l5['name']
assert len(l5.get('portals', [])) == 2
assert len(l5.get('phase', [])) == 2

# full headless run
game.run_game(True)
print('SMOKE_ALL_OK')
