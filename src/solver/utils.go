package solver

import (
	"3DCasePicking/packing"
	"errors"
	"sort"
)


type kv struct {
	key   *packing.OrderLine
	value int
}


func sortMapByValue (myMap map[*packing.OrderLine]int) []kv {
	// Put elements inside map in a Slice
	var s []kv
	for k, v := range myMap {
		s = append(s, kv{k, v})
	}
	// Sort Slice
	sort.Slice(s, func(i, j int) bool {
		return s[i].value < s[j].value
	})
	// Return sorted Slice
	return s
}



func remove (s []*packing.Pallet, toRemove *packing.Pallet) []*packing.Pallet {
	var index int = -1
	for i, pallet := range s {
		if pallet == toRemove {
			index = i
			break
		}
	}
	if index == -1 {
		panic(errors.New("Element not found."))
	}
	return append(s[:index], s[index + 1:]...)
}