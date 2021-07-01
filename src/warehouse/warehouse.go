package warehouse

// Define the warehouse characteristics
const LOCATION_X int = 2
const LOCATION_Y int = 2
const AISLES int = 20
const CROSS_AISLES int = 1
const AISLE_SIZE int = 3
const CROSS_AISLE_SIZE int = 6
const LOCATIONS int = 10

type GraphType map[int]map[int]int


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
			var weight int
			if y > 0 {
				// Init the hashmap
				if _, ok := G[nodeId]; !ok { G[nodeId] = make(map[int]int) }
				if _, ok := G[nodeId - 1]; !ok { G[nodeId - 1] = make(map[int]int) }

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
				if _, ok := G[nodeId]; !ok { G[nodeId] = make(map[int]int) }
				if _, ok := G[nodeId - locations_per_longaisle]; !ok { G[nodeId - locations_per_longaisle] = make(map[int]int) }
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



