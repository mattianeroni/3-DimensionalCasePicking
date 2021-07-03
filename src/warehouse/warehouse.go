package warehouse

import "math"

// Define the warehouse characteristics
const LOCATION_X float64 = 1.0
const LOCATION_Y float64 = 1.0
const AISLES int = 20
const CROSS_AISLES int = 1
const AISLE_SIZE int = 3
const CROSS_AISLE_SIZE float64 = 6.0
const LOCATIONS int = 10

// Initialize the number of nodes
const NUMBER_OF_LOCATIONS int =  (LOCATIONS * (CROSS_AISLES + 1) + CROSS_AISLES + 2) * AISLES

type GraphType map[int]map[int]float64


// Build a graph of the warehouse paths
func Graph() GraphType {
	// Initialize the graph
	var G GraphType = make(GraphType)
	// Calculate cross points
	cross_points := make(map[int]int)
	old := 0
	cross_points[0] = 1
	for i := 0; i < CROSS_AISLES + 1; i++{
		cross_points[old + LOCATIONS + 1] = 1
		old += LOCATIONS + 1
	}

	// Calculate total nodes per side Y
	locations_per_longaisle := LOCATIONS * (CROSS_AISLES + 1) + CROSS_AISLES + 2

	// Populate the graph
	nodeId := 0
	for x := 0; x < AISLES; x++ {
		for y := 0; y < locations_per_longaisle; y++ {
			// Calculate the connections
			var weight float64
			if y > 0 {
				// Init the hashmap
				if _, ok := G[nodeId]; !ok { G[nodeId] = make(map[int]float64) }
				if _, ok := G[nodeId - 1]; !ok { G[nodeId - 1] = make(map[int]float64) }

				// Calculate distances
				weight = LOCATION_Y
				_, ok1 := cross_points[y]
				_, ok2 := cross_points[y - 1]
				if (ok1 && y != 0 && y != locations_per_longaisle) || (ok2 && y - 1 != 0 && y - 1 != locations_per_longaisle){
					weight = LOCATION_Y / 2 + CROSS_AISLE_SIZE / 2
				}
				G[nodeId][nodeId - 1] = weight
				G[nodeId - 1][nodeId] = weight
			}

			if _, ok := cross_points[y]; x > 0 && ok {
				// Init the hashmap
				if _, ok := G[nodeId]; !ok { G[nodeId] = make(map[int]float64) }
				if _, ok := G[nodeId - locations_per_longaisle]; !ok { G[nodeId - locations_per_longaisle] = make(map[int]float64) }
				// Calculate distances
				weight = LOCATION_X * 2
				G[nodeId][nodeId - locations_per_longaisle] = weight
				G[nodeId - locations_per_longaisle][nodeId] = weight
			}
			nodeId++
		}
	}
	return G
}


// Calculate the distance matrix using Floyd-Warshall algorithm
func DistanceMatrix (G GraphType) [][]float64 {
	// Initialize the matrix
	matrix := make([][]float64, NUMBER_OF_LOCATIONS)
	for x := 0; x < NUMBER_OF_LOCATIONS; x++ {
		matrix[x] = make([]float64, NUMBER_OF_LOCATIONS)
		for y := 0; y < NUMBER_OF_LOCATIONS; y++ {
			if x == y {
				matrix[x][y] = 0
				continue
			}
			if val, ok := G[x][y]; ok {
				matrix[x][y] = val
			} else {
				matrix[x][y] = math.Inf(1)
			}
		}
	}
	// Calculate the distances using Floyd-Warshall algorithm
	var newdist float64
	for x := 0; x < NUMBER_OF_LOCATIONS; x++ {
		for y := 0; y < NUMBER_OF_LOCATIONS; y++ {
			for p := 0; p < NUMBER_OF_LOCATIONS; p++ {
				newdist = matrix[x][p] + matrix[p][y]
				if newdist < matrix[x][y]{
					matrix[x][y] = newdist
				}
			}
		}
	}
	// Return the distance matrix
	return matrix
}
