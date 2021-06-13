import case
import pandas as pd


def read_problem (filename, delimiter=";"):
    df = pd.read_csv(filename, delimiter=delimiter)
    orderlines = list()
    for _, line in df.iterrows():
        orderlines.append(
            case.OrderLine(code=line["Code"], 
                           cases=tuple(case.Case(line["SizeX"],line["SizeY"],line["SizeZ"],line["Weight"],line["Strength"])
                                       for _ in range(line["#Cases"])),
                           location=line["Location"]
            )
        )
    return orderlines
