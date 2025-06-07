import os

from dataclasses import dataclass

from nemo.collections.asr.models import EncDecCTCModel
from nemo.collections.tts.models import Tacotron2Model#, FastPitchModel
from nemo.collections.tts.models import HifiGanModel#, WaveGlowModel


# ==== CONFIGURATION ====
# For CUDA debugging: set to "1" to force synchronous kernel launches
# For performance: keep at "0" (default behavior is async)
DEBUG_CUDA = False
os.environ["CUDA_LAUNCH_BLOCKING"] = "1" if DEBUG_CUDA else "0"

#NemoSpeech
MODEL_CACHE_DIR: str = "model_cache"
# change also the model category with the model name
#for example: 
# def load_asr_model(model_name: str) -> EncDecCTCModel:
#   return load_nemo_model(EncDecCTCModel, model_name)
ASR_MODEL_CLASS = EncDecCTCModel
ASR_MODEL_NAME: str = "QuartzNet15x5Base-En"
TTS_MODEL_CLASS = Tacotron2Model
TTS_MODEL_NAME: str = "tts_en_tacotron2"
VOCODER_MODEL_CLASS = HifiGanModel
VOCODER_MODEL_NAME: str = "tts_en_hifigan"


#Rosmaster
GAMEPAD_CONTROLLER_ID = 0
EXTENSION_BOARD_ADDRESS = "/dev/ttyUSB1"



#NemoSpeech
DEFAULT_SAMPLE_RATE: int  = 22050

#PhraseToFunction
FUZZY_THRESHOLD = 85


@dataclass
class AudioSettings:
    mic_id: int = 0
    sample_rate: int = DEFAULT_SAMPLE_RATE
    silence_threshold: float = 3.5
    max_duration_sec: int = 17
    stop_after_silence_sec: float = 3.0
    pre_roll_sec: float = 0.5