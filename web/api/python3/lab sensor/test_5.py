a = [{"a" : 1, "b" : 2}, {"a" : 3, "b" : 4}, {"a" : 5, "b" : 6}]

if 4 in a:
    a.remove(4)

print(a)


print([item["a"] for item in a if item["a"] == 1])

if 1 in [item["a"] for item in a if item["a"] == 1]:
    a.remove(next(item for item in a if item["a"] == 1))


print(a)