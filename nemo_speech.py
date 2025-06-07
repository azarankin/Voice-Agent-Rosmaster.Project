import os
import torch
import tempfile
import numpy as np
import soundfile as sf # soundfile storing
import sounddevice as sd #make sound ot record
from nemo_model_utils import load_asr_model, load_tts_model, load_vocoder_model, DEFAULT_SAMPLE_RATE

# ==== MAIN WRAPPER ====
class NemoSpeech:
    def __init__(self):
        print("🔁 Initializing NemoSpeech models...")
        self.transcribe_model = load_asr_model()
        self.tacotron_model = load_tts_model()
        self.vocoder_model= load_vocoder_model()
        self.tmp_wav_path = os.path.join(tempfile.gettempdir(), "nemo_tmp_audio.wav")
        print("✅ All models loaded")

    def __del__(self):
        if os.path.exists(self.tmp_wav_path):
            try:
                os.remove(self.tmp_wav_path)
                print(f"🧹 Deleted temp file: {self.tmp_wav_path}")
            except Exception as e:
                print(f"⚠️ Failed to delete temp file: {e}")


    def transcribe_audio_from_file(self, audio_file_path: str) -> str:
        transcription = self.transcribe_model.transcribe([audio_file_path])[0]
        #print(f"🗣️ Transcription: {transcription}")
        return transcription

    def transcribe_from_audio(self, audio, sr: int = DEFAULT_SAMPLE_RATE) -> str:
        audio = np.array(audio, dtype=np.float32)
        sf.write(self.tmp_wav_path, audio, sr)
        transcription = self.transcribe_model.transcribe([self.tmp_wav_path])[0]
        return transcription

    def text_to_speech(self, text: str, file_name: str = None, play: bool = False) -> np.ndarray:
        text = "\u200B " + text + "\u200B "  # Adds a zero-width space padding
        tokens = self.tacotron_model.parse(text)
        spectrogram = self.tacotron_model.generate_spectrogram(tokens=tokens)
        audio = self.vocoder_model.convert_spectrogram_to_audio(spec=spectrogram)

        if not isinstance(audio, torch.Tensor):
            audio = audio.to_tensor()

        audio_np = audio.squeeze().cpu().detach().numpy()

        #not used features
        if file_name:
            sf.write(file_name, audio_np, DEFAULT_SAMPLE_RATE)
            print(f"💾 Audio saved to: {file_name}")

        if play:
            sd.wait()
            sd.play(audio_np, DEFAULT_SAMPLE_RATE)
            sd.wait()

        return audio_np
