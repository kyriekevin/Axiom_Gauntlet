import torch


def calculate_matrix_mean(matrix, mode: str) -> torch.Tensor:
    """
    Calculate mean of a 2D matrix per row or per column using PyTorch.
    Inputs can be Python lists, NumPy arrays, or torch Tensors.
    Returns a 1-D tensor of means or raises ValueError on invalid mode.
    """
    a_t = torch.as_tensor(matrix, dtype=torch.float)

    n, m = a_t.shape
    if mode == "row":
        return torch.einsum("ij->i", a_t) / m
    elif mode == "column":
        return torch.einsum("ij->j", a_t) / n
    else:
        raise ValueError(f"Invalid mode: '{mode}'")
