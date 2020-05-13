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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy as sc
import seaborn as sns
from sklearn import preprocessing
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    plot_roc_curve,
    roc_auc_score,
    roc_curve,
)
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
        "model": DecisionTreeClassifier(random_state=1),
    },
    {
        "name": "Random Forest",
        "filename": "random_forest",
        "model": GridSearchCV(
            RandomForestClassifier(random_state=1),
            [
                {
                    "n_estimators": [295],
                    "max_features": ["auto"],
                    "min_samples_split": [8, 12],
                    "max_depth": [15, 18, 21],
                }
            ],
            cv=5,
        ),
    },
    {
        "name": "Support Vector Machine",
        "filename": "support_vector",
        "model": GridSearchCV(
            SVC(kernel="rbf", random_state=1),
            [{"C": [1, 10, 100, 1000],}],
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
                    "activation": ["tanh", "relu"],
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


def plot_metrics(algo, i, X_test, y_test, y_pred):
    plot_roc_curve(algo["model"], X_test, y_test)
    plt.savefig(
        f"figurator/plots/{algo['name']}_iter{i-1}_roc.png"
    )  # doctest: +SKIP
    cm = confusion_matrix(y_test, y_pred)
    ax = plt.subplot()

    sns.heatmap(
        cm, annot=True, ax=ax, cmap="Greens"
    )  # annot=True to annotate cells

    # labels, title and ticks
    ax.set_xlabel("Predicted labels")
    ax.set_ylabel("True labels")
    ax.set_title("Confusion Matrix")
    ax.xaxis.set_ticklabels(["Phishing", "Benign"])
    ax.yaxis.set_ticklabels(["Phishing", "Benign"])
    ax.figure.savefig(f"figurator/plots/{algo['name']}_iter{i-1}_cm.png")
    plt.close("all")


def main():
    global ml_algorithms
    dataset, setid = parse_arguments()

    f_out = open(f"results/training_output/train_{dataset}.txt", "w")
    if not os.path.exists(f"models/{setid}"):
        os.makedirs(f"models/{setid}")
    else:
        sys.exit(f'A model set with the identifier "{setid}" already exists')

    X = pd.read_csv(f"features/{dataset}.csv", usecols=[*range(1, 12)])
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
            plot_metrics(algo, i, X_test, y_test, y_pred)

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
