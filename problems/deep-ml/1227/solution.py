import torch


def softmax(t, dim):
    """Numerically stable softmax along dim.

    Args:
        t (torch.Tensor): input tensor
        dim (int): dimension along which to apply softmax

    Returns:
        torch.Tensor: tensor of same shape as t; slices along dim sum to 1
    """
    max_t = torch.amax(t, dim=dim, keepdim=True)
    exp_t = torch.exp(t - max_t)

    sum_exp_t = torch.sum(exp_t, dim=dim, keepdim=True)

    return exp_t / sum_exp_t
