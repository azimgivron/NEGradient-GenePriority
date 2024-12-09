"""
Evaluation module
=======================

Defines the `Evaluation` class for storing and managing evaluation metrics 
such as ROC curve data, AUC loss, and BEDROC scores.
"""

from typing import Dict, List, Tuple

import numpy as np
from sklearn import metrics

from NEGradient_GenePriority.evaluation.metrics import bedroc_score
from NEGradient_GenePriority.evaluation.results import Results


class Evaluation:
    """
    Represents the evaluation metrics for model predictions.

    Attributes:
        results (List[Results]): List of results, each corresponding to the results
            of a fold/split.
        alphas (List[float]): Alpha values for computing BEDROC scores.
        alpha_map (Dict[float, str]): Mapping of alpha values to descriptive labels.
    """

    alphas: List[float]
    alpha_map: Dict[float, str]

    def __init__(self, results: List[Results]):
        """
        Initializes the Evaluation with model results and parameters.

        Args:
            results (List[Results]): List of results, each corresponding to the
                results of a fold/split.
        """
        for i, result in enumerate(results):
            if not isinstance(result, Results):
                raise TypeError(
                    f"Invalid type at index {i}: Expected `Results`, but got {type(result)}. "
                    "Ensure all elements in the `results` list are instances of the "
                    "`Results` class."
                )
        self.results = results

    def compute_bedroc_scores(self) -> np.ndarray:
        """
        Computes BEDROC scores for the given alpha values.

        Returns:
            np.ndarray: Computed BEDROC scores. Shape is (folds, alphas).
        """
        scores = np.array(
            [
                [
                    bedroc_score(*result_per_fold, decreasing=True, alpha=alpha)
                    for alpha in self.alphas
                ]
                for result_per_fold in self.results
            ]
        )
        return scores

    def compute_avg_auc_loss(self) -> float:
        """
        Computes the average AUC loss (1 - AUC).

        Returns:
            Tuple[float, float]: The computed mean and standard
                deviation of the AUC loss.
        """
        auc_loss = [
            1 - metrics.roc_auc_score(*result_per_fold)
            for result_per_fold in self.results
        ]
        return np.mean(auc_loss), np.std(auc_loss)

    def compute_roc_curve(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes the ROC curve metrics (FPR, TPR).

        Returns:
            Tuple[np.ndarray, np.ndarray]:
                - False Positive Rates (FPR).
                - True Positive Rates (TPR).
        """
        fpr = []
        tpr = []
        nb_th = np.inf
        for result_per_fold in self.results:
            fpr_fold, tpr_fold, threshold = metrics.roc_curve(
                *result_per_fold, pos_label=1, drop_intermediate=True
            )
            fpr.append(fpr_fold)
            tpr.append(tpr_fold)
            nb_th = min(nb_th, len(threshold))
        fpr = np.mean([elem[:nb_th] for elem in fpr], axis=0)
        tpr = np.mean([elem[:nb_th] for elem in tpr], axis=0)
        return fpr, tpr
