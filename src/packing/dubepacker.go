package packing

import (
	"math"
	"sort"
)

// Position and Size of a case seen as arrays
type Position [3]int
type Size [3]int



// Initialize the parameters of the algorithm
// The minimum supporting surface to make the packing feasible
// The minimum number of stable corners to make the packing feasible
const MIN_STABLE_SURFACE float64 = 0.7
const MIN_STABLE_CORNERS int = 3


// Given an index and the already packed case around which
// we are supposed to try a placement, this method returns
// the corresponding position.
func getPosition (index int, item Case) Position {
	switch index {
	case 0:
		return Position{item.X + item.SizeX, item.Y, item.Z}
	case 1:
		return Position{item.X, item.Y + item.SizeY, item.Z}
	case 2:
		return Position{item.X, item.Y, item.Z + item.SizeZ}
	default:
		return Position{0,0,0}
	}
}


// This method checks the intersection between two cases.
func intersect (iCase, jCase Case) bool {
	if math.Min(float64(iCase.Right()), float64(jCase.Right())) > math.Max(float64(iCase.Left()), float64(jCase.Left())) &&
	   math.Min(float64(iCase.Back()), float64(jCase.Back())) > math.Max(float64(iCase.Front()), float64(jCase.Front())) &&
	   math.Min(float64(iCase.Top()), float64(jCase.Top())) > math.Max(float64(iCase.Bottom()), float64(jCase.Bottom())) {
		return true
	}
	return false
}


// This method checks if a case obstruct another, and prevents its placement.
func checkObstruction (toplace, obstructor Case, possibleInserts *[5]int, sumInserts *int) {
	overlapX, overlapY, overlapZ := false, false, false
	// If there is an overlap along X-axis
	if math.Min(float64(obstructor.Right()), float64(toplace.Right())) > math.Max(float64(obstructor.Left()), float64(toplace.Left())){
		overlapX = true
	}
	// If there is an overlap along Y-axis
	if math.Min(float64(obstructor.Back()), float64(toplace.Back())) > math.Max(float64(obstructor.Front()), float64(toplace.Front())) {
		overlapY = true
	}
	// If there is an overlap along Z-axis
	if math.Min(float64(obstructor.Top()), float64(toplace.Top())) > math.Max(float64(obstructor.Bottom()), float64(toplace.Bottom())){
		overlapZ = true
	}

	// Check possible insert along X-axis
	if overlapY && overlapZ {
		if possibleInserts[0] == 1 && obstructor.X < toplace.X {
			possibleInserts[0] = 0
			*sumInserts--
		} else if possibleInserts[1] == 1 && obstructor.X > toplace.X {
			possibleInserts[1] = 0
			*sumInserts--
		}
	}
	// Check possible insert along Y-axis
	if overlapX && overlapZ {
		if possibleInserts[2] == 1 && obstructor.Y < toplace.Y {
			possibleInserts[2] = 0
			*sumInserts--
		} else if possibleInserts[3] == 1 && obstructor.Y > toplace.Y {
			possibleInserts[3] = 0
			*sumInserts--
		}
	}
	// Check possible insert along Z-axis
	if overlapX && overlapY && obstructor.Z > toplace.Z {
		possibleInserts[4] = 0
		*sumInserts--
	}
}


