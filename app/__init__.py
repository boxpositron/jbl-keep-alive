import time
import numpy as np
import pyaudio
import logging
from app.models import FrequencyConfiguration, DeviceConfiguration


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


logger = logging.getLogger(__name__)


def generate_sine_wave(
        frequency: int,
        duration: float,
        sample_rate: int,
        amplitude: float
) -> np.ndarray:
    """
    Generate a sine wave with the given frequency and duration.

    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave


def play_sound(
    wave: np.ndarray,
    sample_rate: int
):
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


def run_device(device: DeviceConfiguration):

    logger.info(f"Running device: {device.device_name}")

    frequency_configuration = device.frequency_configuration

    logger.info(
        f"Generating sine wave at {frequency_configuration.frequency} Hz")

    wave = generate_sine_wave(
        frequency=frequency_configuration.frequency,
        duration=frequency_configuration.duration,
        sample_rate=frequency_configuration.sample_rate,
        amplitude=frequency_configuration.amplitude
    )

    while True:

        logger.info(f"Playing sound at {frequency_configuration.frequency} Hz")
        play_sound(wave=wave, sample_rate=frequency_configuration.sample_rate)

        logger.info(f"Sleeping for {device.interval} seconds")
        time.sleep(device.interval)

# JBL Charge 3 - Device Configuration


device = DeviceConfiguration(
    device_name="JBL Charge 3",
    interval=5,
    frequency_configuration=FrequencyConfiguration(
        frequency=10,  # 10 Hz can be used to keep this device awake
        duration=2,
        sample_rate=44100,
        amplitude=0.5
    )
)


def main() -> None:
    """
    Main function to run the application.
    """
    try:
        run_device(device)

    except KeyboardInterrupt:
        logger.info("Exiting application")
        SystemExit(0)

    except Exception as err:
        logger.error("An error occurred", exc_info=err)


if __name__ == "__main__":
    main()
