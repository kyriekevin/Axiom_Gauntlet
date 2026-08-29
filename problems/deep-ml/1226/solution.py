import torch


def relu(t):
    """Element-wise ReLU: max(0, t).

    Args:
        t (torch.Tensor): input tensor

    Returns:
        torch.Tensor: activated tensor
    """
    return torch.where(t > 0, t, 0.0)


def leaky_relu(t, slope=0.01):
    """Element-wise Leaky ReLU with given negative slope.

    Args:
        t (torch.Tensor): input tensor
        slope (float): slope for negative values

    Returns:
        torch.Tensor: activated tensor
    """
    return torch.where(t > 0, t, t * slope)
