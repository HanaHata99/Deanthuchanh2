import pgsql

dulieu = []

filedoc = open("cutdean.csv", "r")
rowfirst = True
for x in range(1000001):
    doc = filedoc.readline().rstrip()
    if rowfirst == True:
        rowfirst = False
        continue
    temp = doc.split(",")
    dataconvert = temp
    dataconvert[0] = int(temp[0])
    dataconvert[5] = int(temp[5])
    dataconvert[6] = float(temp[6])
    dataconvert[7] = float(temp[7])
    dataconvert[8] = float(temp[8])
    dataconvert[9] = float(temp[9])
    dataconvert[10] = int(temp[10])
    dataconvert[13] = int(temp[13])
    dataconvert[14] = float(temp[14])
    dataconvert[15] = float(temp[15])
    dataconvert[16] = float(temp[16])
    dataconvert[17] = float(temp[17])
    dataconvert[18] = float(temp[18])
    dataconvert[19] = float(temp[19])
    dulieu.append(dataconvert)
    # print(dataconvert)

filedoc.close()

print('Data loaded')

with pgsql.Connection(("localhost", 5432), "postgres", "24032003", "postgres", tls = False) as db:
     with db.transaction():
        with db.prepare("INSERT INTO dulieudean VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)") as insert_person:
            for person in dulieu:
                insert_person(*person)

    
    # with db.prepare("SELECT count (*) as dem FROM dulieudean") as people:
    #     for person in people():
    #         print(person)
    
print('Done')