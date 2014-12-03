#!/usr/bin/env python

from sys import argv
from mymc import Minecraft, Block
from mymc import AIR, CHEST, COBBLESTONE, DIRT, DOOR_WOOD, GRASS, FLOWER_YELLOW, LADDER, LEAVES, MOSS_STONE, \
    STONE_BRICK, WATER, WOOD_PLANKS, STONE_SLAB
from maze import Maze, NORTH, SOUTH, EAST, WEST
from time import sleep


class Kingdom(object):

    """Responsible for building a kingdom."""

    def __init__(self, mc):
        self.mc = mc
        self.landscape = Landscape(mc)
        self.castle = Castle(mc)
        self.labyrinth = Labyrinth(mc)
        self.build_order = [self.landscape, self.labyrinth, self.castle]

    def build(self):
        for obj in self.build_order:
            obj.build()


class Landscape(object):

    """Responsible for building a landscape."""

    def __init__(self, mc):
        self.mc = mc

    def build(self):

        min_x, max_x = self.mc.min_x, self.mc.max_x
        min_y, max_y = self.mc.min_y, self.mc.max_y
        min_z, max_z = self.mc.min_z, self.mc.max_z

        # Don't forget the zero block! 1 - -1 == 2, but it is 3 blocks!
        x_width = max_x - min_x + 1
        z_width = max_z - min_z + 1

        # Set upper half of world to air
        self.mc.make_cube(min_x, 0, min_z, x_width, max_y, z_width, AIR)

        # Carpet world with dirt and a layer of grass
        self.mc.make_cube(min_x, -1, min_z, x_width, 1, z_width, GRASS)


class Castle(object):

    """Responsible for building a castle with a moat."""

    def __init__(self, mc):
        self.mc = mc
        self.island_width = 23
        self.moat_width, self.moat_depth = 32, 10
        self.keep_width = 5
        self.keep_levels = 4

    def build(self):
        self.build_grounds()
        self.build_walls()
        self.build_streets()
        self.build_keep()
        self.build_gateways()
        self.build_bridge()

    def build_bridge(self):
        self.mc.make_cube(self.island_width - 1, -1, -1,
                          x_dim=self.moat_width - self.island_width + 1, z_dim=3, material=WOOD_PLANKS)

    def build_gateways(self):
        self.mc.make_cube(self.island_width - 10, 0, -1,
                          x_dim=self.island_width - 2, y_dim=3, z_dim=3, material=AIR)

    def build_grounds(self):

        ctr = self.mc.center

        # Create moat
        self.mc.make_cube(ctr[0] - self.moat_width + 1, -self.moat_depth, ctr[2] - self.moat_width + 1,
                          self.moat_width * 2, self.mc.max_y, self.moat_width * 2, AIR)
        self.mc.make_cube(ctr[0] - self.moat_width + 1, -self.moat_depth, ctr[2] - self.moat_width + 1,
                          self.moat_width * 2, self.moat_depth, self.moat_width * 2, WATER)

        # Replace the ground under the castle
        self.mc.make_cube(ctr[0] - self.island_width + 1, -self.moat_depth - 1, ctr[2] - self.island_width + 1,
                          self.island_width * 2 + 1, self.moat_depth, self.island_width * 2 + 1, DIRT)
        self.mc.make_cube(ctr[0] - self.island_width + 1, -1, ctr[2] - self.island_width + 1,
                          self.island_width * 2 + 1, 1, self.island_width * 2 + 1, GRASS)

        # Plant flowers around the border of the island
        self.mc.make_cube(-self.island_width, 0, -self.island_width,
                          self.island_width * 2 + 1, 1, self.island_width * 2 + 1, FLOWER_YELLOW)

    def build_walls(self):
        self._build_walls(21, 6)
        self._build_walls(13, 6)

    def build_streets(self):
        materials = [MOSS_STONE, COBBLESTONE]
        for idx, dim in enumerate([2, 5, 8, 13, 16, 18]):
            self.mc.make_cube(-self.island_width + dim, -1, -self.island_width + dim,
                              x_dim=(self.island_width - dim) * 2 + 1, z_dim=(self.island_width - dim) * 2 + 1,
                              material=materials[idx % 2])
        self.mc.make_cube(self.keep_width + 3, -1, -1, x_dim=self.island_width - 9, z_dim=3, material=COBBLESTONE)
        self.mc.make_cube(0, -1, self.keep_width + 1, z_dim=2, material=COBBLESTONE)

    def build_keep(self):

        size = self.keep_width
        height = (self.keep_levels * 5) + 5

        self._build_walls(self.keep_width, height)

        # Floors
        for level in range(1, self.keep_levels + 1):
            self.mc.make_cube(-size + 1, level * 5, -size + 1, size * 2 - 1, 1, size * 2 - 1, STONE_SLAB.withData(2))

        # Patch up ladder (the floors cut into it)
        self.mc.make_cube(-size + 1, 0, 0, 1, height, 1, LADDER.withData(5))

        # Windows
        for level in range(1, self.keep_levels + 1):
            self._make_windows(0, level * 5 + 1, size, "N")
            self._make_windows(0, level * 5 + 1, -size, "S")
            self._make_windows(-size, level * 5 + 1, 0, "W")
            self._make_windows(size, level * 5 + 1, 0, "E")

        # Door
        self.mc.make_cube(0, 0, size, material=DOOR_WOOD.withData(3))
        self.mc.make_cube(0, 1, size, material=DOOR_WOOD.withData(8))

        # Treasure
        self.mc.make_cube(self.keep_width - 1, self.keep_levels * 5, 0, material=WOOD_PLANKS)
        self.mc.make_cube(self.keep_width - 1, self.keep_levels * 5 + 1, 0, material=CHEST.withData(4))

    def _make_windows(self, x, y, z, direction):

        if direction == "N" or direction == "S":
            z1, z2 = z, z
            x1, x2 = x - 2, x + 2

        if direction == "E" or direction == "W":
            x1, x2 = x, x
            z1, z2 = z - 2, z + 2

        self.mc.make_cube(x1, y, z1, 1, 2, 1, AIR)
        self.mc.make_cube(x2, y, z2, 1, 2, 1, AIR)

        win_dirs = {'N': 3, 'S': 2, 'E': 1, 'W': 0}
        sill = Block(109, win_dirs[direction])

        self.mc.make_cube(x1, y - 1, z1, material=sill)
        self.mc.make_cube(x2, y - 1, z2, material=sill)

    def _build_walls(self, size, height, material=STONE_BRICK):

        """Creates four walls with battlements, walkways and ladders."""

        # Walls
        self.mc.make_cube(-size, 0, -size, size * 2 + 1, height + 1, size * 2 + 1, material)
        self.mc.make_cube(-size + 1, 0, -size + 1, size * 2 + 1 - 2, height + 1, size * 2 + 1 - 2, AIR)

        # Carve out battlements
        for x in range(1, 2 * size, 2):
            self.mc.make_cube(-size + x, height, -size, 1, 1, size * 2 + 1, AIR)
            self.mc.make_cube(-size, height, -size + x, size * 2 + 1, 1, 1, AIR)

        # Battlement walks
        self.mc.make_cube(-size + 1, height - 1, -size + 1, size * 2 - 1, 1, size * 2 - 1, STONE_SLAB.withData(2), False)

        # Battlement walk ladder
        self.mc.make_cube(-size + 1, 0, 0, 1, height, 1, LADDER.withData(5))


