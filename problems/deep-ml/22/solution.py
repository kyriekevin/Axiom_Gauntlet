import torch


def sigmoid(z: float) -> float:
    """
    Compute the sigmoid activation function.
    Input:
      - z: float or torch scalar tensor
    Returns:
      - sigmoid(z) as Python float rounded to 4 decimals.
    """
    z_tensor = torch.tensor(z, dtype=torch.float)
    result = 1.0 / (1.0 + torch.exp(-z_tensor))

    return round(result.item(), 4)
