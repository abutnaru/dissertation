import csv

with open("mixed_450k.csv", "r") as f:
    writer = csv.writer(open("temp.csv","w"))
    reader = csv.reader(f)
    for row in reader:
        if row[1]=="1":
            writer.writerow(row)