// This method verifies if it is possible to place the currentItem in a given position.
// The method needs to iterate all the list of already packed items to avoid overlaps
// or intersections.
// It also verifies the stability of cases, the vertical support, and the strength constraint.
func fit (currentItem *Case, pallet Pallet, packed []Case, levelsMap map[*OrderLine]int) bool {
	// Check the pallet borders
	X, Y, Z := pallet.Size()
	if currentItem.Right() > X || currentItem.Back() > Y || currentItem.Top() > Z {
		return false
	}
	// Initialize the stable surface and the stable corners of the currentItem
	// In a feasible packing, a case must have 3 out of 4 corners, or,
	// alternatively, the 70% of its surface lying on a case underneath.
	var stableSurface float64 = 0
	var stableCorners = [4]int{0,0,0,0}  // To use as boolean
	var stableSum int = 0
	var stable bool = false
	itemSurface := float64(currentItem.SizeX * currentItem.SizeY)

	// Identify the corners that need to be supported
	var footholds = [4]Position{
		{currentItem.X, currentItem.Y, currentItem.Z},
		{currentItem.Left(), currentItem.Back(), currentItem.Z},
		{currentItem.Right(), currentItem.Back(), currentItem.Z},
		{currentItem.Right(), currentItem.Front(), currentItem.Z}}

	// Check if the currentItem can be obstructed by other items.
	// In other words we check a priori if currentItem can be physically be
	// placed with no need of further controls.
	var possibleInserts = [5]int{1,1,1,1,1}  // To use as boolean
	var insertsSum int = 5
	var obstructable bool = true
	if currentItem.X == 0 || currentItem.Y == 0 || currentItem.Right() == X || currentItem.Back() == Y {
		obstructable = false
	}

	for _, packedItem := range packed {
		// Check intersection with other already placed cases
		if intersect(*currentItem, packedItem) == true {
			return false
		}
		// Check if the currentItem can physically be placed in that position,
		// or, alternatively, the packedItem prevents this.
		if obstructable == true {
			checkObstruction(*currentItem, packedItem, &possibleInserts, &insertsSum)
			if insertsSum == 0 {
				return false
			}
		}

		// Check if the currentItem has physical support
		if currentItem.Z == 0 && !stable{
			// If the currentItem is on the floor and has no intersections
			// the placement is feasible.
			stableSurface = itemSurface
			stableCorners = [4]int{1, 1, 1, 1}
			stableSum = 4
			stable = true
			// Update the level of the currentItem OrderLine
			if val, ok := levelsMap[currentItem.OrderLine]; ok {
				levelsMap[currentItem.OrderLine] = int(math.Max(float64(val), 0))
			} else {
				levelsMap[currentItem.OrderLine] = 0
			}

		} else if currentItem.Z == packedItem.Top() {
			x1 := math.Min(float64(currentItem.Right()), float64(packedItem.Right()))
			x2 := math.Max(float64(currentItem.Left()), float64(packedItem.Left()))
			y1 := math.Min(float64(currentItem.Back()), float64(packedItem.Back()))
			y2 := math.Max(float64(currentItem.Front()), float64(packedItem.Front()))
			// If the cases are one above the other, and packedItem must support currentItem...
			if x1 > x2 && y1 > y2 {
				// If the packedItem that must sustain the currentItem cannot hold
				// any case above, a negative response is immediately returned.
				if packedItem.CanHold == 0 {
					return false
				}
				// Define how many cases the currentItem is allowed to hold above.
				currentItem.CanHold = int(math.Max(0, math.Min(float64(currentItem.Strength), float64(packedItem.CanHold - 1.0))))

				// Controls made only if the currentItem has not been marked as stable yet.
				if !stable {
					// Update the supported surface.
					stableSurface += (x1 - x2) * (y1 - y2)
					// Verify if the vertical support in the corners is provided.
					for idx, point := range footholds {
						if stableCorners[idx] == 0 && x2 <= float64(point[0]) && float64(point[0]) <= x1 && y2 <= float64(point[1]) && float64(point[1]) <= y1 {
							stableCorners[idx] = 1
							stableSum++
						}
					}
					// Define the layer of the order line corresponding to currentItem.
					if packedItem.Code != currentItem.Code {
						if val, ok := levelsMap[currentItem.OrderLine]; ok {
							levelsMap[currentItem.OrderLine] = int(math.Max(float64(val), float64(levelsMap[packedItem.OrderLine] + 1)))
						} else {
							levelsMap[currentItem.OrderLine] = levelsMap[packedItem.OrderLine] + 1
						}
					}

					// If one of the stability conditions are met, mark the currentItem as stable.
					if stableSurface/itemSurface > MIN_STABLE_SURFACE || stableSum >= MIN_STABLE_CORNERS {
						stable = true
					}
				}
			}
		}
	}
	// If the currentItem is stable returns a positive response
	// This control is made after all the loop because the loop is needed to check
	// eventual intersections too.
	if stable {
		return true
	}
	// Arrived at this point, a positive response should have been returned.
	// If it is not, it mean that there is no intersection between currentItem
	// and the packed cases, but the vertical support is not provided.
	return false
}




