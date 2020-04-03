#!/usr/bin/env -S conda run -n dissertation python
"""
The algorithm trainer produces the machine learning models.
"""
# Machine Learning Algorithms
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier

# Model Helpers
from sklearn import preprocessing
from sklearn.model_selection import KFold, GridSearchCV, train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import f1_score, roc_curve, roc_auc_score

# Scientific Libraries
import numpy as np
import scipy as sc

# Other Libraries
import argparse
import pandas as pd
import csv, pickle


def parse_arguments():
    parser = argparse.ArgumentParser(description="Machine learning model trainer")
    parser.add_argument(
        "-d", "--dataset", dest="dataset", type=str, help="Target dataset", required=True
    )
    args = parser.parse_args()
    return args.dataset


def train_and_eval(model, params, name):
    X_train, y_train, X_test, y_test = params
    model.fit(X_train, y_train.ravel())
    y_pred = model.predict(X_test)
    f1 = f1_score(y_test, y_pred, average="macro")
    print("F1 score for {}: {}".format(name, f1))


def run():
    dataset = parse_arguments()
    X = pd.read_csv("features/" + dataset + ".csv", usecols=[*range(1, 10)])
    Y = pd.read_csv("features/" + dataset + ".csv", usecols=[0])

    # 10 fold cross-validation
    kf = KFold(n_splits=10, shuffle=True, random_state=5)
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.20, random_state=42
    )
    X = X.values
    Y = Y.values
    i = 1

    for train, test in kf.split(X):
        print("Iteration no. ", i)
        i = i + 1

        X_train, X_test = X[train], X[test]
        y_train, y_test = Y[train], Y[test]
        # Normalizing the Sets
        scaler = preprocessing.StandardScaler().fit(X_train)
        scaler.transform(X_train)
        scaler.transform(X_test)

        params = (X_train, y_train, X_test, y_test)

        naive_bayes = GaussianNB()
        train_and_eval(naive_bayes, params, "Naive Bayes")

        decision_tree = DecisionTreeClassifier()
        train_and_eval(decision_tree, params, "Decision Tree")

        random_forest = RandomForestClassifier(n_estimators=20)
        train_and_eval(random_forest, params, "Random Forest")

        svm_parameters = [{"kernel": ["rbf"], "C": [1, 10, 100, 1000]}]
        support_vector = GridSearchCV(SVC(), svm_parameters, cv=3)
        # svmModel = SVC()
        train_and_eval(support_vector, params, "Support Vector Machine")

        ml_perceptron = MLPClassifier(hidden_layer_sizes=(2, 10), max_iter=2800)
        train_and_eval(ml_perceptron, params, "Neural Network")

    # Save trained models
    pickle.dump(naive_bayes, open("models/naive_bayes.sav", "wb"))
    pickle.dump(decision_tree, open("models/decision_tree.sav", "wb"))
    pickle.dump(random_forest, open("models/random_forest.sav", "wb"))
    pickle.dump(support_vector, open("support_vector.sav", "wb"))
    pickle.dump(ml_perceptron, open("models/ml_perceptron.sav", "wb"))


if __name__ == "__main__":
    run()
