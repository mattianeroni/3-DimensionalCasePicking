package main


func main () {
  
  
}





func readfile (filename string) []packing.OrderLine {
	orderlines := make([]packing.OrderLine, 0)

	file, err := os.Open(filename)
	if err != nil {
		panic(err)
	}

	r, err2 := csv.NewReader(file).ReadAll()
	if err2 != nil {
		panic(err2)
	}

	for i, line := range r {
		if i > 0 {
			code, _ := strconv.ParseInt(line[0],10,64)
			ncases, _ := strconv.ParseInt(line[2],10,64)
			sizex, _ := strconv.ParseInt(line[3],10,64)
			sizey, _ := strconv.ParseInt(line[4],10,64)
			height, _ := strconv.ParseInt(line[5],10,64)
			weight, _ := strconv.ParseInt(line[6],10,64)

			cases := make([]packing.Case, ncases)
			for i := 0; i < int(ncases); i++ {
				cases[i] = packing.Case{0,0,int(sizex), int(sizey), int(height),int(weight)}
			}

			orderlines = append(orderlines, packing.OrderLine{int(code), cases})
			fmt.Println(line)
		}
	}

	return orderlines
}
