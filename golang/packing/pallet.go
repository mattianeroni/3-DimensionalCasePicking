package packing

// Define the standard dimensions of the pallets
const PALLET_X int = 120
const PALLET_Y int = 80
const PALLET_Z int = 150
const PALLET_WEIGHT int = 450


type Pallet struct {
	X, Y, Z   int
	MaxWeight, MaxVolume int
	Weight, Volume int
	Cases []Case
	LayersMap map[*OrderLine]int
	OrderLines []*OrderLine
}

// Constructor
func NewPallet() *Pallet {
	return &Pallet{X: PALLET_X, Y: PALLET_Y, Z: PALLET_Z,
		MaxWeight: PALLET_WEIGHT, MaxVolume: PALLET_X * PALLET_Y * PALLET_Z,
		Cases: make([]Case,0), LayersMap: make(map[*OrderLine]int), OrderLines: make([]*OrderLine,0),
		Weight: 0, Volume: 0}
}

// Useful to unpack the dimensions
func (self *Pallet) Size() (int, int, int){
	return self.X, self.Y, self.Z
}
