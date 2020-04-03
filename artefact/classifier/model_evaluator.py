#!/usr/bin/env conda run -n dissertation python
"""
The model evaluator measures the performance of trained
model based on precision, recall, f-measure and accuracy.
"""
import argparse
import csv, pickle, re
import numpy as np
import tldextract as tld
import features_extractor as features


def parse_arguments():
    parser = argparse.ArgumentParser(description="Machine learning model evaluator")
    parser.add_argument(
        "--model",
        type=str,
        dest="target",
        default="all",
        help="Model to be evaluated (Default: All)",
    )
    parser.add_argument("--dir", dest="modelsdir", type=str, help="Models directory")
    parser.add_argument("--dataset", dest="dataset", type=str, help="Target dataset")
    args = parser.parse_args()
    return (args.target, args.dataset, args.modelsdir)


def parse_file(filename):
    f = open("data/" + filename, "r")
    pairs = []
    for row in csv.reader(f):
        try:
            pair = (row[0], float(row[1]))
            pairs.append(pair)
        except Exception as e:
            print(e)
    return pairs


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


def evaluate(model, pairs):
    TP, TN, FP, FN = 0, 0, 0, 0
    for url, url_type in pairs:
        f = features.extract(url)
        prediction = model.predict(f.reshape(1, -1))
        # print("Prediction: {} ({})\nURL Type: {} ({})".format(prediction,type(prediction),url_type,type(url_type)))

        if url_type == 1:
            if prediction == url_type:
                TP += 1
            else:
                FN += 1
        else:
            if prediction == url_type:
                TN += 1
            else:
                FP += 1
    return evaluation_metrics(TP, TN, FP, FN)


def eval_nb(dataset, modelsdir):
    naiveBayes = pickle.load(open("models/" + modelsdir + "/naiveBayes.sav", "rb"))
    print_metrics("Naive Bayes", evaluate(naiveBayes, parse_file(dataset)))


def eval_dt(dataset, modelsdir):
    decisionTree = pickle.load(open("models/" + modelsdir + "/decisionTree.sav", "rb"))
    print_metrics("Decision Tree", evaluate(decisionTree, parse_file(dataset)))


def eval_rf(dataset, modelsdir):
    randomForest = pickle.load(open("models/" + modelsdir + "/randomForest.sav", "rb"))
    print_metrics("Random Forest", evaluate(randomForest, parse_file(dataset)))


def eval_svm(dataset, modelsdir):
    svm = pickle.load(open("models/" + modelsdir + "/supportVector.sav", "rb"))
    print_metrics("Support Vector Machine", evaluate(svm, parse_file(dataset)))


def eval_nn(dataset, modelsdir):
    mlPerceptron = pickle.load(open("models/" + modelsdir + "/mlPerceptron.sav", "rb"))
    print_metrics("Neural Networks", evaluate(mlPerceptron, parse_file(dataset)))


def print_metrics(algo, m):
    print(
        """>> {} Model <<
        Precision:    {}
        Sensitivity:  {}
        F-Measure:    {}
        Accuracy:     {}
        \n-----------------------------------------------\n""".format(
            algo, m["precision"], m["sensitivity"], m["fmeasure"], m["accuracy"]
        )
    )


def eval_all(dataset, modelsdir):
    naiveBayes = pickle.load(open("models/" + modelsdir + "/naiveBayes.sav", "rb"))
    print_metrics("Naive Bayes", evaluate(naiveBayes, parse_file(dataset)))
    decisionTree = pickle.load(open("models/" + modelsdir + "/decisionTree.sav", "rb"))
    print_metrics("Decision Tree", evaluate(decisionTree, parse_file(dataset)))
    randomForest = pickle.load(open("models/" + modelsdir + "/randomForest.sav", "rb"))
    print_metrics("Random Forest", evaluate(randomForest, parse_file(dataset)))
    svm = pickle.load(open("models/" + modelsdir + "/supportVector.sav", "rb"))
    print_metrics("Support Vector Machine", evaluate(svm, parse_file(dataset)))
    mlPerceptron = pickle.load(open("models/" + modelsdir + "/mlPerceptron.sav", "rb"))
    print_metrics("Neural Networks", evaluate(mlPerceptron, parse_file(dataset)))


def run():
    target, dataset, modelsdir = parse_arguments()
    if "all" in target:
        eval_all(dataset, modelsdir)
    elif "nb" in target:
        eval_nb(dataset, modelsdir)
    elif "dt" in target:
        eval_dt(dataset, modelsdir)
    elif "rf" in target:
        eval_rf(dataset, modelsdir)
    if "svm" in target:
        eval_svm(dataset, modelsdir)
    if "nn" in target:
        eval_nn(dataset, modelsdir)


if __name__ == "__main__":
    run()
