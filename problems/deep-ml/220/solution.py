import torch


def cross_entropy_derivative(logits: torch.Tensor, target: int) -> torch.Tensor:
    """
    Compute the derivative of cross-entropy loss with respect to logits.

    Args:
        logits: Raw model outputs tensor
        target: Index of the true class

    Returns:
        Gradient tensor
    """
    z = logits - logits.max()
    exp_z = torch.exp(z)
    p = exp_z / exp_z.sum()

    grad = p.clone()
    grad[target] -= 1.0

    return grad
