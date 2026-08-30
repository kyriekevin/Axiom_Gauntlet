import torch


def compute_cross_entropy_loss(
    predicted_probs: torch.Tensor, true_labels: torch.Tensor, epsilon: float = 1e-15
) -> float:
    """Compute average cross-entropy loss for multi-class classification.

    Args:
        predicted_probs: Tensor of predicted probabilities (batch_size, num_classes)
        true_labels: One-hot encoded true labels (batch_size, num_classes)
        epsilon: Small value for numerical stability

    Returns:
        Average cross-entropy loss as a float
    """
    probs = torch.clamp(predicted_probs, min=epsilon, max=1.0)

    log_probs = torch.log(probs)

    ce_matrix = true_labels * log_probs

    tot_loss = -torch.sum(ce_matrix)

    batch_size = predicted_probs.shape[0]
    avg_loss = tot_loss / batch_size

    return avg_loss.item()
