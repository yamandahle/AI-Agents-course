import json
from src.services.experiment_runner import run_experiments, save_results

with open("config/setup.json") as f:
    config = json.load(f)

config["data"]["window_sizes"] = [10]          # fixed window size per lecture
results = run_experiments(config, fast=True)   # fast=True → 10 epochs per run
save_results(results, "outputs/results/results.json")
print(f"\nTotal results: {len(results)}")
