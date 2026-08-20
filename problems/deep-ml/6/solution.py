import torch


def calculate_eigenvalues(matrix: torch.Tensor) -> torch.Tensor:
    """
    Compute eigenvalues of a 2x2 matrix using PyTorch.
    Input: 2x2 tensor; Output: 1-D tensor with the two eigenvalues in
    descending order (highest to lowest).
    """
    a, b, c, d = matrix[0, 0], matrix[0, 1], matrix[1, 0], matrix[1, 1]

    trace = a + d
    det = a * d - b * c

    disc = trace**2 - 4 * det
    sqrt_disc = torch.sqrt(disc.to(torch.float))

    lambda_1 = (trace + sqrt_disc) / 2.0
    lambda_2 = (trace - sqrt_disc) / 2.0

    return torch.stack([lambda_1, lambda_2])
