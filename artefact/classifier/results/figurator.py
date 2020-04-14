import csv
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from numpy import median


def plot_hamming5k_on_phishtank_0401():
    ham5k = pd.DataFrame(
        [
            ["Precision", 1, 1, 1, 1, 1],
            ["Sensitivity", 0.818, 0.930, 0.944, 0.936, 1],
            ["F-Measure", 0.900, 0.964, 0.971, 0.967, 1],
            ["Accuracy", 0.818, 0.930, 0.944, 0.936, 1],
        ],
        columns=["Metric", "NB", "DT", "RF", "SVM", "MLP"],
    )
    data = ham5k.melt("Metric")
    plot = sns.catplot(
        y="value", x="variable", hue="Metric", data=data, palette="pastel", kind="bar"
    )
    plot.savefig("hamming5k_on_phishtank_0401.png")


def plot_hamming5k_on_phishtank_0405():
    ham5k = pd.DataFrame(
        [
            ["Precision", 1, 1, 1, 1, 1],
            ["Sensitivity", 0.829, 0.935, 0.947, 0.939, 1],
            ["F-Measure", 0.906, 0.966, 0.973, 0.969, 1],
            ["Accuracy", 0.829, 0.935, 0.947, 0.939, 1],
        ],
        columns=["Metric", "NB", "DT", "RF", "SVM", "MLP"],
    )
    data = ham5k.melt("Metric")
    plot = sns.catplot(
        y="value", x="variable", hue="Metric", data=data, palette="pastel", kind="bar"
    )
    plot.savefig("hamming5k_on_phishtank_0405.png")


def plot_hamming5k_on_mixed():
    ham5k = pd.DataFrame(
        [
            ["Precision", 0.219, 0.250, 0.245, 0.241, 0.231],
            ["Sensitivity", 0.762, 0.944, 0.950, 0.929, 1],
            ["F-Measure", 0.341, 0.396, 0.390, 0.382, 0.376],
            ["Accuracy", 0.316, 0.333, 0.310, 0.304, 0.231],
        ],
        columns=["Metric", "NB", "DT", "RF", "SVM", "MLP"],
    )
    data = ham5k.melt("Metric")
    plot = sns.catplot(
        y="value", x="variable", hue="Metric", data=data, palette="pastel", kind="bar"
    )
    plot.savefig("hamming5k_on_mixed.png")


def plot_hamming25k_on_phishtank_0401():
    ham5k = pd.DataFrame(
        [
            ["Precision", 1, 1, 1, 1, 1],
            ["Sensitivity", 0.281, 0.770, 0.784, 0.788, 0.712],
            ["F-Measure", 0.439, 0.870, 0.879, 0.882, 0.831],
            ["Accuracy", 0.281, 0.770, 0.784, 0.788, 0.712],
        ],
        columns=["Metric", "NB", "DT", "RF", "SVM", "MLP"],
    )
    data = ham5k.melt("Metric")
    plot = sns.catplot(
        y="value", x="variable", hue="Metric", data=data, palette="pastel", kind="bar"
    )
    plot.savefig("hamming25k_on_phishtank_0401.png")


def plot_hamming25k_on_phishtank_0405():
    ham5k = pd.DataFrame(
        [
            ["Precision", 1, 1, 1, 1, 1],
            ["Sensitivity", 0.288, 0.768, 0.783, 0.791, 0.726],
            ["F-Measure", 0.447, 0.868, 0.878, 0.883, 0.841],
            ["Accuracy", 0.288, 0.768, 0.783, 0.791, 0.726],
        ],
        columns=["Metric", "NB", "DT", "RF", "SVM", "MLP"],
    )
    data = ham5k.melt("Metric")
    plot = sns.catplot(
        y="value", x="variable", hue="Metric", data=data, palette="pastel", kind="bar"
    )
    plot.savefig("hamming25k_on_phishtank_0405.png")


def plot_hamming25k_on_mixed():
    ham5k = pd.DataFrame(
        [
            ["Precision", 0.693, 0.389, 0.391, 0.361, 0.371],
            ["Sensitivity", 0.233, 0.819, 0.843, 0.830, 0.785],
            ["F-Measure", 0.348, 0.528, 0.534, 0.504, 0.504],
            ["Accuracy", 0.798, 0.660, 0.658, 0.621, 0.642],
        ],
        columns=["Metric", "NB", "DT", "RF", "SVM", "MLP"],
    )
    data = ham5k.melt("Metric")
    plot = sns.catplot(
        y="value", x="variable", hue="Metric", data=data, palette="pastel", kind="bar"
    )
    plot.savefig("hamming25k_on_mixed.png")


def main():
    plot_hamming5k_on_phishtank_0401()
    plot_hamming5k_on_phishtank_0405()
    plot_hamming5k_on_mixed()
    plot_hamming25k_on_phishtank_0401()
    plot_hamming25k_on_phishtank_0405()
    plot_hamming25k_on_mixed()


main()
