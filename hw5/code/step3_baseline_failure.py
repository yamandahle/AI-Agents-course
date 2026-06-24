"""
Step 3 — Baseline Failure: Too-Large Model on GPU
Demonstrates that facebook/opt-66b (~132GB FP16) cannot fit in A100 40GB VRAM.
Run this in Google Colab with an A100 GPU.
"""

from transformers import AutoModelForCausalLM
import torch, json, os
from datetime import datetime

os.makedirs("results", exist_ok=True)

# 66B model = ~132GB in FP16, clearly too big for 40GB VRAM
model_name = "facebook/opt-66b"

print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"VRAM available: 40GB")
print(f"Model size in FP16: ~132GB")
print(f"Attempting to load {model_name}...")
print("Expected to FAIL with OOM ❌")

try:
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="cuda"
    )
    print("✅ Loaded (unexpected!)")
    result = {
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "model": model_name
    }

except torch.cuda.OutOfMemoryError as e:
    print(f"❌ OUT OF MEMORY ERROR (expected!)")
    torch.cuda.empty_cache()
    result = {
        "timestamp": datetime.now().isoformat(),
        "status": "OOM_error",
        "model": model_name,
        "model_size_fp16_gb": 132,
        "available_vram_gb": 40,
        "gap_gb": 92,
        "error": str(e)
    }

except Exception as e:
    print(f"❌ Other error: {str(e)}")
    result = {
        "timestamp": datetime.now().isoformat(),
        "status": "error",
        "model": model_name,
        "error": str(e)
    }

with open("results/step3_results.json", "w") as f:
    json.dump(result, f, indent=2)

print("\n✅ Result saved to results/step3_results.json")
print(json.dumps(result, indent=2))
