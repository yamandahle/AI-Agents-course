import torch
import torch.nn as nn
import json
from src.services.data_generator import SignalGenerator
from src.sdk.models.mlp import MLP
from src.sdk.models.rnn import SignalRNN
from src.sdk.models.lstm import SignalLSTM

def train_model(model, x, y, epochs=200):
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()
    for epoch in range(epochs):
        optimizer.zero_grad()
        loss = criterion(model(x), y)
        loss.backward()
        optimizer.step()
        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.6f}")
    return loss.item()

if __name__ == "__main__":
    with open("config/setup.json", "r") as f:
        conf = json.load(f)
    
    gen = SignalGenerator(conf)
    x, y = gen.create_dataset()
    
    models = {
        "MLP": MLP(14, conf["models"]["mlp"]["layers"]),
        "RNN": SignalRNN(14, 128, 2),
        "LSTM": SignalLSTM(14, 256, 2)
    }
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        final_loss = train_model(model, x, y)
        print(f"{name} Final MSE: {final_loss:.6f}")
