import operator
import collections

from case import rotate


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
def fit (currentItem, pallet, pos, packed):
    # Check the pallet borders
    X, Y, Z = pallet.size
    if currentItem.right > X or currentItem.back > Y or currentItem.top > Z:
        return False

    for packedItem in packed:
        # Check intersection with other already placed cases
        if intersect(currentItem, packedItem):
            return False

    return True



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
                if fit(currentItem, pallet, pos, packed):
                    toPack = False
                    break
                # Eventually try same position rotating the case
                rotate(currentItem)
                if fit(currentItem, pallet, pos, packed):
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
