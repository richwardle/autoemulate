from sklearn.model_selection import KFold
from dtemulate.experimental_design import LatinHypercube
from dtemulate.emulators import GaussianProcess, RandomForest
import numpy as np


def compare(X, y, cv=5, models=None):
    """
    Compare a list of emulators using K-fold cross-validation.

    :param X: Input data (simulation input).
    :param y: Target data (simulation output).
    :param cv: Number of folds for cross-validation.
    :param model: List of emulators to compare.
    :return: Scores
    """

    X = np.array(X)
    y = np.array(y)

    # Check X and y have same number of samples
    if X.shape[0] != y.shape[0]:
        raise ValueError("X and y must have the same number of samples.")

    # Check for NaNs
    if np.isnan(X).any() or np.isnan(y).any():
        raise ValueError("X and y should not contain NaNs.")

    scores = {}
    kfold = KFold(n_splits=cv, shuffle=True)
    if models is None:
        models = [GaussianProcess(), RandomForest()]

    for model in models:
        fold_scores = []

        for train_index, test_index in kfold.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            model.fit(X_train, y_train)
            fold_scores.append(model.score(X_test, y_test))

        # average score over folds, score is a tuple of (rsme, r2)
        scores[type(model).__name__] = sum(fold_scores) / cv

    return scores