package packing


type OrderLine struct {
	Code string
	Location int
	Cases []Case
	Pallet *Pallet
	ndEdge *Edge		// Edge connecting the location to the I/O point
	dnEdge *Edge		// Edge connecting the I/O point to the location
}
