#!/usr/bin/python

from dimensions import *
from maze import Maze, NORTH, SOUTH, EAST, WEST
import mcpi.minecraft as minecraft
import mcpi.block as block
from threading import Thread
from time import sleep


def get_conn():
    return minecraft.Minecraft.create(address='checkers.local')

mc = get_conn()


def create_walls(size, base_height, height, material=block.STONE_BRICK):

    """Creates four walls with battlements, walkways and ladders."""

    # Four walls
    mc.setBlocks(-size, base_height + 1, -size, size, base_height + height + 1, size, material)
    mc.setBlocks(-size + 1, base_height + 1, -size + 1, size - 1, base_height + height + 1, size - 1, block.AIR)

    # Carve battlements
    for x in range(1, 2 * size, 2):
        mc.setBlocks(-size + x, base_height + height + 1, -size, -size + x, base_height + height + 1, size, block.AIR)
        mc.setBlocks(-size, base_height + height + 1, -size + x, size, base_height + height + 1, -size + x, block.AIR)

    # Battlement walks
    mc.setBlocks(-size + 1, base_height + height - 1, -size + 1, size - 1, base_height + height - 1, size - 1,
                 block.WOOD_PLANKS)
    mc.setBlocks(-size + 2, base_height + height - 1, -size + 2, size - 2, base_height + height - 1, size - 2,
                 block.AIR)

    # Battlement walk ladder
    mc.setBlocks(-size + 1, base_height + 1, 0, -size + 1, base_height + height, 0, block.LADDER.withData(5))


def create_grounds(moat_width, moat_depth, island_width):

    # Set upper half to air
    mc.setBlocks(x_min, 1, z_min, x_max, y_max, z_max, block.AIR)
    # Set lower half of world to dirt with a layer of grass
    mc.setBlocks(x_min, -1, z_min, x_max, y_min, z_max, block.DIRT)
    mc.setBlocks(x_min, 0, z_min, x_max, 0, z_max, block.GRASS)
    create_labyrinth()
    # Clear maze from moat in to center
    mc.setBlocks(-moat_width, 0, -moat_width, moat_width-1, y_max, moat_width-1, block.AIR)
    # Create water moat
    mc.setBlocks(-moat_width, 0, -moat_width, moat_width-1, -moat_depth, moat_width-1, block.WATER)
    # Replace the ground under the castle
    mc.setBlocks(-island_width, -1, -island_width, island_width, -moat_depth, island_width, block.DIRT)
    mc.setBlocks(-island_width, 0, -island_width, island_width, 0, island_width, block.GRASS)
    # Place planking through castle and over moat
    mc.setBlocks(5, 0, -1, moat_width, 0, 1, block.WOOD_PLANKS)


def create_keep(size=5, base_height=0, levels=4):

    height = (levels * 5) + 5

    create_walls(size, base_height, height)

    # Floors & Windows
    for level in range(1, levels + 1):
        mc.setBlocks(-size + 1, (level * 5) + base_height, -size + 1, size - 1, (level * 5) + base_height, size - 1,
                     block.WOOD_PLANKS)

    # Windows
    for level in range(1, levels + 1):
        create_windows(0, (level * 5) + base_height + 2, size, "N")
        create_windows(0, (level * 5) + base_height + 2, -size, "S")
        create_windows(-size, (level * 5) + base_height + 2, 0, "W")
        create_windows(size, (level * 5) + base_height + 2, 0, "E")

    # Door
    mc.setBlocks(0, base_height + 1, size, 0, base_height + 2, size, block.AIR)
    mc.setBlock(0, base_height + 1, size, block.DOOR_WOOD.withData(3))
    mc.setBlock(0, base_height + 2, size, block.DOOR_WOOD.withData(8))

    # Replace ladder
    mc.setBlocks(-4, 1, 0, -4, 25, 0, block.AIR)
    mc.setBlocks(-4, 1, 0, -4, 25, 0, block.LADDER.withData(5))


def create_windows(x, y, z, direction):

    if direction == "N" or direction == "S":
        z1 = z
        z2 = z
        x1 = x - 2
        x2 = x + 2

    if direction == "E" or direction == "W":
        z1 = z - 2
        z2 = z + 2
        x1 = x
        x2 = x

    mc.setBlocks(x1, y, z1, x1, y + 1, z1, block.AIR)
    mc.setBlocks(x2, y, z2, x2, y + 1, z2, block.AIR)

    if direction == "N":
        a = 3
    if direction == "S":
        a = 2
    if direction == "W":
        a = 0
    if direction == "E":
        a = 1

    mc.setBlock(x1, y - 1, z1, 109, a)
    mc.setBlock(x2, y - 1, z2, 109, a)


