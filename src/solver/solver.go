package solver

import (
	. "3DCasePicking/packing"
	"math"
	"math/rand"
	"sort"
	"time"
)


// Define the beta value needed to get a greedy solution
const GREEDY_BETA float64 = 0.9999


// Define the solution type
type Solution struct {
	Pallets []*Pallet
	Cost float64
}


type Solver struct {
	orderlines []*OrderLine
	edges []*Edge
	dists [][]float64
	Best Solution
	History []float64
}


// Solver constructor
func NewSolver (orderlines []*OrderLine, edges []*Edge, dists [][]float64) *Solver {
	// Sort edges preparing the saving list
	sort.Slice(edges, func (i, j int) bool {
		return edges[i].Saving > edges[j].Saving
	})
	return &Solver{orderlines: orderlines, edges: edges, dists: dists}
}


// Method to costify a solution
// The cost of a solution is the overall distance that all the picker have to walk
func (self *Solver) getCost(pallets []*Pallet) float64 {
	var cost float64 = 0
	// For each pallet
	for _, pallet := range pallets {
		// Sort the locations/orderlines to visit for increasing layer value
		sortedOrderLinesLayer := sortMapByValue(pallet.LayersMap)
		// Calculate the legth of the path to walk
		for i := 0; i < len(sortedOrderLinesLayer) - 1; i++ {
			firstOrderLine := sortedOrderLinesLayer[i].key
			secondOrderLine := sortedOrderLinesLayer[i + 1].key
			cost += self.dists[firstOrderLine.Location][secondOrderLine.Location]
		}
		// Calculate distances to leave and go back to the I/O point
		lastPos := len(sortedOrderLinesLayer) - 1
		cost += self.dists[0][sortedOrderLinesLayer[0].key.Location]
		cost += self.dists[sortedOrderLinesLayer[lastPos].key.Location][0]
	}
	return cost
}


// Heuristic solution to the 3-Dimensional Case Picking problem
func (self *Solver) Heuristic (beta float64) Solution{
	// Generate the dummy solution
	pallets := make([]*Pallet,0)
	var p *Pallet
	for _, orderline := range self.orderlines {
		p = NewPallet()
		_, packedCases, layersMap := DubePacker(*p, orderline.Cases)
		p.Cases, p.LayersMap = packedCases, layersMap
		p.OrderLines = append(p.OrderLines, orderline)
		orderline.Pallet = p
		pallets = append(pallets, p)
		for _, c := range orderline.Cases {
			p.Volume += c.SizeX * c.SizeY * c.SizeZ
			p.Weight += c.Weight
		}
	}
	// Merging process
	var origin, destination *Pallet
	// Iterate the saving list from the edge that guarantees the maximu saving
	// to the edge that guarantees the minimum saving.
	for _, edge := range self.edges {
		// Picks origin and destination of the edge
		origin, destination = edge.Origin.Pallet, edge.Destination.Pallet
		// If origin and destination are already into the same pallet go to the next edge.
		if origin == destination {
			continue
		}
		// Preliminary lower bound controls on weight and volume
		if origin.Weight + destination.Weight > origin.MaxWeight {
			continue
		}
		if origin.Volume + destination.Volume > origin.MaxVolume {
			continue
		}

		// Try merging the destination pallet into the origin pallet
		done, packedCases, layersMap := DubePacker(*origin, destination.Cases)
		if done {
			origin.Cases = packedCases
			origin.LayersMap = layersMap
			origin.Weight += destination.Weight
			origin.Volume += destination.Volume
			origin.OrderLines = append(origin.OrderLines, destination.OrderLines...)
			pallets = remove(pallets, destination)
			for _, orderline := range destination.OrderLines {
				orderline.Pallet = origin
			}
			continue
		}

		// If the first tentative did not work, try merging the origin
		// pallet into the destination pallet.
		origin, destination = destination, origin
		done, packedCases, layersMap = DubePacker(*origin, destination.Cases)
		if done {
			origin.Cases = packedCases
			origin.LayersMap = layersMap
			origin.Weight += destination.Weight
			origin.Volume += destination.Volume
			origin.OrderLines = append(origin.OrderLines, destination.OrderLines...)
			pallets = remove(pallets, destination)
			for _, orderline := range destination.OrderLines {
				orderline.Pallet = origin
			}
		}
	}
	return Solution{Pallets: pallets, Cost: self.getCost(pallets)}
}


// Biased Randomised Algorithm that incorporates the Heuristic one
// to efficiently solve the 3-Dimensional Case Picking problem
func (self *Solver) BiasedRandomisedAlgorithm (maxTime int) Solution {
	// Initialize time variables useful to measure the execution time
	maxTimeSec := time.Duration(float64(maxTime) * math.Pow(10.0, 9)).Seconds()
	startTime := time.Now()
	currentTime := time.Now()

	// Initialize the starting solution
	var best Solution = self.Heuristic(GREEDY_BETA)
	var newSol Solution
	var history = []float64{best.Cost}
	var beta float64

	// Execute until the maxTime allowed (expressed in seconds) is not expired
	for currentTime.Sub(startTime).Seconds() < maxTimeSec {
		// Generate a uniformly random beta
		beta = 0.1 + rand.Float64() * (0.3 - 0.1)
		// Generate a new solution
		newSol = self.Heuristic(beta)
		// Eventually update the best
		if newSol.Cost < best.Cost {
			best = newSol
		}
		// Save the evolution of the algorithm
		history = append(history, best.Cost)
		// Update the execution time
		currentTime = time.Now()
	}
	// Save the best solution
	self.Best, self.History = best, history
	// Return the best solution found so far
	return best
}
