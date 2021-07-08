package packing

// Position and Size of a case seen as arrays (not used)
//type Position [3]int
//type Size [3]int

// The cases to pick and place
type Case struct {
	Code string
	X, Y, Z int
	SizeX, SizeY, SizeZ int
	Weight, Strength int
	Rotated bool
	OrderLine *OrderLine
	CanHold int
	busyCorners [3]bool  			// Needed to speed up the DubePacker
}

// Rotate a case in place
func rotate (c *Case){
	c.SizeX, c.SizeY = c.SizeY, c.SizeX
	c.Rotated = !c.Rotated
}


// Set the position more quickly along all axis
func setPos (c *Case, pos Position){
	c.X, c.Y, c.Z = pos[0], pos[1], pos[2]
}


// Interesting positions needed during the packing
func (self *Case) Front() int {return self.Y}
func (self *Case) Back() int {return self.Y + self.SizeY}

func (self *Case) Left() int {return self.X}
func (self *Case) Right() int {return self.X + self.SizeX}

func (self *Case) Top() int {return self.Z + self.SizeZ}
func (self *Case) Bottom() int {return self.Z }