import pgsql

filedoc = open("cutdean", "r")
for x in range(1000001):
    doc = filedoc.readline()

dulieu = [("Wallace", 1986), ("Keith", 1959), ("Lianne", 1960)]


with pgsql.Connection(("localhost", 5432), "postgres", "12345", "postgres", tls = False) as db:
     with db.transaction():
        with db.prepare("INSERT INTO abc123 VALUES ($1, $2)") as insert_person:
            for person in dulieu:
                insert_person(*person)

    
    # with db.prepare("SELECT count (*) as dem FROM dulieudean") as people:
    #     for person in people():
    #         print(person)
