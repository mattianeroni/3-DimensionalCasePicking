"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
This file is part of the implementation of an algorithm for solving the
3-dimensional case picking problem. A newly considered problem of operational
research that combines the routing of pickers into the warehouse, with the
positioning of 3-dimensional items inside pallets (i.e., Pallet Loading Problem).

The algorithm proposed and implemented comes from a collaboration between the
Department of Engineering at University of Parma (Parma, ITALY) and the
IN3 Computer Science Dept. at Universitat Oberta de Catalunya (Barcelona, SPAIN).


Written by Mattia Neroni Ph.D., Eng. in July 2021.
Author' contact: mattianeroni93@gmail.com
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
import operator
import collections
import functools

from .case import rotate
from .pallet import HashableDict


# Initialize the parameters of the algorithm
# The minimum supporting surface to make the packing feasible
# The minimum number of stable corners to make the packing feasible
MIN_STABLE_SURFACE = 0.7
MIN_STABLE_CORNERS = 3



def getPosition (index, item):
    """
     Given an index and the already packed case around which
     we are supposed to try a placement, this method returns
     the corresponding position.
    """
    d = {
        0 : (item.x + item.sizex, item.y, item.z),
        1 : (item.x, item.y + item.sizey, item.z),
        2 : (item.x, item.y, item.z + item.sizez),
    }
    return d.get(index)


# Deprecated -- Now it is controlled in the check_obstruction
# method to avoid further controls.
# This method checks the intersection between two cases.
#def intersect (iCase, jCase):
#    if min(iCase.right, jCase.right) > max(iCase.left, jCase.left) and \
#       min(iCase.back, jCase.back) > max(iCase.front, jCase.front) and \
#       min(iCase.top, jCase.top) > max(iCase.bottom, jCase.bottom):
#        return True
#
#    return False



def check_obstruction (toplace, obstructor, obstructionRisk, possibleInserts, insertsSum):
    """
     This method checks if the placement of a case is possible or is prevetend
     by the presence on another one.
     During the placement is also verified the physical possibility to place
     the case in that position by reaching the position from each of five directions.

     :param toplace: <Case> The case for which the placement must be verified.
     :param obstructor: <Case> The case that may obstuct the placement.
     :param obstructionRisk: <bool> Boolean variable True only if the case to place
                            is not on the side of the pallet. It avoids additional
                            controls when not necessary.
    :param possibleInserts: <list> A list of Boolean elements (0 or 1). If at leas one of these
                            elements is 1 after checking all the possible obstructors, the
                            case to place can be placed in the given position.
    :param insertsSum: <int> Simply keeps track of still possible inserts. At the beginning it
                        is equal to 5, if it is higher than 0 after checking all the possible
                        obstructors, the placement of case to place in the given position is
                        allowed.

    :return: <tuple> First element is True if there is an instersection and False otherwise,
            while the second return teh insertsSum value that say if the physical placement
            made by an operator is possible.

    """
    # If there is an overlap along X-axis
    overlapX = True if min(obstructor.right, toplace.right) > max(obstructor.left, toplace.left) else False
    # If there is an overlap along Y-axis
    overlapY = True if min(obstructor.back, toplace.back) > max(obstructor.front, toplace.front) else False
    # If there is an overlap along Z-axis
    overlapZ = True if min(obstructor.top, toplace.top) > max(obstructor.bottom, toplace.bottom) else False

    # This is an intersection
    if overlapX and overlapY and overlapZ:
        return True, insertsSum

    # In this case the obstruction controls are not needed
    # NOTE: this check is here and not outside this function, because is important
    # to verify in any case that there is no intersection (see previous check).
    if not obstructionRisk:
        return False, insertsSum

    # Check possible insert along X-axis
    if overlapY and overlapZ:
        if possibleInserts[0] == 1 and obstructor.x < toplace.x:
            possibleInserts[0] = 0
            return False, insertsSum - 1
        elif possibleInserts[1] == 1 and obstructor.x > toplace.x:
            possibleInserts[1] = 0
            return False, insertsSum - 1

    # Check possible insert along Y-axis
    if overlapX and overlapZ:
        if possibleInserts[2] == 1 and obstructor.y < toplace.y:
            possibleInserts[2] = 0
            return False, insertsSum - 1
        elif possibleInserts[3] == 1 and obstructor.y > toplace.y:
            possibleInserts[3] = 0
            return False, insertsSum - 1

    # Check possible insert along Z-axis
    if overlapX and overlapY and obstructor.z > toplace.z:
        possibleInserts[4] = 0
        return False, insertsSum - 1

    return False, insertsSum



