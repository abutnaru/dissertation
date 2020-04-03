import csv

f=open("mixed450k_raw.csv", 'r')
reader = csv.reader(f)
f2=open("test.csv", 'w')
writer = csv.writer(f2)
for row in reader:
    c = 0
    for item in row:
        if item =="malicious":
            c=1
    writer.writerow([row[1], c])
