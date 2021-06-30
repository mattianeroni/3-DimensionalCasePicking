package main

import (
	"3DCasePicking/packing"
	"bufio"
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
	"time"
)




func main () {
	orderlines := readfile("./test/testproblem.csv",';')
	cases := make([]packing.Case, 0)
	pallet := packing.Pallet{X: 200, Y: 150, Z: 200, MaxWeight: 1000}


	for _, or := range orderlines {
		cases = append(cases, or.Cases...)
	}

	startTime := time.Now()
	packedCases, done := packing.DubePacker(pallet, cases)
	endTime := time.Now()
	fmt.Println("Computational time: ", endTime.Sub(startTime).Seconds())
	for i := 0; i < 1000; i++ {
		startTime := time.Now()
		packedCases, done = packing.DubePacker(pallet, cases)
		endTime := time.Now()
		fmt.Println("Computational time: ", endTime.Sub(startTime).Seconds())
	}


	fmt.Println("Feasible :", done)


	writefile("./test/results.csv", packedCases)
}





func readfile (filename string, delimiter rune) []packing.OrderLine {
	orderlines := make([]packing.OrderLine, 0)

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
					Layer : 0,
					CanHold: int(strength)}
			}
			orderlines = append(orderlines, packing.OrderLine{Code: code, Location: int(location), Cases:cases})
		}
	}
	return orderlines
}




func writefile(filename string, cases []packing.Case) {
	f, err := os.Create(filename)
	if err != nil {
		panic(err)
	}
	defer f.Close()

	w := bufio.NewWriter(f)
	defer w.Flush()
	w.WriteString("X,Y,Z,SizeX,SizeY,SizeZ\n")
	for _, item := range cases {
		w.WriteString(fmt.Sprintf("%d,%d,%d,%d,%d,%d\n", item.X, item.Y, item.Z, item.SizeX, item.SizeY, item.SizeZ))
	}

}