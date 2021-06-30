import operator


d = {
    1 : 0,
    2 : 7,
    5 : -1
}


print(d)
d = dict(sorted(d.items(), key=operator.itemgetter(1)))
print(d)
