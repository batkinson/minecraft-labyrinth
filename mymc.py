from mcpi import minecraft
from mcpi.block import *


MAX_DIM = 256
BOUNDARY = BEDROCK_INVISIBLE.id
DIM_IDX = {'x': 0, 'y': 1, 'z': 2}
DIMS = ['x', 'y', 'z']
MIN_MAX = ['_min_', '_max_']


def _dim_coord(dim, value):
    """Returns a tuple where the dimension is value, remaining are zero."""
    result = [0, 0, 0]
    result[DIM_IDX[dim]] = value
    return result


class Minecraft(object):

    """A convenient wrapper over the minecraft pi api."""

    def __init__(self, address=None, port=None):
        self.address = address
        self.port = port
        self._mc = None
        self._max_x = None
        self._min_x = None
        self._max_y = None
        self._min_y = None
        self._max_z = None
        self._min_z = None

    def new_conn(self):
        """Returns a new connection based on this one. Does not recompute world dimensions."""
        clone = Minecraft(self.address, self.port)
        for dim in DIMS:
            for mm in MIN_MAX:
                attr_name = mm + dim
                setattr(clone, attr_name, getattr(self, attr_name))

    @property
    def conn(self):
        """Returns the minecraft connection for this instance. If none exists, it will create one."""
        if not self._mc:
            args = []
            for attr in ['address', 'port']:
                value = getattr(self, attr)
                if value:
                    args.append(value)
            self._mc = minecraft.Minecraft.create(*args)
        return self._mc

    def is_boundary(self, x, y, z):
        """True if the block at x,y,z is invisible bedrock."""
        return self.conn.getBlock(x, y, z) == BOUNDARY

    def _max_dim(self, dim, start=0, end=MAX_DIM):
        """Finds the maximum value in the dim dimension."""
        mid = (start + end) / 2
        if self.is_boundary(*_dim_coord(dim, mid)):
            result = self._max_dim(dim, start, mid - 1)
        elif self.is_boundary(*_dim_coord(dim, mid + 1)):
            result = mid
        else:
            result = self._max_dim(dim, mid + 1, end)
        return result

    def _min_dim(self, dim, start=0, end=-MAX_DIM):
        """Finds the minimum value in the dim dimension."""
        mid = (start + end) / 2
        if self.is_boundary(*_dim_coord(dim, mid)):
            result = self._min_dim(dim, start, mid + 1)
        elif self.is_boundary(*_dim_coord(dim, mid - 1)):
            result = mid
        else:
            result = self._min_dim(dim, mid - 1, end)
        return result

    @property
    def max_x(self):
        if not self._max_x:
            self._max_x = self._max_dim('x')
        return self._max_x

    @property
    def min_x(self):
        if not self._min_x:
            self._min_x = self._min_dim('x')
        return self._min_x

    @property
    def max_z(self):
        if not self._max_z:
            self._max_z = self._max_dim('z')
        return self._max_z

    @property
    def min_z(self):
        if not self._min_z:
            self._min_z = self._min_dim('z')
        return self._min_z

    @property
    def min_y(self):
        """Find lowest y value with usable blocks."""
        return -128

    @property
    def max_y(self):
        """Find highest y value with usable blocks."""
        return 128

    @property
    def center(self):
        """Returns the center point x,y,z of the world as a dict"""
        result = []
        for dim in DIMS:
            result.append((getattr(self, 'max_' + dim) + getattr(self, 'min_' + dim)) / 2)
        return tuple(result)

    def altitude(self, x, z):
        """Returns the max y value at x,z."""
        return self.conn.getHeight(x, z)

    def mark_boundary(self, material=GLOWING_OBSIDIAN):
        """Marks the x/z boundary of the world."""
        for x in xrange(self.min_x + 1, self.max_x):
            self.make_cube(x, self.altitude(x, self.max_z) - 1, self.max_z, material=material)
            self.make_cube(x, self.altitude(x, self.min_z) - 1, self.min_z, material=material)
        for z in xrange(self.min_z, self.max_z + 1):
            self.make_cube(self.max_x, self.altitude(self.max_x, z) - 1, z, material=material)
            self.make_cube(self.min_x, self.altitude(self.min_x, z) - 1, z, material=material)

    def make_cube(self, x, y, z, x_dim=1, y_dim=1, z_dim=1, material=BEDROCK, fill=True):
        """Creates a rectangle with cubes, optionally filled."""
        self.conn.setBlocks(x, y, z, x + (x_dim - 1), y + (y_dim - 1), z + (z_dim - 1), material)
        if not fill and material.id != AIR.id and max(x_dim, y_dim, z_dim) > 2:
            point = []
            dim = []
            for p, d in zip([x, y, z], [x_dim, y_dim, z_dim]):
                if d > 2:
                    p += 1
                    d -= 2
                point.append(p)
                dim.append(d)
            args = point + dim
            args.append(AIR)
            self.make_cube(*args)

    def block_at(self, x, y, z):
        """Returns the block at x, y, z, with additional data."""
        return self.conn.getBlockWithData(x, y, z)

    @property
    def player_pos(self):
        """Moves the player to the specified position."""
        return self.conn.player.getPos()

    @player_pos.setter
    def player_pos(self, *args):
        self.conn.player.setPos(*args)

    def chat(self, msg):
        self.conn.postToChat(msg)

    def poll_block_hits(self):
        return self.conn.events.pollBlockHits()

    def get_block(self, *args):
        return self.conn.getBlock(*args)