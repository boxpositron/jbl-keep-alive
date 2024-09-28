import numpy as np
import pyaudio


def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave


def play_sound(wave, sample_rate=44100):
    p = pyaudio.PyAudio()

    # Open stream to play the sound
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    output=True)

    # Convert the wave data to 32-bit float and play it
    stream.write(wave.astype(np.float32).tobytes())

    # Close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == "__main__":
    frequency = 440  # A4 note (440 Hz)
    duration = 3     # 3 seconds
    sample_rate = 44100  # Standard sample rate for audio

    sine_wave = generate_sine_wave(frequency, duration, sample_rate)
    play_sound(sine_wave, sample_rate)
