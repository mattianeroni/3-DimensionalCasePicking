package packing


type Pallet struct {
	X, Y, Z   int
	MaxWeight int
	Cases []Case
}

// Useful to unpack the dimensions
func (self *Pallet) Size() (int, int, int){
	return self.X, self.Y, self.Z
}