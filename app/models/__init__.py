from enum import Enum
from pydantic import BaseModel
from typing_extensions import Annotated

DEFAULT_SAMPLE_RATE: int = 44100
DEFAULT_AMPLITUDE: float = 0.5


class FrequencyConfiguration(BaseModel):
    frequency: Annotated[int, "Frequency in Hz"]
    duration: Annotated[float, "Duration in seconds"]
    sample_rate: Annotated[int, "Sample rate in Hz"] = DEFAULT_SAMPLE_RATE
    amplitude: Annotated[float, "Amplitude of the wave"] = DEFAULT_AMPLITUDE


class JBLDevice(str, Enum):
    CHARGE_3 = "JBL Charge 3"


class DeviceConfiguration(BaseModel):
    device_model: Annotated[JBLDevice, "Model of the device"]
    interval: Annotated[float, "Interval in seconds"]
    frequency_configuration: Annotated[
        FrequencyConfiguration,
        "Frequency configuration"
    ]


class Device(BaseModel):
    index: int
    structVersion: int
    name: str
    maxInputChannels: int
    maxOutputChannels: int
    defaultLowInputLatency: float
    defaultLowOutputLatency: float
    defaultHighInputLatency: float
    defaultHighOutputLatency: float
    defaultSampleRate: int
