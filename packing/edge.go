package packing


type Edge struct {
	Origin OrderLine
	Destination OrderLine
	Cost int
	Saving int
}
