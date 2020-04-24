#!/usr/bin/env -S conda run -n dissertation python
"""
The model evaluator measures the performance of the target trained 
models based on precision, recall, f-measure and accuracy.
"""
import argparse
import concurrent.futures
import csv
import pickle
import re
import sys
import time

import numpy as np
import tldextract as tld
from tqdm import tqdm

import features_extractor as features


def parse_arguments():
    parser = argparse.ArgumentParser(description="Trained model evaluator")
    parser.add_argument(
        "-m",
        "--modelsdir",
        dest="modelsdir",
        type=str,
        help="Models directory",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--dataset",
        dest="dataset",
        type=str,
        help="Target dataset",
        required=True,
    )
    args = parser.parse_args()
    return (args.dataset, args.modelsdir)


def calc_precision(TP, FP):
    return TP / (TP + FP)


def calc_sensitivity(TP, FN):
    return TP / (TP + FN)


def calc_fmeasure(TP, FP, FN):
    return 2 * (
        (calc_precision(TP, FP) * calc_sensitivity(TP, FN))
        / (calc_precision(TP, FP) + calc_sensitivity(TP, FN))
    )


def calc_accuracy(TP, TN, FP, FN):
    return (TP + TN) / (TP + TN + FP + FN)


def evaluation_metrics(TP, TN, FP, FN):
    return {
        "precision": calc_precision(TP, FP),
        "sensitivity": calc_sensitivity(TP, FN),
        "fmeasure": calc_fmeasure(TP, FP, FN),
        "accuracy": calc_accuracy(TP, TN, FP, FN),
    }


def evaluate(model, processed_dataset):  # whitelist="off"
    TP, TN, FP, FN = 0, 0, 0, 0
    for line in processed_dataset:
        label = line[0]
        featureset = line[1:]
        prediction = model.predict(featureset.reshape(1, -1))
        if label == 1:
            if prediction == label:
                TP += 1
            else:
                FN += 1
        else:
            if prediction == label:
                TN += 1
            else:
                FP += 1
    return evaluation_metrics(TP, TN, FP, FN)


def write_metrics(algorithm, eval_metrics, f_out):
    f_out.write(
        f""">> {algorithm} Model <<
        Precision:    {eval_metrics["precision"]}
        Sensitivity:  {eval_metrics["sensitivity"]}
        F-Measure:    {eval_metrics["fmeasure"]}
        Accuracy:     {eval_metrics["accuracy"]}
        \n-----------------------------------------------\n\n"""
    )


def parse(file_name):
    f_in = open(f"data/processed_sets/{file_name}.csv", "r")
    return [(row[0], float(row[1])) for row in csv.reader(f_in)]


def main():
    data, modset = parse_arguments()
    f_in = open(f"data/processed_sets/{data}.csv", "r")
    dataset = [l for l in csv.reader(f_in)]
    f_in.close()
    res, processed_dataset = [], []
    print("Starting feature extraction from the target dataset")
    title = "Processing recods"
    with tqdm(total=len(dataset), desc=title, file=sys.stdout) as progressbar:
        with concurrent.futures.ProcessPoolExecutor() as e:
            for line in dataset:
                res.append(e.submit(features.extract, line[0], float(line[1])))
            for f in concurrent.futures.as_completed(res):
                processed_dataset.append(f.result())
                progressbar.update()

    models = [
        {"name": "Naive Bayes", "filename": "naive_bayes"},
        {"name": "Decision Tree", "filename": "decision_tree"},
        {"name": "Random Forest", "filename": "random_forest"},
        {"name": "Support Vector Machine", "filename": "support_vector"},
        {"name": "Neural Network", "filename": "ml_perceptron"},
    ]

    print("Starting model evaluation")
    title = "Evaluating models"
    with tqdm(total=len(models), desc=title, file=sys.stdout) as progressbar:
        f_out = open(f"results/model_evaluation/eval_{modset}_{data}.txt", "w")
        for model in models:
            f_in = open(f"models/{modset}/{model['filename']}.sav", "rb")
            m = pickle.load(f_in)
            write_metrics(model["name"], evaluate(m, processed_dataset), f_out)
            f_in.close()
            progressbar.update()
        f_out.close()


if __name__ == "__main__":
    print("Initiating model evaluation...\n")
    start = time.perf_counter()
    main()
    finish = time.perf_counter()
    print(f"\nEvaluation f_inished in {round(finish-start,2)} seconds")
