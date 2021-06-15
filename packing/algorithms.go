package packing

import "sort"

// Position and Size of a case seen as arrays
type Position [3]int
type Size [3]int


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

	for _, c := range cases[1:]{
		currentItem = c
		
	}


	
	return cases, true
}
