#ifndef INC_3DCASEPICKING_CASE_H
#define INC_3DCASEPICKING_CASE_H


class Case {

    int x, y, z;
    int sizex, sizey, sizez;
    int weight, strength;

    // Destructor
    ~Case() = default;

    // Constructor
    Case(int sizex, sizey, sizez, weight, strength) :
    x(0), y(0), z(0),
    sizex(sizex), sizey(sizey), sizez(sizez),
    weight(weight), strength(strength){}

    // Rotate the case in-place
    void rotate()
    {
        int buffer = sizex;
        this->sizex = this->sizey;
        this->sizey = buffer;
    }

    // Sides of the case
    int front(){return y;}
    int back(){return y + sizey;}
    int left(){return x;}
    int right(){return x + sizex;}
    int bottom(){return z;}
    int top(){return z + sizez;}

};


// Rotate a case
void rotate (Case& c)
{
    int buffer = c.sizex;
    c.sizex = c.sizey;
    c.sizey = buffer;
}

#endif
