package packing

import (
	"math"
	"sort"
)

// Position and Size of a case seen as arrays
type Position [3]int
type Size [3]int



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
func fit (currentItem Case, pallet *Pallet, pos Position, packed []Case) bool {
	// Check the pallet borders
	X, Y, Z := pallet.Size()
	if currentItem.Right() > X || currentItem.Back() > Y || currentItem.Top() > Z {
		return false
	}

	for _, packedItem := range packed {
		// Check intersection with other already placed cases
		if intersect(currentItem, packedItem) == true {
			return false
		}
	}
	return true
}




// Algorithm described in the following paper.
// Dube, E., Kanavathy, L. R., & Woodview, P. (2006). Optimizing Three-Dimensional
// Bin Packing Through Simulation. In Sixth IASTED International Conference Modelling,
// Simulation, and Optimization.
func DubePacker (pallet *Pallet, cases []Case) ([]Case, bool){
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
		var toPack bool = true
		// Try the three positions close to the already packed items
		// and in each position try the two possible rotations.
		// We first try floor positions for all items. The beginning of a new
		// level is the last thing we try.
		for posIndex := 0; posIndex < 3; posIndex++{
			// For each packed case
			for _, packedItem := range packed {
				// Try with the position
				pos := getPosition(posIndex, packedItem)
				setPos(&currentItem, pos)
				if fit(currentItem, pallet, pos, packed) == true {
					toPack = false
					break
				}
				// Eventually try same position rotating the case
				rotate(&currentItem)
				if fit(currentItem, pallet, pos, packed) == true {
					toPack = false
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
