#%%
import itertools
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

from dmfwizard.types import BoardDesign, Grid, Peripheral
from dmfwizard.io import load_peripheral
from dmfwizard.construct import Constructor, reduce_board_to_electrodes, crenellate_grid, offset_polygon
from dmfwizard.crenellation import crenellate_electrodes
from dmfwizard.kicad import save_board

# Define pitch of the electrode grids
BASE_PITCH = 1.25
SMALL_PITCH = 2 * BASE_PITCH
LARGE_PITCH = 3 * BASE_PITCH
# Define shape of the electrode crenellations
MARGIN = 0.15
NUM_DIGITS = 5
THETA = 30
# Copper-to-copper clearance and origin within the kicad PCB
CLEARANCE = 0.11
BOARD_ORIGIN = [162.5, 62.25]

# Define position of the grids
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

# Create reservoirs
small_reservoir_origin = np.add(SMALL_ORIGIN, (0.5 * SMALL_PITCH, 0.0))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/four_tier_reservoir.json'),
    np.add(small_reservoir_origin, np.multiply((2, 3), SMALL_PITCH)).tolist(),
    np.deg2rad(0))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/four_tier_reservoir.json'),
    np.add(small_reservoir_origin, np.multiply((7, 3), SMALL_PITCH)).tolist(),
    np.deg2rad(0))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/four_tier_reservoir.json'),
    np.add(small_reservoir_origin, np.multiply((12, 3), SMALL_PITCH)).tolist(),
    np.deg2rad(0))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/four_tier_reservoir.json'),
    np.add(small_reservoir_origin, np.multiply((17, 3), SMALL_PITCH)).tolist(),
    np.deg2rad(0))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/vortex2_reservoir.json'),
    np.add(small_reservoir_origin, np.multiply((22, 3), SMALL_PITCH)).tolist(),
    np.deg2rad(0))

# Create active input locations
construct.add_peripheral(
    board,
    load_peripheral('peripherals/dispense2.json'),
    np.add(np.add(LARGE_ORIGIN, (0, 0.5*LARGE_PITCH)), np.multiply((3, 1), LARGE_PITCH)).tolist(),
    np.deg2rad(90))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/dispense2.json'),
    np.add(np.add(LARGE_ORIGIN, (0, 0.5*LARGE_PITCH)), np.multiply((3, 3), LARGE_PITCH)).tolist(),
    np.deg2rad(90))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/dispense2.json'),
    np.add(np.add(LARGE_ORIGIN, (0, 0.5*LARGE_PITCH)), np.multiply((13, 1), LARGE_PITCH)).tolist(),
    np.deg2rad(270))
construct.add_peripheral(
    board,
    load_peripheral('peripherals/dispense2.json'),
    np.add(np.add(LARGE_ORIGIN, (0, 0.5*LARGE_PITCH)), np.multiply((13, 3), LARGE_PITCH)).tolist(),
    np.deg2rad(270))

# Create copy of the board to crenellate. We will use the un-crenellated version for
# generating the board definition file.
crenellated_board = board.copy()

# Create interwoven fingers between neighboring electrodes
crenellate_grid(crenellated_board.grids[0], NUM_DIGITS, THETA, MARGIN*LARGE_PITCH)
crenellate_grid(crenellated_board.grids[1], NUM_DIGITS, THETA, MARGIN*SMALL_PITCH)

# Manually crenellate the interfaces between large grid and small grid
crenellate_electrodes(
    crenellated_board.grids[0].electrodes[(3, 6)],
    crenellated_board.grids[1].electrodes[(6, 0)],
    NUM_DIGITS, THETA, MARGIN*SMALL_PITCH)
crenellate_electrodes(
    crenellated_board.grids[0].electrodes[(7, 6)],
    crenellated_board.grids[1].electrodes[(12, 0)],
    NUM_DIGITS, THETA, MARGIN*SMALL_PITCH)
crenellate_electrodes(
    crenellated_board.grids[0].electrodes[(11, 6)],
    crenellated_board.grids[1].electrodes[(18, 0)],
    NUM_DIGITS, THETA, MARGIN*SMALL_PITCH)

# Crenellate reservoir outputs
crenellate_electrodes(
    crenellated_board.grids[1].electrodes[(2, 2)],
    crenellated_board.peripherals[0].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)
crenellate_electrodes(
    crenellated_board.grids[1].electrodes[(7, 2)],
    crenellated_board.peripherals[1].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)
crenellate_electrodes(
    crenellated_board.grids[1].electrodes[(12, 2)],
    crenellated_board.peripherals[2].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)
crenellate_electrodes(
    crenellated_board.grids[1].electrodes[(17, 2)],
    crenellated_board.peripherals[3].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)
crenellate_electrodes(
    crenellated_board.grids[1].electrodes[(22, 2)],
    crenellated_board.peripherals[4].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)

# Crenellate active inputs
crenellate_electrodes(
    crenellated_board.grids[0].electrodes[(3, 1)],
    crenellated_board.peripherals[5].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)
crenellate_electrodes(
    crenellated_board.grids[0].electrodes[(3, 3)],
    crenellated_board.peripherals[6].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)
