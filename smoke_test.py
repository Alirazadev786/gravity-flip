import sys, os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
sys.path.insert(0, '.')
import game

# verify new classes
assert hasattr(game, 'PortalFlip'), 'PortalFlip missing'
assert hasattr(game, 'PhasePlatform'), 'PhasePlatform missing'
assert hasattr(game, 'Boss'), 'Boss missing'
assert hasattr(game, 'Shield'), 'Shield missing'

levels = game.make_levels()
assert len(levels) == 9, f'expected 9 levels, got {len(levels)}'
l5 = levels[4]
assert l5['name'] == 'Phase Factory', l5['name']
assert len(l5.get('portals', [])) == 2
assert len(l5.get('phase', [])) == 2

# verify new levels
l6 = levels[5]
assert l6['name'] == 'Ice World', l6['name']
assert len(l6.get('shields', [])) == 1

l7 = levels[6]
assert l7['name'] == 'Lava World', l7['name']
assert len(l7.get('shields', [])) == 1

l8 = levels[7]
assert l8['name'] == 'Space World', l8['name']
assert len(l8.get('shields', [])) == 1
assert len(l8.get('portals', [])) == 3

l9 = levels[8]
assert l9['name'] == 'Boss Arena', l9['name']
assert 'boss' in l9, 'boss missing in level 9'
assert l9['boss'].hp == 10

# full headless run
import game as g
g.run_game(True)
print('SMOKE_ALL_OK')
