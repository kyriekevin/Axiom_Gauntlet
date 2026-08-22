import torch


def to_float_tensor(values):
    res = torch.tensor(values, dtype=torch.float32)

    return res
