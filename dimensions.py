from mcpi import minecraft, block

mc = minecraft.Minecraft.create(address='checkers.local')

MAX_DIM = 256
BOUNDARY = block.BEDROCK_INVISIBLE.id

__all__ = ['x_min', 'x_max', 'z_min', 'z_max', 'y_min', 'y_max', 'x_center', 'z_center']


def is_boundary(x, y, z):
    """True if the block at x,y,z is invisible bedrock."""
    return mc.getBlock(x, y, z) == BOUNDARY


def find_x_max(start=0, end=MAX_DIM):
    """Find highest x value with usable blocks."""
    mid = (start + end) / 2
    if is_boundary(mid, 0, 0):
        return find_x_max(start, mid - 1)
    elif is_boundary(mid + 1, 0, 0):
        return mid
    else:
        return find_x_max(mid + 1, end)


def find_x_min(start=0, end=-MAX_DIM):
    """Find lowest x value with usable blocks."""
    mid = (start + end) / 2
    if is_boundary(mid, 0, 0):
        return find_x_min(start, mid + 1)
    elif is_boundary(mid - 1, 0, 0):
        return mid
    else:
        return find_x_min(mid - 1, end)


def find_z_max(start=0, end=MAX_DIM):
    """Find highest z value with usable blocks."""
    mid = (start + end) / 2
    if is_boundary(0, 0, mid):
        return find_z_max(start, mid - 1)
    elif is_boundary(0, 0, mid + 1):
        return mid
    else:
        return find_z_max(mid + 1, end)


def find_z_min(start=0, end=-MAX_DIM):
    """Find lowest z value with usable blocks."""
    mid = (start + end) / 2
    if is_boundary(0, 0, mid):
        return find_z_min(start, mid + 1)
    elif is_boundary(0, 0, mid - 1):
        return mid
    else:
        return find_z_min(mid - 1, end)


def x_dim():
    """Returns the usable x dimensions as a tuple, (min, max)."""
    return find_x_min(), find_x_max()


def z_dim():
    """Returns the usable z dimensions as a tuple, (min, max)."""
    return find_z_min(), find_z_max()


x_min, x_max = x_dim()
z_min, z_max = z_dim()

# y dimension doesn't matter as much, for now
y_min, y_max = -128, 128

x_center, z_center = (x_min + x_max) / 2, (z_min + z_max) / 2


def mark_boundary(material=block.GLOWING_OBSIDIAN):
    """Marks the x/z boundary of the world."""
    for x in xrange(x_min + 1, x_max):
        mc.setBlock(x, mc.getHeight(x, z_max) - 1, z_max, material)
        mc.setBlock(x, mc.getHeight(x, z_min) - 1, z_min, material)
    for z in xrange(z_min, z_max + 1):
        mc.setBlock(x_max, mc.getHeight(x_max, z) - 1, z, material)
        mc.setBlock(x_min, mc.getHeight(x_min, z) - 1, z, material)
