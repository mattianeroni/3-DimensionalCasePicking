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
        0 : (item.x + item.sizex, item.y, item.z),
        1 : (item.x, item.y + item.sizey, item.z),
        2 : (item.x, item.y, item.z + item.sizez),
    }
    return d.get(index)



# This method checks the intersection between two cases.
def intersect (iCase, jCase):
    if min(iCase.right, jCase.right) > max(iCase.left, jCase.left) and \
       min(iCase.back, jCase.back) > max(iCase.front, jCase.front) and \
       min(iCase.top, jCase.top) > max(iCase.bottom, jCase.bottom):
        return True

    return False


# This method checks if the placement of a case is possible or is prevetend
# by the presence on another one.
def obstruct (topack, obstructor):
    if not (obstructor.x > topack.x and \
       min(obstructor.back, topack.back) > max(obstructor.front, topack.front) and \
       min(obstructor.top, topack.top) > max(obstructor.bottom, topack.bottom)):
       return False

    if not (obstructor.y > topack.y and \
       min(obstructor.right, topack.right) > max(obstructor.left, topack.left) and \
       min(obstructor.top, topack.top) > max(obstructor.bottom, topack.bottom)):
       return False

    if not (obstructor.z > topack.z and \
       min(iCase.right, jCase.right) > max(iCase.left, jCase.left) and \
       min(iCase.back, jCase.back) > max(iCase.front, jCase.front)):
       return False

    return True


# This method verifies if it is possible to place the currentItem in a given position.
# The method needs to iterate all the list of already packed items to avoid overlaps
# or intersections.
# It also verifies the stability of cases, the vertical support, and the strength constraint.
def fit (currentItem, pallet, packed, layersMap):
    left, right = currentItem.left, currentItem.right
    front, back = currentItem.front, currentItem.back
    # Check the pallet borders
    X, Y, Z = pallet.size
    if right > X or back > Y or currentItem.top > Z:
        return False

    # Initialize the stable surface and the stable corners of the currentItem
    # In a feasible packing, a case must have 3 out of 4 corners, or,
    # alternatively, the 70% of its surface lying on a case underneath.
    stableSurface = 0
    stableCorners = [0,0,0,0]  # To use as boolean
    sumStables = 0
    stable = False
    itemSurface = currentItem.sizex * currentItem.sizey

    # Verify if the currentItem placement could be obstructed by one of
    # the already packed items.
    # If yes a further constrol is made for every packedItem.
    obstructRisk = False if left == 0 or right == X or front == 0 or back == Y else True

    # Save the orderline corresponding to the currentItem
    orderline = currentItem.orderline

    # Identify the corners that need to be supported
    footholds = [
        currentItem.position,
        (left, back),
        (right, back),
        (right, front)
    ]

    for packedItem in packed:
        # Check intersection with other already placed cases.
        if intersect(currentItem, packedItem):
            return False

        # Check if packedItem prevents the placement of currentItem
        if obstructRisk and obstruct(currentItem, packedItem):
            return False

        #if not stable:
        # Check if the currentItem has physical support...
        if not stable and currentItem.z == 0:
            # If the currentItem is on the floor and has no intersections
            # the placement is feasible.
            stableSurface = itemSurface
            stableCorners = [1,1,1,1]
            sumStables = 4
            stable = True
            # Update the layer of the currentItem
            if layersMap.get(orderline) is None:
                layersMap[orderline] = 0

        elif currentItem.z == packedItem.top:
            # If currentItem will lay on another case...
            x1 = min(right, packedItem.right); x2 = max(left, packedItem.left)
            y1 = min(back, packedItem.back); y2 = max(front, packedItem.front)
            if x1 > x2 and y1 > y2:
                # If the packedItem cannot hold a case above, interrupt immediately
                if packedItem.canHold == 0:
                    return False

                # Check the strength and the number of cases the currentItem
                # will be able to hold above.
                currentItem.canHold = max(0, min(currentItem.strength, packedItem.canHold - 1))

                if not stable:
                    # Update the supported surface.
                    stableSurface += (x1 - x2) * (y1 - y2)

                    # Verify if the vertical support in the corners is provided.
                    for idx, point in enumerate(footholds):
                        if not stableCorners[idx] and x2 <= point[0] <= x1 and y2 <= point[1] <= y1:
                            stableCorners[idx] = 1
                            sumStables += 1

                    # Define the layer of the OrderLine corresponding to currentItem.
                    if packedItem.code != currentItem.code:
                        packedOrderLine = packedItem.orderline
                        if (layer := layersMap.get(orderline)) is not None:
                            layersMap[orderline] = max(layer, layersMap[packedOrderLine] + 1)
                        else:
                            layersMap[orderline] = layersMap[packedOrderLine] + 1

                    # If one of the stability conditions is met.
                    if stableSurface / itemSurface > MIN_STABLE_SURFACE or sumStables >= MIN_STABLE_CORNERS:
                        stable = True
    # At this point there are no intersections, if the currentItem is stable
    # a positive response is returned.
    if stable:
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
    packed = collections.deque(pallet.cases)

    # Initialize the layers map in which it will be saved the layer
    # corresponding to each OrderLine
    layersMap = dict()

    # Sort cases for decreasing strength
    cases.sort(key=operator.attrgetter('strength'), reverse=True)

    # Place the first item
    currentItem = cases[0]
    currentItem.setPosition(pivot)
    layersMap[currentItem.orderline] = 0

    # Interrupt immediately if the packing is already not feasible
    if currentItem.top > Z:
        return False, packed, layersMap

    if currentItem.right > X or currentItem.back > Y:
        rotate(currentItem)
        if currentItem.right > X or currentItem.back > Y:
            return False, packed, layersMap
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
                currentItem.setPosition(pos)
                if fit(currentItem, pallet, packed, layersMap):
                    toPack = False
                    break
                # Eventually try same position rotating the case
                rotate(currentItem)
                if fit(currentItem, pallet, packed, layersMap):
                    toPack = False
                    break

                # Readjust the item
                rotate(currentItem)

            # If already packed we don't need to try other positions.
            if not toPack: break

        # If all positions have been tried and the packing is not possible
        # there is no feasible solution.
        if toPack:
            return False, packed, layersMap
        # If currentItem has been packed add it to the list of packed
        packed.append(currentItem)

    return True, packed, layersMap
