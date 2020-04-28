#!/usr/bin/env -S conda run -n dissertation python
"""
The algorithm trainer produces the machine learning models.
"""
import argparse
import csv
import os
import pickle
import sys
import time

import numpy as np
import pandas as pd
import scipy as sc
from sklearn import preprocessing
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, roc_auc_score, roc_curve, plot_roc_curve
from sklearn.model_selection import GridSearchCV, KFold, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from tqdm import tqdm
import matplotlib.pyplot as plt

ml_algorithms = [
    {"name": "Naive Bayes", "filename": "naive_bayes", "model": GaussianNB()},
    {
        "name": "Decision Tree",
        "filename": "decision_tree",
        "model": DecisionTreeClassifier(),
    },
    {
        "name": "Random Forest",
        "filename": "random_forest",
        "model": RandomForestClassifier(n_estimators=125),
    },
    {
        "name": "Support Vector Machine",
        "filename": "support_vector",
        "model": GridSearchCV(
            SVC(),
            [
                {
                    "kernel": ["rbf"],
                    "C": [1, 10, 100,1000],
                }
            ], cv=3
        ),
    },
    {
        "name": "Neural Network",
        "filename": "ml_perceptron",
        "model": MLPClassifier(hidden_layer_sizes=(2, 10), max_iter=2800)
    },
]

def parse_arguments():
    parser = argparse.ArgumentParser(description="Model trainer")
    parser.add_argument(
        "-d",
        "--dataset",
        dest="dataset",
        type=str,
        help="Target dataset",
        required=True,
    )
    parser.add_argument(
        "-id",
        "--id",
        dest="set_identifier",
        type=str,
        help="Model set identifier",
        required=True,
    )
    args = parser.parse_args()
    return (args.dataset, args.set_identifier)


def main():
    global ml_algorithms
    dataset, setid = parse_arguments()

    f_out = open(f"results/training_output/train_{dataset}.txt", "w")
    if not os.path.exists(f"models/{setid}"):
        os.makedirs(f"models/{setid}")
    else:
        sys.exit(f'A model set with the identifier "{setid}" already exists')

    X = pd.read_csv(f"features/{dataset}.csv", usecols=[*range(1, 14)])
    Y = pd.read_csv(f"features/{dataset}.csv", usecols=[0])

    # 10 fold cross-validation
    kf = KFold(n_splits=10, shuffle=True, random_state=25)
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.20, random_state=35
    )
    X = X.values
    Y = Y.values
    title = "K-fold iteration"
    i = 1
    for train, test in tqdm(kf.split(X), total=kf.get_n_splits(), desc=title):
        f_out.write(f"Iteration number {i}\n")
        i += 1
        X_train, X_test = X[train], X[test]
        y_train, y_test = Y[train], Y[test]
        # Normalizing the Sets
        scaler = preprocessing.StandardScaler().fit(X_train)
        scaler.transform(X_train)
        scaler.transform(X_test)
        
        for algo in ml_algorithms:
            print(f"Training the {algo['name']} model")
            algo["model"].fit(X_train, y_train.ravel())
            y_pred = algo["model"].predict(X_test)
            f1 = f1_score(y_test, y_pred, average="macro")
            f_out.write(f"F1 score for {algo['name']}: {f1}\n")
            plot_roc_curve(algo['model'], X_test, y_test)
            plt.savefig(f"figurator/plots/{algo['name']}_iter{i-1}_roc.png")  # doctest: +SKIP

            # average_precision = average_precision_score(y_test, y_pred)
            # disp = plot_precision_recall_curve(algo["model"], X_test, y_test)
            # disp.ax_.set_title('2-class Precision-Recall curve: '
            #       'AP={0:0.2f}'.format(average_precision))
            # plt.savefig(f"test_{algo['name']}.png")

    for algo in ml_algorithms:
        f_model = open(f"models/{setid}/{algo['filename']}.sav", "wb")
        pickle.dump(algo["model"], f_model)
        f_model.close()

    f_out.close()


if __name__ == "__main__":
    print("Model training initiated...\n")
    start = time.perf_counter()
    main()
    finish = time.perf_counter()
    print(f"\nTraining finished in {round(finish-start,2)} seconds")
