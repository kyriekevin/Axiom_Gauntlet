import torch


def matrix_dot_vector(a, b) -> torch.Tensor:
    """
    Compute the product of matrix `a` and vector `b` using PyTorch.
    Inputs can be Python lists, NumPy arrays, or torch Tensors.
    Returns a 1-D tensor of length m, or tensor(-1) if dimensions mismatch.
    """
    a_t = torch.as_tensor(a, dtype=torch.float)
    b_t = torch.as_tensor(b, dtype=torch.float)
    # Dimension mismatch check
    if a_t.size(1) != b_t.size(0):
        return torch.tensor(-1)
    # Your implementation here

    n, m = a_t.shape
    result = torch.zeros(n, dtype=torch.float)

    for i in range(n):
        row_sum = 0.0
        for j in range(m):
            row_sum += a_t[i, j] * b_t[j]
        result[i] = row_sum

    return result
