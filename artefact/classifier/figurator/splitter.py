import csv

r = open("features_breakdown.csv", "r")
reader = csv.reader(r)
benign = open("benign.csv", "w")
malicious = open("malicious.csv", "w")
bwriter = csv.writer(benign)
mwriter = csv.writer(malicious)
for row in reader:
    label, features = row[0], row[1:]
    if label == "0":
        bwriter.writerow(features)
    if label == "1":
        mwriter.writerow(features)
