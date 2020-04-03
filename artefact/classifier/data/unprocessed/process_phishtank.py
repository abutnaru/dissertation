import argparse
import json, csv

def parse_arguments():
    parser = argparse.ArgumentParser(description="Phishtank data preprocessor")
    parser.add_argument("--dataset", dest="dataset", type=str, help="Target dataset")
    args = parser.parse_args()
    return args.dataset

def main():
    target = parse_arguments()
    phishes = json.load(target)
    out_file = open('phishtank_processed.csv', 'w')
    writer=csv.writer(out_file)
    for phish in phishes:
        writer.writerow([phish['url'], 1])
    print("Phishtank data parsed successfully")