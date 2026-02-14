from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"

_tokenizer = None
_model = None

def _load_model():
    global _tokenizer, _model

    if _tokenizer is None or _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        _model.eval()

    return _tokenizer, _model


async def detect_intent(text: str):
    tokenizer, model = _load_model()

    prompt = f"""
You are a banking intent classifier.

Classify the user intent into one of:
- balance_check
- transfer_money
- withdraw_money
- deposit_money
- other

User input:
"{text}"

Return only the intent label.
"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=20,
            temperature=0.0
        )

    result = tokenizer.decode(output[0], skip_special_tokens=True)

    # Extract last line as intent
    intent = result.strip().split("\n")[-1].strip()

    return intent
