import torch


def transpose_matrix(a) -> torch.Tensor:
    """
    Transpose a 2D matrix using PyTorch.

    Args:
        a: A 2D matrix (can be list, numpy array, or torch.Tensor)

    Returns:
        A transposed torch.Tensor
    """
    a_t = torch.as_tensor(a)

    m, n = a_t.shape
    res = torch.empty(n, m, dtype=a_t.dtype)
    for i in range(m):
        for j in range(n):
            res[j, i] = a_t[i, j]

    return res
