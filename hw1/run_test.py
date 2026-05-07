import json
from src.services.data_generator import build_datasets
from src.sdk.models.fc import FC
from src.sdk.models.rnn import SignalRNN
from src.sdk.models.lstm import SignalLSTM
from src.services.train import train_model

with open("config/setup.json") as f:
    config = json.load(f)

# Signal S1, low noise, window W=10
train_ds, val_ds = build_datasets(config, "low", window_size=10)

for name, model in [("FC", FC(10)), ("RNN", SignalRNN(10)), ("LSTM", SignalLSTM(10))]:
    print(f"\nTraining {name}...")
    result = train_model(model, train_ds, val_ds, config)
    print(f"{name} → best val MSE: {result['best_val_mse']:.6f} at epoch {result['best_epoch']}")
    print(f"  first loss: {result['train_losses'][0]:.6f}")
    print(f"  last  loss: {result['train_losses'][-1]:.6f}")
