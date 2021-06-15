package packing


// Position and Size of a case seen as arrays
type Position [3]int
type Size [3]int


// Algorithm described in the following paper.
// Dube, E., Kanavathy, L. R., & Woodview, P. (2006). Optimizing Three-Dimensional
// Bin Packing Through Simulation. In Sixth IASTED International Conference Modelling,
// Simulation, and Optimization.
func DubePacker (pallet *Pallet, cases []Case) ([]Case, bool){
	var pivot = Position{0,0,0}
	
	return cases, true
}
