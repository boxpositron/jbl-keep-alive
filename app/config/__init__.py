from os import getenv
from dotenv import load_dotenv

load_dotenv()


def load_or_throw(env_name: str) -> str:
    value = getenv(env_name)

    if value is None:
        raise Exception(f"Environment variable {env_name} is missing")

    return value


JBL_DEVICE_TARGET: str = load_or_throw("JBL_DEVICE_TARGET")
