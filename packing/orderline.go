package packing


type OrderLine struct {
	Code byte
	Location int
	Cases []Case

	ndEdge *Edge		// Edge connecting the location to the I/O point
	dnEdge *Edge		// Edge connecting the I/O point to the location
}


// Constructor
func NewOrderLine (code byte, location int, cases []Case) OrderLine {
	return OrderLine{code, location, cases, nil, nil}
}