import case
import pandas as pd


def read_problem (filename, delimiter=";"):
    df = pd.read_csv(filename, delimiter=delimiter)
    orderlines = list()
    for _, line in df.iterrows():
        orderlines.append(
            case.OrderLine(code=line["Code"], 
                           cases=tuple(case.Case(0,0,line["SizeX"],line["SizeY"],line["Height"],line["Weight"])
                                       for _ in range(line["#Cases"]))
            )
        )
    return orderlines