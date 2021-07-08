package main

import (
	"3DCasePicking/packing"
	solver2 "3DCasePicking/solver"
	"3DCasePicking/warehouse"
	"bufio"
	"encoding/csv"
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"time"
)


func main () {
	// Set random seed
	rand.Seed(time.Now().Unix())

	// Warehouse layout construction
	G := warehouse.Graph()
	dists := warehouse.DistanceMatrix(G)

	fmt.Println(len(dists[0]))

	// Problem import and creation
	orderlines := readfile("./test/testproblem.csv",';')
	edges := buildEdges(orderlines, dists)

	// Initialize the solver
	solver := solver2.NewSolver(orderlines, edges, dists)


	// Packing
	startTime := time.Now()
	sol := solver.Heuristic(0.2)
	endTime := time.Now()
	fmt.Println("Computational time: ", endTime.Sub(startTime).Seconds())
	fmt.Println("Number of pallets:", len(sol.Pallets))
	fmt.Println("Cost :", sol.Cost)
	fmt.Println()

	// Export results
	writefile("./test/results.csv", sol.Pallets)
}





func readfile (filename string, delimiter rune) []*packing.OrderLine {
	orderlines := make([]*packing.OrderLine, 0)

	file, err := os.Open(filename)
	if err != nil {
		panic(err)
	}

	reader := csv.NewReader(file)
	reader.Comma = delimiter
	lines, err2 := reader.ReadAll()
	if err2 != nil {
		panic(err2)
	}

	for i, line := range lines {
		if i > 0 {
			code := line[1]
			ncases, _ := strconv.ParseInt(line[2],10,64)
			sizex, _ := strconv.ParseInt(line[3],10,64)
			sizey, _ := strconv.ParseInt(line[4],10,64)
			sizez, _ := strconv.ParseInt(line[5],10,64)
			weight, _ := strconv.ParseInt(line[6],10,64)
			strength, _ := strconv.ParseInt(line[7],10,64)
			location, _ := strconv.ParseInt(line[8],10,64)

			cases := make([]packing.Case, ncases)
			orderLine := &packing.OrderLine{Code: code, Location: int(location)}
			for i := 0; i < int(ncases); i++ {
				cases[i] = packing.Case{
					Code : code,
					X : 0,
					Y : 0 ,
					Z : 0,
					SizeX : int(sizex),
					SizeY : int(sizey),
					SizeZ : int(sizez),
					Weight : int(weight),
					Strength : int(strength),
					Rotated : false,
					OrderLine: orderLine,
					CanHold: int(strength)}
			}
			orderLine.Cases = cases
			orderlines = append(orderlines, orderLine)
		}
	}
	return orderlines
}




func buildEdges (orderlines []*packing.OrderLine, dists [][]float64) []*packing.Edge{
	var cost, saving float64
	var first, second *packing.Edge
	var edges []*packing.Edge
	// Build edges connecting orderlines to I/O point
	for _, orderline := range orderlines {
		cost = dists[0][orderline.Location]
		first = &packing.Edge{Destination: orderline, Cost: cost, Saving: 0}
		second = &packing.Edge{Origin: orderline, Cost: cost, Saving: 0}
		first.Inverse = second
		second.Inverse = first
		orderline.FromDepot = first
		orderline.ToDepot = second
	}
	// Build edges connecting storage locations to each other
	for i := 0; i < len(orderlines) - 1; i++ {
		for j := i + 1; j < len(orderlines); j++ {
			firstLine := orderlines[i]
			secondLine := orderlines[j]
			cost = dists[firstLine.Location][secondLine.Location]
			saving = firstLine.ToDepot.Cost + secondLine.FromDepot.Cost - cost
			first = &packing.Edge{Origin: firstLine, Destination: secondLine, Cost: cost, Saving: saving}
			second = &packing.Edge{Origin: secondLine, Destination: firstLine, Cost: cost, Saving: saving}
			first.Inverse = second
			second.Inverse = first
			edges = append(edges, first)
		}
	}
	// Return edges
	return edges
}




func writefile(filename string, pallets []*packing.Pallet) {
	f, err := os.Create(filename)
	if err != nil {
		panic(err)
	}
	defer f.Close()

	w := bufio.NewWriter(f)
	defer w.Flush()
	w.WriteString("Stop,X,Y,Z,SizeX,SizeY,SizeZ\n")
	for _, pallet := range pallets {
		for _, item := range pallet.Cases {
			w.WriteString(fmt.Sprintf("%d,%d,%d,%d,%d,%d,%d\n", 0, item.X, item.Y, item.Z, item.SizeX, item.SizeY, item.SizeZ))
		}
		w.WriteString(fmt.Sprintf("%d,%d,%d,%d,%d,%d,%d\n", 1, 0, 0, 0, 0, 0, 0))
	}
}