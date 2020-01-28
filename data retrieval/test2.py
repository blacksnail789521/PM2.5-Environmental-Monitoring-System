string = "456"

li = [1, 2]

with open("test.txt", "w") as output:
    for element in li:
        print(element)
        output.write(str(element) + "\n")