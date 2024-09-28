from app.models import (
    FrequencyConfiguration,
    Device,
    JBLDevice
)
from app.config import JBL_DEVICE_TARGET
from app.devices import fetch_device_config
import time
import numpy as np
import logging

import pyaudio
import sounddevice as sd

from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


logger = logging.getLogger(__name__)

DeviceMap: Dict[str, JBLDevice] = {
    JBL_DEVICE_TARGET: JBLDevice.CHARGE_3
}


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


def list_audio_devices() -> List[Device]:
    p = pyaudio.PyAudio()

    devices: List[Device] = []

    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)

        device = Device(
            index=device_info["index"],
            structVersion=device_info["structVersion"],
            name=device_info["name"],
            maxInputChannels=device_info["maxInputChannels"],
            maxOutputChannels=device_info["maxOutputChannels"],
            defaultLowInputLatency=device_info["defaultLowInputLatency"],
            defaultLowOutputLatency=device_info["defaultLowOutputLatency"],
            defaultHighInputLatency=device_info["defaultHighInputLatency"],
            defaultHighOutputLatency=device_info["defaultHighOutputLatency"],
            defaultSampleRate=device_info["defaultSampleRate"]
        )

        # Check if the device name is a string
        if type(device.name) is str:
            device.name = device.name.strip()

        # Filter out non-output devices

        if type(device.maxOutputChannels) is int:
            if device.maxOutputChannels > 0:
                devices.append(device)

    p.terminate()

    return devices


def get_default_output_device() -> Device:
    # Get the default output device
    # Index 1 refers to the output device (0 for input)
    default_output_index = sd.default.device[1]
    device_info = sd.query_devices(default_output_index)

    audio_devices = list_audio_devices()

    selected_device = next(
        (device for device in audio_devices if device.index ==
         device_info["index"]),
        None)

    if not selected_device:
        raise ValueError("No default output device")

    return selected_device


def keep_alive():

    while True:
        active_device = get_default_output_device()

        active_device_name = ""

        if type(active_device.name) is str:
            active_device_name = active_device.name.strip()

        if not len(active_device_name):
            logger.error("No active audio device found")
            return

        device_model = DeviceMap.get(active_device_name, None)

        if not device_model:
            logger.error(f"Device model not found for {active_device_name}")
            return

        device = fetch_device_config(device_model)

        frequency_configuration = FrequencyConfiguration(
            frequency=device.frequency_configuration.frequency,
            duration=device.frequency_configuration.duration,
            amplitude=device.frequency_configuration.amplitude,
            sample_rate=active_device.defaultSampleRate,
        )

        wave = generate_sine_wave(
            frequency=frequency_configuration.frequency,
            duration=frequency_configuration.duration,
            sample_rate=frequency_configuration.sample_rate,
            amplitude=frequency_configuration.amplitude
        )

        logger.info(f"Playing sound at {frequency_configuration.frequency} Hz")
        play_sound(wave=wave, sample_rate=frequency_configuration.sample_rate)

        logger.info(f"Sleeping for {device.interval} seconds")
        time.sleep(device.interval)


def main() -> None:
    """
    Main function to run the application.
    """
    try:

        keep_alive()

    except KeyboardInterrupt:
        logger.info("Exiting application")
        SystemExit(0)

    except Exception as err:
        logger.error("An error occurred", exc_info=err)


if __name__ == "__main__":
    main()
