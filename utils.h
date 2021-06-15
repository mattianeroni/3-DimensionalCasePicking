#ifndef UTILS_H
#define UTILS_H
#include <iostream>

// Plot a set of things
template<class... Args>
void print(Args... args)
{
    (std::cout << ... << args) << "\n";
}



// Read a csv file
vector<OrderLine> readfile (std::string filename){
    vector<OrderLine> result;
    std::ifstream file(filename);
    string line, val;
    int lineid = 0;

    if(!file.is_open())
        throw runtime_error("Cannot open file.");

    while (getline(file, line)){
        if (lineid > 0){
            stringstream ss (line);
            vector<int> row;
            vector<Case> cases;

            while (getline(ss, val, ';'))
                row.push_back(stoi(val));

            for (int i = 0; i < row[1]; i++){
                cases.push_back(Case(row[2], row[3], row[4], row[5], 0));
            }
            result.push_back(OrderLine(row[0], cases));
        }
        lineid++;
    }
    file.close();
    return result;
}



#endif
