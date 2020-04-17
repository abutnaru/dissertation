#!/usr/bin/env -S conda run -n dissertation python
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
        "-m",
        "--model",
        type=str,
        dest="target",
        default="all",
        help="Model to be evaluated (Default: All)",
    )
    parser.add_argument(
        "-n",
        "--dirname",
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
    return (args.target, args.dataset, args.modelsdir)


def parse_file(filename):
    f = open("data/" + filename + ".csv", "r")
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

def is_benign(url):
    reader = csv.reader(open("data/benign_1M.csv", 'r'))
    for row in reader:
        if tld.extract(url).domain == tld.extract(row[0]).domain:
            return True
    return False

def eval_with_whitelist(model, pairs):
    TP, TN, FP, FN = 0, 0, 0, 0
    for url, url_type in pairs:
        f = features.extract(url)
        if is_benign(url):
            TN+=1
        else:
            prediction = model.predict(f.reshape(1, -1))
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
    naive_bayes = pickle.load(open("models/" + modelsdir + "/naive_bayes.sav", "rb"))
    print_metrics("Naive Bayes", evaluate(naive_bayes, parse_file(dataset)))


def eval_dt(dataset, modelsdir):
    decision_tree = pickle.load(
        open("models/" + modelsdir + "/decision_tree.sav", "rb")
    )
    print_metrics("Decision Tree", evaluate(decision_tree, parse_file(dataset)))


def eval_rf(dataset, modelsdir):
    random_forest = pickle.load(
        open("models/" + modelsdir + "/random_forest.sav", "rb")
    )
    print_metrics("Random Forest", evaluate(random_forest, parse_file(dataset)))


def eval_svm(dataset, modelsdir):
    support_vector = pickle.load(
        open("models/" + modelsdir + "/support_vector.sav", "rb")
    )
    print_metrics(
        "Support Vector Machine", evaluate(support_vector, parse_file(dataset))
    )


def eval_nn(dataset, modelsdir):
    ml_perceptron = pickle.load(
        open("models/" + modelsdir + "/ml_perceptron.sav", "rb")
    )
    print_metrics("Neural Networks", evaluate(ml_perceptron, parse_file(dataset)))


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
    naive_bayes = pickle.load(open("models/" + modelsdir + "/naive_bayes.sav", "rb"))
    print_metrics("Naive Bayes", evaluate(naive_bayes, parse_file(dataset)))
    decision_tree = pickle.load(
        open("models/" + modelsdir + "/decision_tree.sav", "rb")
    )
    print_metrics("Decision Tree", evaluate(decision_tree, parse_file(dataset)))
    random_forest = pickle.load(
        open("models/" + modelsdir + "/random_forest.sav", "rb")
    )
    print_metrics("Random Forest", evaluate(random_forest, parse_file(dataset)))
    support_vector = pickle.load(
        open("models/" + modelsdir + "/support_vector.sav", "rb")
    )
    print_metrics(
        "Support Vector Machine", evaluate(support_vector, parse_file(dataset))
    )
    ml_perceptron = pickle.load(
        open("models/" + modelsdir + "/ml_perceptron.sav", "rb")
    )
    print_metrics("Neural Networks", evaluate(ml_perceptron, parse_file(dataset)))


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
