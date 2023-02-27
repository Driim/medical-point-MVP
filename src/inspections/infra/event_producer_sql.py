import json
import logging

from src.inspections.domain.inspections.models import Event

logger = logging.getLogger(__name__)

OUTPUT_FILE = "inserts.sql"
file = open(OUTPUT_FILE, "a")


class EventProducerSql:
    def __init__(self):
        file.write("\n\nINSERT INTO event_log (*) VALUES\n")

    async def produce(self, events: list[Event]):
        # TODO: write SQL inserts to file
        for event in events:
            values = []
            for _, value in event.__dict__.items():
                if isinstance(value, dict):
                    values.append(f"'{json.dumps(value)}'")
                else:
                    values.append(f"'{str(value)}'")

            logger.info(values)
            file.write(f"({','.join(values)})\n")