// Algorithm described in the following paper.
// Dube, E., Kanavathy, L. R., & Woodview, P. (2006). Optimizing Three-Dimensional
// Bin Packing Through Simulation. In Sixth IASTED International Conference Modelling,
// Simulation, and Optimization.
func DubePacker (pallet Pallet, cases []Case) (bool, []Case, map[*OrderLine]int){
	// Initialize the pivot and other useful variables
	var pivot Position
	var toPack bool
	// Initilize the size of the pallet
	X, Y, Z := pallet.Size()
	// Initilize the already packed cases
	var packed []Case = pallet.Cases					 // Pallet is passed by value so the origilnals are not changed
	// Initialize the map containig the level for each order line
	var levelsMap map[*OrderLine]int = pallet.LayersMap  // Pallet is passed by value so the origilnals are not changed

	// Sort cases for decreasing strength
	sort.Slice(cases, func(i, j int) bool {
		return cases[i].Strength > cases[j].Strength
	})

	// For each item to pack
	for _, currentItem := range cases {
		// A just placed case has no busy corners
		currentItem.busyCorners = [3]bool{false, false, false}
		toPack = true
		// If the case to place is the first, just place it and quickly checks
		// that it does not exceed the pallet borders.
		if len(packed) == 0 {
			// Place the first case in the bottom-front-left corner
			levelsMap[currentItem.OrderLine] = 0
			setPos(&currentItem, Position{0,0,0})

			// Interrupt immediately if the packing is already not feasible
			if currentItem.Top() > Z {
				return false, cases, levelsMap
			}
			if currentItem.Right() > X || currentItem.Back() > Y {
				rotate(&currentItem)
				if currentItem.Right() > X || currentItem.Back() > Y {
					return false, cases, levelsMap
				}
			}
			// Append it to the list of packed items
			packed = append(packed, currentItem)
			toPack = false
			continue
		}
		// Try the three positions close to the already packed items
		// and in each position try the two possible rotations.
		// We first try floor positions for all items. The beginning of a new
		// level is the last thing we try.
		for posIndex := 0; posIndex < 3; posIndex++{
			// For each packed case
			for _, packedItem := range packed {
				// If the packedItem considered corner is marked as
				// busy, the placement is not even tried.
				if packedItem.busyCorners[posIndex] == true {
					continue
				}
				// Try with the position
				pivot = getPosition(posIndex, packedItem)
				setPos(&currentItem, pivot)
				if fit(&currentItem, pallet, packed, levelsMap) == true {
					toPack = false
					packedItem.busyCorners[posIndex] = true
					break
				}
				// Eventually try same position rotating the case
				rotate(&currentItem)
				if fit(&currentItem, pallet, packed, levelsMap) == true {
					toPack = false
					packedItem.busyCorners[posIndex] = true
					break
				}
				// Readjust the item
				rotate(&currentItem)
			}
			// If already packed we don't need to try other positions.
			if toPack == false { break }
		}
		// If all positions have been tried and the packing is not possible
		// there is no feasible solution.
		if toPack == true { return false, cases, levelsMap }
		// If currentItem has been packed add it to the list of packed
		packed = append(packed, currentItem)
	}
	return true, packed, levelsMap
}
