package main

import (
	"3DCasePicking/packing"
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
)


func main () {

	readfile("./test/testproblem.csv",';')
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
		fmt.Println(line)
		if i > 0 {
			code, _ := strconv.ParseInt(line[1],10,64)
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
					X : 0,
					Y : 0 ,
					Z : 0,
					SizeX : int(sizex),
					SizeY : int(sizey),
					SizeZ : int(sizez),
					Weight : int(weight),
					Strength : int(strength),
					Rotated : false}
			}

			orderlines = append(orderlines, packing.NewOrderLine(byte(code), int(location), cases))
			//fmt.Println(line)
		}
	}

	return orderlines
}