crenellate_electrodes(
    crenellated_board.grids[0].electrodes[(12, 1)],
    crenellated_board.peripherals[7].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)
crenellate_electrodes(
    crenellated_board.grids[0].electrodes[(12, 3)],
    crenellated_board.peripherals[8].electrode('A'),
    NUM_DIGITS,
    THETA,
    MARGIN*SMALL_PITCH
)

# Get list of all electrodes with polygons in global board coordinates
electrodes = reduce_board_to_electrodes(board)


fig, ax = plt.subplots(figsize=(10, 10))
# Add grid outlines for reference
def draw_grid(ax, grid):
    for col, row in itertools.product(range(grid.size[0]), range(grid.size[1])):
        ax.add_patch(patches.Rectangle(
            (grid.pitch * col + grid.origin[0], grid.pitch * row + grid.origin[1]),
            grid.pitch,
            grid.pitch,
            fill=False,
            color='yellow')
        )
draw_grid(ax, board.grids[0])
draw_grid(ax, board.grids[1])
for e in electrodes:
    ax.add_patch(patches.Polygon(offset_polygon(e.offset_points(), -0.1), fill=False))

# Add 50x75mm border for reference
ax.add_patch(patches.Rectangle((0, 0), 75, 50, fill=False, color='green'))
# Add cover margins that shows the exposed area of the top plate
ax.add_patch(patches.Rectangle((2.5, 4.0), 75-5, 50, fill=False, color='cyan'))
ax.autoscale()
ax.axis('square')
ax.invert_yaxis()
plt.show()

# %%
# Write KiCad footprints and layout.yml file for kicad
projdir = path = os.path.abspath(os.path.dirname(__file__))
save_board(crenellated_board, BOARD_ORIGIN, projdir, CLEARANCE)
# %%
# Generate the 'layout' property of a board definition file

# First, get electrode refdes to pin mapping from pcb file, based on net names
# Then, map the board grids and peripherals to the board definition format. 
# Finally, encode to JSON using the custom encoder for more readable output.

from dmfwizard.kicad import extract_electrode_nets
import json
import re

class CompactJSONEncoder(json.JSONEncoder):
    """A JSON Encoder that puts small lists on single lines."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indentation_level = 0

    def encode(self, o):
        """Encode JSON object *o* with respect to single line lists."""

        if isinstance(o, (list, tuple)):
            if self._is_single_line_list(o):
                return "[" + ", ".join(json.dumps(el) for el in o) + "]"
            else:
                self.indentation_level += 1
                output = [self.indent_str + self.encode(el) for el in o]
                self.indentation_level -= 1
                return "[\n" + ",\n".join(output) + "\n" + self.indent_str + "]"

        elif isinstance(o, dict):
            self.indentation_level += 1
            output = [self.indent_str + f"{json.dumps(k)}: {self.encode(v)}" for k, v in o.items()]
            self.indentation_level -= 1
            return "{\n" + ",\n".join(output) + "\n" + self.indent_str + "}"

        else:
            return json.dumps(o)

    def _is_single_line_list(self, o):
        if isinstance(o, (list, tuple)):
            return not any(isinstance(el, (list, tuple, dict)) for el in o)\
                   and len(o) <= 2\
                   and len(str(o)) - 2 <= 60

    @property
    def indent_str(self) -> str:
        return " " * self.indentation_level

net_table = extract_electrode_nets('PD_ElectrodeBoard_v6.kicad_pcb')

print(net_table)

pin_table = {}
for refdes, net_name in net_table.items():
    match = re.match('/P(\d+)', net_name)
    if match is None:
        print(f"Failed to match pin number from net '{net_name}'")
    else:
        pin = int(match.group(1))
        pin_table[refdes] = pin

layout = {}

# Create empty
def create_grid_dict(grid: Grid):
    ret = {}
    ret['origin'] = grid.origin
    ret['pitch'] = grid.pitch
    ret['pins'] = [[None] * grid.width for _ in range(grid.height)]
    for pos, electrode in grid.electrodes.items():
        ret['pins'][pos[1]][pos[0]] = pin_table[f'E{electrode.refdes}']
    return ret

def create_periph_dict(periph: Peripheral):
    return {
        'class': periph.peripheral_class,
        'type': periph.peripheral_type,
        'id': periph.id,
        'origin': periph.global_origin(),
        'rotation': np.rad2deg(periph.rotation),
        'electrodes': [
            {
                'id': e['id'],
                'pin': pin_table[f"E{e['electrode'].refdes}"],
                'polygon': e['electrode'].points,
                'origin': e['electrode'].origin,
            }
            for e in periph.electrodes
        ],
    }

grid0 = create_grid_dict(board.grids[0])
grid1 = create_grid_dict(board.grids[1])
periphs = [create_periph_dict(p) for p in board.peripherals]
layout = {
    "layout": {
        'grids': [grid0, grid1],
        'peripherals': periphs,
    }
}

with open('electrode_board_layout.json', 'w') as f:
    f.write(json.dumps(layout, cls=CompactJSONEncoder))



# %%
