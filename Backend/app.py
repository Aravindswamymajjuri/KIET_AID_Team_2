import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

# ===================== CONFIG =====================
BASE_MODEL = "google/flan-t5-base"
LORA_PATH = "./model"

device = "cuda" if torch.cuda.is_available() else "cpu"

# ===================== FASTAPI APP =====================
app = FastAPI(
    title="Healthcare Chatbot API",
    description="FLAN-T5 + LoRA Healthcare Assistant",
    version="1.0.0"
)

# ===================== LOAD MODEL =====================
print("🔄 Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

print("🔄 Loading base model...")
model = AutoModelForSeq2SeqLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)

print("🔄 Loading LoRA adapter...")
model = PeftModel.from_pretrained(model, LORA_PATH)
model = model.merge_and_unload()

model.to(device)
model.eval()

print(f"✅ Model loaded successfully on {device}")

# ===================== REQUEST / RESPONSE SCHEMA =====================
class ChatRequest(BaseModel):
    question: str
    max_length: int = 256

class ChatResponse(BaseModel):
    answer: str

# ===================== GENERATION FUNCTION =====================
def generate_answer(question: str, max_length: int):
    inputs = tokenizer(
        question,
        return_tensors="pt",
        truncation=True,
        max_length=256
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            num_beams=4,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.2
        )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# ===================== API ENDPOINTS =====================
@app.get("/")
def health_check():
    return {"status": "Healthcare Chatbot API is running"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = generate_answer(
        question=request.question,
        max_length=request.max_length
    )
    return {"answer": answer}
