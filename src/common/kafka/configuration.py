from pydantic import BaseSettings


class KafkaConfiguration(BaseSettings):
    instance: str
    topic: str
    username: str
    password: str
    cafile: str

    class Config:
        env_prefix = "kafka_"
