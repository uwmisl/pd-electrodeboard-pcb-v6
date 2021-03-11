#%%
import itertools
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

from dmfwizard.types import BoardDesign, Grid
from dmfwizard.io import load_peripheral
from dmfwizard.construct import Constructor, reduce_board_to_electrodes, crenellate_grid, offset_polygon
from dmfwizard.crenellation import crenellate_electrodes
from dmfwizard.kicad import save_board

BASE_PITCH = 1.25
SMALL_PITCH = 2 * BASE_PITCH
LARGE_PITCH = 3 * BASE_PITCH
MARGIN = 0.15
NUM_DIGITS = 2
THETA = 30

LARGE_GRID_WIDTH = 16
LARGE_GRID_HEIGHT = 7
LARGE_ORIGIN = (75.0/2 - LARGE_GRID_WIDTH*LARGE_PITCH/2, 4.5)
SMALL_ORIGIN = (
    LARGE_ORIGIN[0] - LARGE_PITCH + 0.5 * (LARGE_PITCH - SMALL_PITCH),
    LARGE_ORIGIN[1] + LARGE_PITCH * LARGE_GRID_HEIGHT)

# Create board and grids
board = BoardDesign()
large_grid = Grid(LARGE_ORIGIN, (LARGE_GRID_WIDTH, LARGE_GRID_HEIGHT), LARGE_PITCH)
small_grid = Grid(SMALL_ORIGIN, (25, 4), SMALL_PITCH)
board.grids.append(large_grid)
board.grids.append(small_grid)
construct = Constructor()

# Define small grid electrodes
construct.fill_horiz(small_grid, (2, 1), 21)
construct.fill(small_grid, (6, 0))
construct.fill(small_grid, (12, 0))
construct.fill(small_grid, (18, 0))
construct.fill_vert(small_grid, (2, 1), 2)
construct.fill_vert(small_grid, (7, 1), 2)
construct.fill_vert(small_grid, (12, 1), 2)
construct.fill_vert(small_grid, (17, 1), 2)
construct.fill_vert(small_grid, (22, 1), 2)

# Define large grid electrodes
construct.fill_rect(large_grid, (3, 1), (10, 3))
construct.fill_rect(large_grid, (3, 3), (2, 4))
construct.fill_rect(large_grid, (7, 3), (2, 4))
construct.fill_rect(large_grid, (11, 3), (2, 4))

# Create interwoven fingers between neighboring electrodes
crenellate_grid(large_grid, NUM_DIGITS, THETA, MARGIN*LARGE_PITCH)
crenellate_grid(small_grid, NUM_DIGITS, THETA, MARGIN*SMALL_PITCH)

# Manually crenellate the interfaces between large grid and small grid
crenellate_electrodes(
    large_grid.electrodes[(3, 6)],
    small_grid.electrodes[(6, 0)],
    NUM_DIGITS, THETA, MARGIN*SMALL_PITCH)
crenellate_electrodes(
    large_grid.electrodes[(7, 6)],
    small_grid.electrodes[(12, 0)],
    NUM_DIGITS, THETA, MARGIN*SMALL_PITCH)
crenellate_electrodes(
    large_grid.electrodes[(11, 6)],
    small_grid.electrodes[(18, 0)],
    NUM_DIGITS, THETA, MARGIN*SMALL_PITCH)


# Create reservoirs
small_reservoir_origin = np.add(SMALL_ORIGIN, (0.5 * SMALL_PITCH, 0.0))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/chevron1_reservoir.json'),
    np.add(small_reservoir_origin, np.multiply((2, 3), SMALL_PITCH)),
    np.deg2rad(0))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/chevron1_reservoir.json'),
    np.add(small_reservoir_origin, np.multiply((7, 3), SMALL_PITCH)),
    np.deg2rad(0))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/chevron1_reservoir.json'),
    np.add(small_reservoir_origin, np.multiply((12, 3), SMALL_PITCH)),
    np.deg2rad(0))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/chevron1_reservoir.json'),
    np.add(small_reservoir_origin, np.multiply((17, 3), SMALL_PITCH)),
    np.deg2rad(0))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/vortex1_reservoir.json'),
    np.add(small_reservoir_origin, np.multiply((22, 3), SMALL_PITCH)),
    np.deg2rad(0))

# Crenellate reservoir outputs
crenellate_electrodes(
    small_grid.electrodes[(2, 2)],
    board.peripherals[0].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)
crenellate_electrodes(
    small_grid.electrodes[(7, 2)],
    board.peripherals[1].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)
crenellate_electrodes(
    small_grid.electrodes[(12, 2)],
    board.peripherals[2].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)
crenellate_electrodes(
    small_grid.electrodes[(17, 2)],
    board.peripherals[3].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)
crenellate_electrodes(
    small_grid.electrodes[(22, 2)],
    board.peripherals[4].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)

# Create active input locations
construct.add_peripheral(
    board,
    load_peripheral('peripherals/dispense1.json'),
    np.add(np.add(LARGE_ORIGIN, (0, 0.5*LARGE_PITCH)), np.multiply((3, 1), LARGE_PITCH)),
    np.deg2rad(90))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/dispense1.json'),
    np.add(np.add(LARGE_ORIGIN, (0, 0.5*LARGE_PITCH)), np.multiply((3, 3), LARGE_PITCH)),
    np.deg2rad(90))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/dispense1.json'),
    np.add(np.add(LARGE_ORIGIN, (0, 0.5*LARGE_PITCH)), np.multiply((13, 1), LARGE_PITCH)),
    np.deg2rad(270))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/dispense1.json'),
    np.add(np.add(LARGE_ORIGIN, (0, 0.5*LARGE_PITCH)), np.multiply((13, 3), LARGE_PITCH)),
    np.deg2rad(270))
# Crenellate active inputs
crenellate_electrodes(
    large_grid.electrodes[(3, 1)],
    board.peripherals[5].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)
crenellate_electrodes(
    large_grid.electrodes[(3, 3)],
    board.peripherals[6].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)
crenellate_electrodes(
    large_grid.electrodes[(12, 1)],
    board.peripherals[7].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)
crenellate_electrodes(
    large_grid.electrodes[(12, 3)],
    board.peripherals[8].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)

electrodes = reduce_board_to_electrodes(board)

fig, ax = plt.subplots(figsize=(10, 10))
for e in electrodes:
    ax.add_patch(patches.Polygon(offset_polygon(e.offset_points(), -0.1), fill=False))

# Add 50x75mm border for reference
ax.add_patch(patches.Rectangle((0, 0), 75, 50, fill=False, color='green'))
# Add cover margins
ax.add_patch(patches.Rectangle((2.5, 4.0), 75-5, 50, fill=False, color='cyan'))
# Add grids for reference
def draw_grid(ax, grid):
    for col, row in itertools.product(range(grid.size[0]), range(grid.size[1])):
        ax.add_patch(patches.Rectangle(
            (grid.pitch * col + grid.origin[0], grid.pitch * row + grid.origin[1]),
            grid.pitch,
            grid.pitch,
            fill=False,
            color='yellow')
        )
draw_grid(ax, large_grid)
draw_grid(ax, small_grid)

ax.autoscale()
ax.axis('square')
ax.invert_yaxis()
plt.show()

# %%
CLEARANCE = 0.11
BOARD_ORIGIN = [162.5, 62.25]
projdir = path = os.path.abspath(os.path.dirname(__file__))
save_board(board, BOARD_ORIGIN, projdir, CLEARANCE)
# %%
