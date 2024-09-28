from typing import Dict
from enum import Enum
from app.models import (
    JBLDevice,
    DeviceConfiguration,
    FrequencyConfiguration,
)

DEVICE_CONFIGURATIONS: Dict[JBLDevice, DeviceConfiguration] = {
    JBLDevice.CHARGE_3: DeviceConfiguration(
        device_model=JBLDevice.CHARGE_3,
        interval=5,
        frequency_configuration=FrequencyConfiguration(
            frequency=10,  # 10 Hz can be used to keep this device awake
            duration=2,
            sample_rate=44100,
            amplitude=0.005
        )
    )
}


def fetch_device_config(
    device_name: JBLDevice
) -> DeviceConfiguration:

    config = DEVICE_CONFIGURATIONS.get(device_name, None)

    if config:
        return config

    raise ValueError(f"Device configuration not found for {device_name}")
