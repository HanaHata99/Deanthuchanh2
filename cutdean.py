filedoc = open("D:\data_complete_extended.csv", "r")
filewrite = open("D:\cutdean2.csv", "w")

for x in range(10):
    doc = filedoc.readline()
    filewrite.write(doc)

print("daxong")
filewrite.close()
filedoc.close()