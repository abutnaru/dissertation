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
from sklearn.metrics import f1_score, roc_auc_score, roc_curve
from sklearn.model_selection import GridSearchCV, KFold, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from tqdm import tqdm

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
        "model": GridSearchCV(
            RandomForestClassifier(),
            [{"n_estimators": [10, 100, 500, 1000], "max_features": ["auto","log2", "sqrt"]}],
            cv=5,
        ),
    },
    {
        "name": "Support Vector Machine",
        "filename": "support_vector",
        "model": GridSearchCV(
            SVC(),
            [
                {
                    "kernel": ["poly", "rbf", "sigmoid", "linear"],
                    "C": [0.01, 0.1, 1, 10, 100, 1000],
                    "gamma": [1, 0.1, 0.01, 0.001, 0.0001],
                }
            ],
            cv=5,
        ),
    },
    {
        "name": "Neural Network",
        "filename": "ml_perceptron",
        "model": GridSearchCV(
            MLPClassifier(max_iter=2500),
            [
                {
                    "hidden_layer_sizes": [
                        (25, 50, 25),
                        (50, 50, 50),
                        (50, 100, 50),
                        (100,),
                    ],
                    "activation": ["tahn", "relu"],
                    "solver": ["sgd", "adam"],
                    "alpha": [0.0001, 0.05],
                    "learning_rate": ["constant", "adaptive"],
                }
            ],
            cv=5,
        ),
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
            algo["model"].fit(X_train, y_train.ravel())
            y_pred = algo["model"].predict(X_test)
            f1 = f1_score(y_test, y_pred, average="macro")
            f_out.write(f"F1 score for {algo['name']}: {f1}\n")

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
