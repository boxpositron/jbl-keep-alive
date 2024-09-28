import logging
import asyncio

import pyaudio
import numpy as np

from app.devices import fetch_device_config

from app.models import (
    FrequencyConfiguration,
    Device,
    JBLDevice
)

from app.config import JBL_DEVICE_TARGET

from typing import List, Dict, TypedDict, Callable

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


logger = logging.getLogger(__name__)

DeviceMap: Dict[str, JBLDevice] = {
    JBL_DEVICE_TARGET: JBLDevice.CHARGE_3
}


def generate_sine_wave(config: FrequencyConfiguration) -> np.ndarray:
    """
    Generate a sine wave with the given frequency and duration.

    """
    sample_rate = config.sample_rate
    frequency = config.frequency
    duration = config.duration
    amplitude = config.amplitude

    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave


def play_sound(
    wave: np.ndarray,
    device: Device
):

    p = pyaudio.PyAudio()
    # Open stream to play the sound
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=device.defaultSampleRate,
                    output_device_index=device.index,
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

        try:
            device = Device(**device_info)  # type: ignore
        except Exception as err:
            logger.error(
                f"Error parsing device info: {device_info}", exc_info=err)
            continue

        # Check if the device name is a string
        device.name = device.name.strip()

        # Filter out non-output devices

        if device.maxOutputChannels > 0:
            devices.append(device)

    p.terminate()

    return devices


class KeepAliveJob(TypedDict):
    device_name: str
    callback: Callable[[], None]
    interval: int


async def run_job(job: KeepAliveJob):
    device_name = job["device_name"]
    callback = job["callback"]
    interval = job["interval"]

    logger.info(f"Starting keep alive job for {device_name}")

    while True:

        callback()
        await asyncio.sleep(interval)


def keep_alive():

    logger.info("Starting keep alive process")

    system_devices = list_audio_devices()

    jobs: List[KeepAliveJob] = []

    for system_device in system_devices:

        device_name = system_device.name

        device_model = DeviceMap.get(device_name, None)

        logger.info(f"Found device: {device_name}")

        if not device_model:
            continue

        device = fetch_device_config(device_model)

        wave = generate_sine_wave(device.frequency_configuration)

        play_sound(
            wave=wave,
            device=system_device
        )

        jobs.append(
            {
                "device_name": device_name,
                "callback": lambda: play_sound(
                    wave=wave,
                    device=system_device
                ),
                "interval": int(device.interval)
            }
        )

    loop = asyncio.get_event_loop()

    for job in jobs:
        loop.create_task(run_job(job))

    loop.run_forever()


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
