"""
Indices module
==============

This module defines the `Indices` class, which encapsulates a set of row-column indices 
for managing subsets of data in datasets and sparse matrices.
"""

from __future__ import annotations

from typing import Set, Tuple, Union

import numpy as np
import scipy.sparse as sp
from NEGradient_GenePriority.preprocessing.utils import from_indices


class Indices:
    """
    Encapsulates a set of indices for a dataset.

    This class is designed to manage a collection of row-column indices representing a subset
    of a dataset. It provides methods to retrieve the corresponding data from a given sparse
    matrix, as well as a set representation for efficient operations. Additionally, it supports
    merging multiple indices.

    Attributes:
        indices (np.ndarray): A 2D array of shape (n, 2), where each row represents
                              a (row, column) pair of indices.
    """

    def __init__(self, indices: np.ndarray) -> None:
        """
        Initializes the Indices object with the given array of indices.

        Args:
            indices (np.ndarray): A 2D array of shape (n, 2) containing row-column pairs.
        """
        assert isinstance(indices, np.ndarray), f"Wrong type: {type(indices)}"
        assert (
            indices.ndim == 2 and indices.shape[1] == 2
        ), "indices must be a 2D array with shape (n, 2)."
        self.indices: np.ndarray = indices

    @property
    def indices_set(self) -> Set[Tuple[int, int]]:
        """
        Converts the indices into a set of (row, column) tuples.

        Returns:
            Set[Tuple[int, int]]: A set of (row, column) tuples for the indices.
        """
        return set(zip(self.indices[:, 0], self.indices[:, 1]))

    def __getitem__(self, key: Union[int, slice]) -> Union[np.ndarray, Tuple[int, int]]:
        """
        Retrieves a specific index or a slice of indices.

        Args:
            key (Union[int, slice]): The index or slice to retrieve.

        Returns:
            Union[np.ndarray, Tuple[int, int]]: A single index as a tuple, or a slice of indices.
        """
        return self.indices[key]

    def get_data(self, dataset_matrix: sp.coo_matrix) -> sp.csr_matrix:
        """
        Retrieves the subset of the dataset corresponding to the stored indices.

        Args:
            dataset_matrix (sp.coo_matrix): The full dataset represented as a COO sparse matrix.

        Returns:
            sp.csr_matrix: A sparse matrix in CSR format containing only the elements
                           specified by the indices. The shape of the returned matrix
                           matches the shape of the original dataset.
        """
        return from_indices(dataset_matrix, self.indices_set).tocsr()

    def merge(self, indices: Indices) -> Indices:
        """
        Merges another Indices object into the current one.

        Args:
            indices (Indices): Another Indices object to merge.

        Returns:
            Indices: A new instance of Indices with merged indices.
        """
        merged_indices = np.vstack((self.indices, indices.indices))
        return Indices(merged_indices)

    def mask(self, data: np.ndarray) -> np.ndarray:
        """
        Applies a mask over the indices to extract the relevant elements from a 2D array.

        Args:
            data (np.ndarray): The data to mask. It must have the same shape as the dataset
                               from which the indices were extracted.

        Returns:
            np.ndarray: A 1D array of elements from `data` corresponding to the stored indices.
        """
        rows, cols = zip(*self.indices.tolist())
        return data[np.array(rows), np.array(cols)]
