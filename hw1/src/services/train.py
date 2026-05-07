import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from typing import Dict


def train_model(model: nn.Module, train_ds: Dataset,
                val_ds: Dataset, config: dict) -> Dict:
    """
    Trains model with Adam+MSE for N epochs with mini-batch gradient descent.
    Returns train/val loss history and best validation metrics.
    """
    epochs = config["training"]["epochs"]
    batch_size = config["training"]["batch_size"]
    lr = config["training"]["lr"]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)

    train_losses, val_losses = [], []
    best_val_mse = float("inf")
    best_epoch = 0

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        for x_batch, y_batch in train_loader:
            x_batch, y_batch = x_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            loss = criterion(model(x_batch), y_batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(x_batch)
        train_losses.append(epoch_loss / len(train_ds))

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for x_batch, y_batch in val_loader:
                x_batch, y_batch = x_batch.to(device), y_batch.to(device)
                val_loss += criterion(model(x_batch), y_batch).item() * len(x_batch)
        val_mse = val_loss / len(val_ds)
        val_losses.append(val_mse)

        if val_mse < best_val_mse:
            best_val_mse = val_mse
            best_epoch = epoch

    return {
        "train_losses": train_losses,
        "val_losses": val_losses,
        "best_val_mse": best_val_mse,
        "best_epoch": best_epoch,
    }
