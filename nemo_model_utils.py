import os
import torch
#import nemo.collections.asr as nemo_asr
#import nemo.collections.tts as nemo_tts
from config import MODEL_CACHE_DIR, ASR_MODEL_CLASS, ASR_MODEL_NAME, TTS_MODEL_CLASS, TTS_MODEL_NAME, VOCODER_MODEL_CLASS, VOCODER_MODEL_NAME, DEFAULT_SAMPLE_RATE

__all__ = [DEFAULT_SAMPLE_RATE]

# ==== MODEL LOADING and DEVICE UTILS====

from typing import Type, TypeVar
from torch.nn import Module
T = TypeVar('T', bound=Module)

def get_torch_device():
    if torch.cuda.is_available():
        print("✅ CUDA is available")
        return torch.device("cuda")
    else:
        print("⚠️ CUDA not available. Using CPU.")
        return torch.device("cpu")


def get_nemo_model_path(model_name: str) -> str:
    return os.path.join(MODEL_CACHE_DIR, model_name + ".nemo")


def load_nemo_model(the_model: Type[T], model_name: str) -> T:
    model_path = get_nemo_model_path(model_name)
    device = get_torch_device()
    if os.path.exists(model_path):
        print(f"📦 Loading model from cache: {model_path}")
        model = the_model.restore_from(model_path).to(device)
    else:
        print(f"⬇️ Downloading model: {model_name}")
        model = the_model.from_pretrained(model_name=model_name).to(device)
        model.save_to(model_path)
    return model

def load_asr_model() -> ASR_MODEL_CLASS:
    return load_nemo_model(ASR_MODEL_CLASS, ASR_MODEL_NAME)


def load_tts_model() -> TTS_MODEL_CLASS:
    return load_nemo_model(TTS_MODEL_CLASS, TTS_MODEL_NAME)


def load_vocoder_model() -> VOCODER_MODEL_CLASS:
    return load_nemo_model(VOCODER_MODEL_CLASS, VOCODER_MODEL_NAME)

def print_available_models(model_class: Type[Module]) -> None:
    print("📚 Available models:")
    for model in model_class.list_available_models():
        print(f"🔹 {model.pretrained_model_name}")

