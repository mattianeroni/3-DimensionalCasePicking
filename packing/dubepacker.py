import operator
import collections

from case import rotate


# Initialize the parameters of the algorithm
# The minimum supporting surface to make the packing feasible
# The minimum number of stable corners to make the packing feasible
MIN_STABLE_SURFACE = 0.7
MIN_STABLE_CORNERS = 3


# Given an index and the already packed case around which
# we are supposed to try a placement, this method returns
# the corresponding position.
def getPosition (index, item):
    d = {
        0 : (item.position[0] + item.sizex, item.position[1], item.position[2]),
        1 : (item.position[0], item.position[1] + item.sizey, item.position[2]),
        2 : (item.position[0], item.position[1], item.position[2] + item.sizez)
    }
    return d.get(index)



# This method checks the intersection between two cases.
def intersect (iCase, jCase):
    if min(iCase.right, jCase.right) > max(iCase.left, jCase.left) and \
       min(iCase.back, jCase.back) > max(iCase.front, jCase.front) and \
       min(iCase.top, jCase.top) > max(iCase.bottom, jCase.bottom):
        return True

    return False




# This method verifies if it is possible to place the currentItem in a given position.
# The method needs to iterate all the list of already packed items to avoid overlaps
# or intersections.
# It also verifies the stability of cases, the vertical support, and the strength constraint.
def fit (currentItem, pallet, packed):
    # Check the pallet borders
    X, Y, Z = pallet.size
    if currentItem.right > X or currentItem.back > Y or currentItem.top > Z:
        return False

    # Initialize the stable surface and the stable corners of the currentItem
    # In a feasible packing, a case must have 3 out of 4 corners, or,
    # alternatively, the 70% of its surface lying on a case underneath.
    stableSurface = 0
    stableCorners = [False,False,False,False]
    itemSurface = currentItem.sizex * currentItem.sizey

    # Identify the corners that need to be supported
    footholds = [
        currentItem.position,
        (currentItem.left, currentItem.back),
        (currentItem.right, currentItem.back),
        (currentItem.right, currentItem.front)
    ]

    for packedItem in packed:
        # Check intersection with other already placed cases.
        if intersect(currentItem, packedItem):
            return False

        # Check if the currentItem has physical support...
        if currentItem.position[2] == 0:
            # If the currentItem is on the floor and has no intersections
            # the placement is feasible.
            stableSurface = itemSurface
            stableCorners = [True,True,True,True]

        elif currentItem.position[2] == packedItem.top:
            # Update the supported surface.
            x1 = min(currentItem.right, packedItem.right); x2 = max(currentItem.left, packedItem.left)
            y1 = min(currentItem.back, packedItem.back); y2 = max(currentItem.front, packedItem.front)
            if x1 > x2 and y1 > y2:
                stableSurface += (x1 - x2) * (y1 - y2)
                # Verify if the vertical support in the corners is provided.
                for idx, point in enumerate(footholds):
                    if not stableCorners[idx] and x2 <= point[0] <= x1 and y2 <= point[1] <= y1:
                        stableCorners[idx] = True
    # If one of the stability conditions is met, returns a positive response.
    # The control is made after all the loop because the loop is needed to check
    # eventual intersections too.
    if stableSurface / itemSurface > MIN_STABLE_SURFACE or sum(stableCorners) >= MIN_STABLE_CORNERS:
        return True

    # Arrived at this point, a positive response should have been returned.
    # If it is not, it mean that there is no intersection between currentItem
    # and the packed cases, but the vertical support is not provided.
    return False



# Algorithm described in the following paper.
# Dube, E., Kanavathy, L. R., & Woodview, P. (2006). Optimizing Three-Dimensional
# Bin Packing Through Simulation. In Sixth IASTED International Conference Modelling,
# Simulation, and Optimization.
def dubePacker (pallet, cases):
    # Initialize the pivot in the bottom-left-front corner
    pivot = (0,0,0)
    X, Y, Z = pallet.size
    packed = collections.deque()

    # Sort cases for decreasing strength
    cases.sort(key=operator.attrgetter('strength'))

    # Place the first item
    currentItem = cases[0]
    currentItem.position = pivot

    # Interrupt immediately if the packing is already not feasible
    if currentItem.top > Z:
        return False

    if currentItem.right > X or currentItem.back > Y:
        rotate(currentItem)
        if currentItem.right > X or currentItem.back > Y:
            return False
    # Add item to the list of packed
    packed.append(currentItem)

    # For each item to pack
    for currentItem in cases[1:]:
        toPack = True
        # Try the three positions close to the already packed items
        # and in each position try the two possible rotations.
        # We first try floor positions for all items. The beginning of a new
        # level is the last thing we try.
        for posIndex in range(3):
            # For each packed case
            for packedItem in packed:
                # Try with the position
                pos = getPosition(posIndex, packedItem)
                currentItem.position = pos
                currentItem.level = packedItem.level + 1 if posIndex == 2 else packedItem.level
                if fit(currentItem, pallet, packed):
                    toPack = False
                    break
                # Eventually try same position rotating the case
                rotate(currentItem)
                if fit(currentItem, pallet, packed):
                    toPack = False
                    break

                # Readjust the item
                rotate(currentItem)

            # If already packed we don't need to try other positions.
            if not toPack: break

        # If all positions have been tried and the packing is not possible
        # there is no feasible solution.
        if toPack: return False
        # If currentItem has been packed add it to the list of packed
        packed.append(currentItem)

    return True
