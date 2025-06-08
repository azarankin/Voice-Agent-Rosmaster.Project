import sounddevice as sd
import numpy as np
import time
from scipy.io.wavfile import write
from config import DEFAULT_SAMPLE_RATE, AudioSettings

class VoiceRecorder:
    def __init__(self, mic_id = None, settings: AudioSettings = AudioSettings(), debug: bool = False):
        self.fs = settings.sample_rate
        self.mic_id = mic_id or settings.mic_id
        self.silence_threshold = settings.silence_threshold
        self.max_duration_sec = settings.max_duration_sec
        self.stop_after_sec = settings.stop_after_silence_sec
        self.pre_roll_sec = settings.pre_roll_sec
        self.channel_count = 1  # Mono recording
        self.debug = debug
        self.reset_buffers()
        self.print_input_devices()

    def record(self):
        self.reset_buffers()
        try:
            selected_device = sd.default.device[self.mic_id]
            device_info = sd.query_devices(selected_device, 'input')
            print(f"🎤 Using input device: {device_info['name']}")

            with sd.InputStream(callback=self.audio_callback,
                                channels=self.channel_count,
                                samplerate=self.fs, dtype='float32'):
                print("🎙 Please speak into the microphone...")
                start_time = time.time()
                while not self.stop_recording and (time.time() - start_time) < self.max_duration_sec:
                    time.sleep(0.1)

        except sd.PortAudioError as e:
            print(f"❌ Microphone error: {e}")
            print("📛 Check if microphone is connected or used by another app.")
            self.recording_buffer = []
            self.stop_recording = True

        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            self.recording_buffer = []
            self.stop_recording = True

    def reset_buffers(self):
        self.recording_buffer: list[np.ndarray] = []
        self.pre_roll_buffer: list[np.ndarray] = []
        self.silence_counter = 0
        self.recording_started = False
        self.stop_recording = False

    def print_input_devices(self):
        devices = sd.query_devices()
        input_devices = [f"[{i}] {d['name']}" for i, d in enumerate(devices) if d['max_input_channels'] > 0]
        print(f"🎧 Total input devices: {len(input_devices)} {input_devices}, selected = {self.mic_id}")

    def audio_callback(self, indata, frames, time_info, status):
        volume_norm = np.linalg.norm(indata) * 10
        if self.debug:
            print(f"🔈 Volume: {volume_norm:.2f} | Recording: {self.recording_started} | Silence: {self.silence_counter}")

        self.pre_roll_buffer.extend(indata.copy())
        max_pre_len = int(self.pre_roll_sec * self.fs)
        if len(self.pre_roll_buffer) > max_pre_len:
            self.pre_roll_buffer = self.pre_roll_buffer[-max_pre_len:]

        if volume_norm > self.silence_threshold and not self.recording_started:
            self.recording_started = True
            self.recording_buffer.extend(self.pre_roll_buffer)
            self.pre_roll_buffer.clear()
            self.silence_counter = 0

        if self.recording_started:
            self.recording_buffer.extend(indata.copy())
            if volume_norm < self.silence_threshold:
                self.silence_counter += 1
            else:
                self.silence_counter = 0

            if self.silence_counter > int(self.stop_after_sec * self.fs / frames):
                self.stop_recording = True

    def save_to_file(self, path: str = 'output.wav'):
        if not self.recording_buffer:
            print("⚠️ No speech recorded.")
            return

        audio = np.array(self.recording_buffer, dtype=np.float32)
        write(path, self.fs, audio)
        print(f"💾 Audio saved to {path}")

    def play(self, array: np.ndarray = None):
        if array is None:
            if not self.recording_buffer:
                print("⚠️ No recording to play.")
                return
            array = np.array(self.recording_buffer, dtype=np.float32)
        sd.play(array, self.fs)
        sd.wait()

    def get_audio(self) -> np.ndarray:
        return np.array(self.recording_buffer, dtype=np.float32)