def create_labyrinth(material=block.LEAVES.withData(1)):
    """Generates and renders a labyrinth."""
    c_dim, c_height = 5, 3
    x_width, z_width = x_max - x_min,  z_max - z_min
    x_cells, z_cells = x_width / c_dim, z_width / c_dim
    maze = Maze(z_cells, x_cells)
    blk_x, blk_z = (x_cells - 13) / 2, (z_cells - 13) / 2
    for bx in xrange(blk_x, blk_x + 13):
        for bz in xrange(blk_z, blk_z + 13):
            maze[bz, bx].disconnect()
    maze.generate()
    maze[blk_z + 6, blk_x + 13].remove_wall(NORTH)
    for cell_x in xrange(0, x_cells):
        for cell_z in xrange(0, z_cells):
            walls = maze[cell_z, cell_x].walls
            north, west = x_min + cell_x * c_dim, z_min + cell_z * c_dim
            if walls[NORTH] and walls[SOUTH] and walls[EAST] and walls[WEST]:
                mc.setBlocks(north, 1, west, north + c_dim, c_height + 1, west + c_dim, material)
            else:
                if walls[NORTH]:
                    mc.setBlocks(north, 1, west, north, c_height + 1, west + c_dim, material)
                if walls[SOUTH]:
                    mc.setBlocks(north + c_dim, 1, west, north + c_dim, c_height + 1, west + c_dim, material)
                if walls[EAST]:
                    mc.setBlocks(north, 1, west + c_dim, north + c_dim, c_height + 1, west + c_dim, material)
                if walls[WEST]:
                    mc.setBlocks(north, 1, west, north + c_dim, c_height + 1, west, material)


def build_kingdom():

    mc.postToChat('Building kingdom, this may take a while...')
    sleep(.5)

    def build_it():
        create_grounds(32, 10, 23)
        create_walls(21, 0, 5)
        create_walls(13, 0, 6)
        create_keep()
        # Plant flowers in front
        mc.setBlocks(23, 1, -23, 22, 1, 23, block.FLOWER_YELLOW)
        # Build castle streets
        mc.setBlocks(-21, 0, -21, 21, 0, 21, block.MOSS_STONE)
        mc.setBlocks(-18, 0, -18, 18, 0, 18, block.COBBLESTONE)
        mc.setBlocks(-15, 0, -15, 15, 0, 15, block.MOSS_STONE)
        mc.setBlocks(-10, 0, -10, 10, 0, 10, block.COBBLESTONE)
        mc.setBlocks(-7, 0, -7, 7, 0, 7, block.MOSS_STONE)
        mc.setBlocks(-5, 0, -5, 5, 0, 5, block.COBBLESTONE)
        mc.setBlocks(8, 0, -1, 21, 0, 1, block.COBBLESTONE)
        mc.setBlocks(0, 0, 6, 0, 0, 7, block.COBBLESTONE)
        # Creates gateways
        mc.setBlocks(13, 1, -1, 23, 3, 1, block.AIR)
        # Add our treasure
        mc.setBlock(4, 21, 0, block.CHEST.withData(4))
        # Position player at the middle of the southern boundary
        mc.player.setPos(x_min + 2, 25, (z_min + z_max) / 2)
        mc.postToChat('Construction complete. Find treasure in the castle!')

    build_thread = Thread(target=build_it)
    build_thread.start()
    build_thread.join()


class ExplodingBlock(Thread):

    """Manages making a TNT block explode."""

    def __init__(self, x, y, z, fuse_delay, blast_radius):
        Thread.__init__(self)
        self.x, self.y, self.z = x, y, z
        self.fuse_delay = fuse_delay
        self.blast_radius = blast_radius
        self.blink_pause = 0.25

    @staticmethod
    def explode(x, y, z, fuse=3, radius=3):
        exp_block = ExplodingBlock(x, y, z, fuse, radius)
        exp_block.daemon = True
        exp_block.start()

    def run(self):
        conn = get_conn()
        x, y, z = self.x, self.y, self.z
        blast_radius = self.blast_radius

        # The fuse
        for fuse in xrange(0, self.fuse_delay):
            conn.setBlock(x, y, z, block.AIR)
            sleep(self.blink_pause)
            conn.setBlock(x, y, z, block.TNT)
            sleep(self.blink_pause)

        blasts = [(x, y, z)]

        # The blast
        while blasts:
            x, y, z = blasts.pop(0)
            for bxo in xrange(-blast_radius, blast_radius):
                for byo in xrange(-blast_radius, blast_radius):
                    for bzo in xrange(-blast_radius, blast_radius):
                        if bxo ** 2 + byo ** 2 + bzo ** 2 < blast_radius ** 2:
                            bx, by, bz = x + bxo, y + byo, z + bzo
                            conn.setBlock(bx, by, bz, block.AIR)


if __name__ == "__main__":
    build_kingdom()
    try:
        while True:
            hit_events = mc.events.pollBlockHits()
            if hit_events:
                for hit_event in hit_events:
                    hit_block = mc.getBlock(hit_event.pos)
                    if hit_block == block.CHEST.id:
                        build_kingdom()
                    elif hit_block == block.TNT.id:
                        hp = hit_event.pos
                        ExplodingBlock.explode(hp.x, hp.y, hp.z)
        sleep(0.1)
    except KeyboardInterrupt:
        print("exiting")