class Labyrinth(object):

    """Responsible for building a labyrinth."""

    def __init__(self, mc):
        self.mc = mc
        self.material = LEAVES

    def build(self):

        material = self.material
        min_x, max_x = self.mc.min_x, self.mc.max_x
        min_z, max_z = self.mc.min_z, self.mc.max_z

        # Don't forget the zero block! 1 - -1 == 2, but it is 3 blocks!
        x_width = max_x - min_x + 1
        z_width = max_z - min_z + 1

        c_dim, c_height = 6, 3  # in world block units

        # in labyrinth cell units (remember walls overlap, need exact fit + 1 for outermost wall)
        x_cells, z_cells = (x_width - 1) / (c_dim - 1), (z_width - 1) / (c_dim - 1)
        castle_cells = 13

        maze = Maze(z_cells, x_cells)

        # Disconnect cells where castle resides, ensures compatible maze
        blk_x, blk_z = (x_cells - castle_cells) / 2, (z_cells - castle_cells) / 2
        for bx in xrange(blk_x, blk_x + castle_cells):
            for bz in xrange(blk_z, blk_z + castle_cells):
                maze[bz, bx].disconnect()

        maze.generate()

        # Remove the wall from graph where the labyrinth will meet with castle
        maze[blk_z + castle_cells / 2, blk_x + castle_cells].remove_wall(NORTH)

        # Render the labyrinth by generating blocks where there are walls
        for cell_x in xrange(0, x_cells):
            for cell_z in xrange(0, z_cells):
                walls = maze[cell_z, cell_x].walls
                north, west = min_x + cell_x * (c_dim - 1), min_z + cell_z * (c_dim - 1)
                if walls[NORTH] and walls[SOUTH] and walls[EAST] and walls[WEST]:
                    self.mc.make_cube(north, 0, west, c_dim, c_height, c_dim, material)
                else:
                    if walls[NORTH]:
                        self.mc.make_cube(north, 0, west, 1, c_height, c_dim, material)
                    if walls[SOUTH]:
                        self.mc.make_cube(north + (c_dim - 1), 0, west, 1, c_height, c_dim, material)
                    if walls[EAST]:
                        self.mc.make_cube(north, 0, west + (c_dim - 1), c_dim, c_height, 1, material)
                    if walls[WEST]:
                        self.mc.make_cube(north, 0, west, c_dim, c_height, 1, material)


if __name__ == "__main__":

    net_params = []
    if len(argv) == 2:
        net_params.append(argv[1])
    elif len(argv) == 3:
        net_params.append(argv[1])
        net_params.append(int(argv[2]))

    mc = Minecraft(*net_params)

    def start_game():
        kingdom = Kingdom(mc)
        mc.chat('Building kingdom, this may take a while...')
        sleep(.5)
        kingdom.build()
        mc.chat('Construction complete. Find treasure in the castle!')
        mc.player_pos = (mc.min_x + 2, 25, (mc.min_z + mc.max_z) / 2)

    start_game()
    try:
        while True:
            hit_events = mc.poll_block_hits()
            if hit_events:
                for hit_event in hit_events:
                    hit_block = mc.get_block(hit_event.pos)
                    if hit_block == CHEST.id:
                        mc.chat('Congratulations, You found the treasure!')
                        start_game()
                        break
        sleep(0.25)
    except KeyboardInterrupt:
        print("exiting")