def fit (currentItem, pallet, packed, layersMap):
    """
     This method verifies if it is possible to place the currentItem in a given position.
     The method needs to iterate all the list of already packed items to avoid overlaps
     or intersections.
     It also verifies the stability of cases, the vertical support, and the strength constraint.

     :param currentItem: <Case> The case to place
     :param pallet: <Pallet> The pallet (only used to get it size)
     :param packed: <list<Case>> The set of already packed cases in that pallet
     :param layersMap: <dict> A copy of the layersMap of the pallet used to keep track
                        of orderlines level (i.e., order in which they can be placed).

     :return: True if the placement is possible and False otherwise.

    """
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


    # Check if the currentItem can be obstructed by other items.
    # In other words we check a priori if currentItem can be physically be
    # placed with no need of further controls.
    possibleInserts = [1,1,1,1,1]   # To use as boolean
    insertsSum = 5
    obstructRisk = False if left == 0 or right == X or front == 0 or back == Y else True

    # Save the orderline corresponding to the currentItem
    orderline = currentItem.orderline
    # Initialise the 'layer' associated to the currentItem in a local variable
    layer = clayer if (clayer := layersMap.get(orderline)) else 0

    # Identify the corners that need to be supported
    footholds = [
        currentItem.position,
        (left, back),
        (right, back),
        (right, front)
    ]

    for packedItem in packed:
        # Check intersection with other already placed cases.
        #if intersect(currentItem, packedItem):
        #    return False

        # Check if packedItem prevents the placement of currentItem.
        # Check intersection with other already placed cases.
        intersection, insertsSum = check_obstruction(currentItem, packedItem, obstructRisk, possibleInserts, insertsSum)
        if intersection or insertsSum == 0:
            return False


        # Check if the currentItem has physical support...
        if not stable and currentItem.z == 0:
            # If the currentItem is on the floor and has no intersections
            # the placement is feasible.
            stableSurface = itemSurface
            stableCorners = [1,1,1,1]
            sumStables = 4
            stable = True
            # Update the layer of the currentItem
            layer = max(layer, 0)

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
                # If it is not placed on top of any other case, this value is already initialised
                # equal to the currentItem strength.
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
                        layer = max(layer, layersMap[packedOrderLine] + 1)

                    # If one of the stability conditions is met.
                    if stableSurface / itemSurface >= MIN_STABLE_SURFACE or sumStables >= MIN_STABLE_CORNERS:
                        stable = True
    # At this point there are no intersections, if the currentItem is stable
    # a positive response is returned after setting the layer of the currentItem.
    if stable:
        layersMap[orderline] = layer
        return True
    # Arrived at this point, a positive response should have been returned.
    # If it is not, it mean that there is no intersection between currentItem
    # and the packed cases, but the vertical support is not provided.
    return False




@functools.lru_cache(maxsize=32)
def dubePacker (pallet, hosted):
    """
     The algorithm implemented in this method is a modified version of the one proposed by:
     Dube, E., Kanavathy, L. R., & Woodview, P. (2006). Optimizing Three-Dimensional
     Bin Packing Through Simulation. In Sixth IASTED International Conference Modelling,
     Simulation, and Optimization.

     The original version did not consider the aspect that are here implemented and reported:
        - Stability issues
        - Portability and strength issues
        - Actual possibility to place cases in a given position (obstructions during the
          placement)


     :param pallet: <Pallet> The pallet in which cases must be placed.
     :param hosted: <list<Case>> The set of cases to place.

     :return: <tuple> The first element is True if the packing has been successful
                and False otherwise, the second returns the set of packed items with
                the attributes and characteristichs they assumed during the packing
                (note at the beginning a copy of hosted cases is made), while, the
                third element is the new layersMap of the pallet.

    """
    # Copy pallet's data
    X, Y, Z = pallet.size
    packed = collections.deque([c.__copy__() for c in pallet.cases])

    # Initialize the layers map in which it will be saved the layer
    # corresponding to each OrderLine
    layersMap = HashableDict(pallet.layersMap)

    # Sort cases for decreasing strength
    sortedCases = sorted(hosted.cases, key=operator.attrgetter('strength'), reverse=True)

    # For each item to pack
    for currentItem in sortedCases:
        currentItem = currentItem.__copy__()
        currentItem.busyCorners = [False, False, False]
        currentItem.canHold = currentItem.strength

        if len(packed) == 0:
            # Place the first item
            pivot = (0,0,0)
            currentItem.setPosition(pivot)

            # Interrupt immediately if the packing is already not feasible
            if currentItem.top > Z:
                return False, packed, layersMap

            if currentItem.right > X or currentItem.back > Y:
                rotate(currentItem)
                if currentItem.right > X or currentItem.back > Y:
                    return False, packed, layersMap
            # Add item to the list of packed and update the layers map
            layersMap[currentItem.orderline] = 0
            packed.append(currentItem)
        else:
            toPack = True
            # Try the three positions close to the already packed items
            # and in each position try the two possible rotations.
            # We first try floor positions for all items. The beginning of a new
            # level is the last thing we try.
            for posIndex in range(3):
                # For each packed case
                for packedItem in packed:
                    # If the corner is already busy no further chack is made.
                    if packedItem.busyCorners[posIndex]:
                        continue
                    # Set the currentItem in a certain position
                    pivot = getPosition(posIndex, packedItem)
                    currentItem.setPosition(pivot)
                    # Try the two possible rotations
                    if fit(currentItem, pallet, packed, layersMap):
                        toPack = False
                        packedItem.busyCorners[posIndex] = True
                        break
                    # Eventually try same position rotating the case
                    rotate(currentItem)
                    if fit(currentItem, pallet, packed, layersMap):
                        toPack = False
                        packedItem.busyCorners[posIndex] = True
                        break
                    # Readjust the item
                    rotate(currentItem)

                # If already packed we don't need to try other positions.
                if not toPack: break

            # If all positions have been tried and the packing is not possible
            # there is no feasible solution.
            if toPack: return False, packed, layersMap
            # If currentItem has been packed add it to the list of packed
            packed.append(currentItem)

    return True, packed, layersMap
