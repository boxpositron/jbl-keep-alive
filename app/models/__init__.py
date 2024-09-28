from pydantic import BaseModel
from typing_extensions import Annotated

DEFAULT_SAMPLE_RATE: int = 44100
DEFAULT_AMPLITUDE: float = 0.5


class FrequencyConfiguration(BaseModel):
    frequency: Annotated[int, "Frequency in Hz"]
    duration: Annotated[float, "Duration in seconds"]
    sample_rate: Annotated[int, "Sample rate in Hz"] = DEFAULT_SAMPLE_RATE
    amplitude: Annotated[float, "Amplitude of the wave"] = DEFAULT_AMPLITUDE


class DeviceConfiguration(BaseModel):
    device_name: Annotated[str, "Name of the device"]
    interval: Annotated[float, "Interval in seconds"]
    frequency_configuration: Annotated[
        FrequencyConfiguration,
        "Frequency configuration"
    ]
