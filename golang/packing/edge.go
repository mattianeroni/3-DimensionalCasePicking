package packing


type Edge struct {
	Origin *OrderLine
	Destination *OrderLine
	Cost float64
	Saving float64
	Inverse *Edge
}
