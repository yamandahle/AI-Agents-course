@echo off
echo ── HW5 Setup: AirLLM Environment ──

cd /d C:\Users\ASUS\Desktop\AI-Agents-course\hw5

echo Step 1: Create virtual environment (Python 3.11)
uv venv .venv --python 3.11

echo Step 2: Activate virtual environment
call .venv\Scripts\activate

echo Step 3: Install PyTorch CPU-only
pip install torch --index-url https://download.pytorch.org/whl/cpu

echo Step 4: Install AirLLM and other dependencies
pip install transformers airllm psutil huggingface_hub

echo.
echo Done! Virtual environment is ready.
echo To activate next time run:  .venv\Scripts\activate
pause
