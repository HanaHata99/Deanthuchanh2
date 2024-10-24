filedoc = open("/Volumes/Trang Kata/data_complete_extended.csv", "r")
filewrite = open("/Volumes/Trang Kata/cutdean.csv", "w")

for x in range(1000001):
    doc = filedoc.readline()
    filewrite.write(doc)

print("daxong")
filewrite.close()
filedoc.close()