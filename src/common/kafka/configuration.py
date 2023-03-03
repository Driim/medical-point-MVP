from pydantic import BaseSettings


class KafkaConfiguration(BaseSettings):
    instance: str
    topic: str
    username: str
    password: str
    cafile: str | None

    class Config:
        env_prefix = "kafka_"
