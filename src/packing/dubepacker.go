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



// Sum elements in an array
func sumArray(arr... int) int {
	var res int = 0
	for _, i := range arr {res += i}
	return res
}


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


// This method verifies if it is possible to place the currentItem in a given position.
// The method needs to iterate all the list of already packed items to avoid overlaps
// or intersections.
// It also verifies the stability of cases, the vertical support, and the strength constraint.
func fit (currentItem *Case, pallet Pallet, packed []Case) bool {
	// Check the pallet borders
	X, Y, Z := pallet.Size()
	if currentItem.Right() > X || currentItem.Back() > Y || currentItem.Top() > Z {
		return false
	}
	// Initialize the stable surface and the stable corners of the currentItem
	// In a feasible packing, a case must have 3 out of 4 corners, or,
	// alternatively, the 70% of its surface lying on a case underneath.
	var stableSurface float64 = 0
	var stableCorners = []int{0,0,0,0}  // To use as boolean
	var stable bool = false
	itemSurface := float64(currentItem.SizeX * currentItem.SizeY)

	// Identify the corners that need to be supported
	var footholds = [4]Position{
		{currentItem.X, currentItem.Y, currentItem.Z},
		{currentItem.Left(), currentItem.Back(), currentItem.Z},
		{currentItem.Right(), currentItem.Back(), currentItem.Z},
		{currentItem.Right(), currentItem.Front(), currentItem.Z}}


	for _, packedItem := range packed {
		// Check intersection with other already placed cases
		if intersect(*currentItem, packedItem) == true {
			return false
		}

		// Check if the currentItem has physical support
		if currentItem.Z == 0 && !stable{
			// If the currentItem is on the floor and has no intersections
			// the placement is feasible.
			stableSurface = itemSurface
			stableCorners = []int{1, 1, 1, 1}
			stable = true
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
						}
					}
					// Define the layer of the currentItem.
					if currentItem.Code == packedItem.Code {
						currentItem.Layer = packedItem.Layer
					} else {
						currentItem.Layer = packedItem.Layer + 1
					}
					// If one of the stability conditions are met, mark the currentItem as stable.
					if stableSurface/itemSurface > MIN_STABLE_SURFACE || sumArray(stableCorners...) >= MIN_STABLE_CORNERS {
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
func DubePacker (pallet Pallet, cases []Case) ([]Case, bool){
	// Initialize the pivot in the bottom-left-front corner
	var pivot = Position{0,0,0}
	X, Y, Z := pallet.Size()
	var packed = make([]Case, 0)

	// Sort cases for decreasing strength
	sort.Slice(cases, func(i, j int) bool {
		return cases[i].Strength > cases[j].Strength
	})

	// Place the first item
	var currentItem Case = cases[0]
	currentItem.busyCorners = [3]bool{false, false, false}
	setPos(&currentItem, pivot)
	packed = append(packed, currentItem)

	// Interrupt immediately if the packing is already not feasible
	if currentItem.Top() > Z {
		return cases, false
	}
	if currentItem.Right() > X || currentItem.Back() > Y {
		rotate(&currentItem)
		if currentItem.Right() > X || currentItem.Back() > Y {
			return cases, false
		}
	}

	// For each item to pack
	for _, currentItem := range cases[1:]{
		currentItem.busyCorners = [3]bool{false, false, false}
		var toPack bool = true
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
				pos := getPosition(posIndex, packedItem)
				setPos(&currentItem, pos)
				if fit(&currentItem, pallet, packed) == true {
					toPack = false
					packedItem.busyCorners[posIndex] = true
					break
				}
				// Eventually try same position rotating the case
				rotate(&currentItem)
				if fit(&currentItem, pallet, packed) == true {
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
		if toPack == true { return cases, false }
		// If currentItem has been packed add it to the list of packed
		packed = append(packed, currentItem)
	}
	return packed, true
}
