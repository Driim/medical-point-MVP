# flake8: noqa: S311
# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta
from random import getrandbits, random, randrange
from uuid import uuid4

from faker import Faker
from faker.providers import person
from fastapi import Depends

from src.common.models import PaginationQueryParams
from src.inspections.dal.inspections_repository import InspectionsRepository
from src.inspections.domain.inspections.models import (
    Event,
    EventBase,
    EventData,
    EventType,
    Inspection,
    InspectionFailReason,
    InspectionsFindBByWorkerDto,
    InspectionsFindDto,
    InspectionsPaginatedDto,
    Measurements,
)
from src.inspections.infra.event_producer_kafka import EventProducerKafka
from src.inspections.infra.event_producer_sql import EventProducerSql
from src.inspections.infra.structures_service import StructuresService

fake_person = Faker()
fake_person.add_provider(person)


class InspectionService:
    def __init__(
        self,
        structures: StructuresService = Depends(StructuresService),
        producer: EventProducerKafka = Depends(EventProducerKafka),
        inspections_repo: InspectionsRepository = Depends(InspectionsRepository),
    ):
        self._structures = structures
        self._producer = producer
        self._inspections_repo = inspections_repo

    async def find_inspections(
        self, dto: InspectionsFindDto, pagination: PaginationQueryParams, user_id: str
    ) -> InspectionsPaginatedDto:
        # 1. Get from structures available to user OU ID's
        available_ou = await self._structures.get_available_ou_for_user(user_id)

        if dto.ou_id:
            # TODO: we should call structures to check if user have access to this company
            available_ou = [dto.ou_id]
            dto.ou_id = None

        # 2. Request data from clickhouse
        return await self._inspections_repo.find_inspections(
            dto, available_ou, pagination
        )

    async def find_inspections_by_worker(
        self, dto: InspectionsFindBByWorkerDto
    ) -> list[Inspection]:
        return await self._inspections_repo.find_inspections_by_worker(dto)

    async def generate_inspection(self, device_id: str, worker_id: str) -> None:
        response = await self._structures.worker_can_take_exam(device_id, worker_id)
        worker = response.worker
        device = response.device

        inspection_id = str(uuid4())
        event_datetime = self._get_start_datetime()
        events: list[Event] = list()

        base = EventBase(
            inspection_id=inspection_id,
            datetime=event_datetime,
            worker=worker,
            device=device,
        )

        event = self._get_inspection_start_event(base)
        events.append(event)
        base.datetime = event.datetime

        exams_amount = randrange(2, 7)
        exams = self._get_exams(base, exams_amount)
        base.datetime = exams[-1].datetime
        events.extend(exams)

        event = self._get_end_of_exam_event(base)
        base.datetime = event.datetime
        events.append(event)

        event = self._get_inspection_result_event(base)
        events.append(event)

        # TODO: we can make shuffle events here from time to time, to emulate "weird" work
        await self._producer.produce(events)

    @staticmethod
    def _get_start_datetime() -> datetime:
        return datetime.now() - timedelta(minutes=randrange(1, 60))

    @staticmethod
    def _get_inspection_start_event(base: EventBase) -> Event:
        # change name because of encoding problems
        base.worker.fio = fake_person.name()
        return Event(
            inspection_id=str(base.inspection_id),
            worker_id=str(base.worker.id),
            device_id=str(base.device.id),
            event_type=EventType.START,
            datetime=base.datetime + timedelta(seconds=1),
            # we need it as string because we can not transform it kafka engine later
            event_data=json.dumps(
                {"worker": base.worker.dict(), "device": base.device.dict()}
            ).replace('"', "'"),
        )

    def _get_exams(self, base: EventBase, amount: int) -> list[Event]:
        exams = list()
        time = base.datetime

        for i in range(amount):
            measurement = Measurements(i)
            data = self._get_data_for_measurement(measurement)
            time = time + timedelta(seconds=randrange(5, 20))

            exams.append(
                Event(
                    inspection_id=str(base.inspection_id),
                    worker_id=str(base.worker.id),
                    device_id=str(base.device.id),
                    event_type=EventType.DATA,
                    datetime=time,
                    event_data=json.dumps(
                        {"measurement": str(measurement), "data": data}
                    ).replace('"', "'"),
                )
            )

        return exams

    @staticmethod
    def _get_data_for_measurement(measurement: Measurements) -> dict:
        match measurement:
            case Measurements.ALCOHOL:
                return {"ppm": random()}
            case Measurements.PRESSURE:
                return {
                    "systolic": {
                        "upper": randrange(80, 160),
                        "lower": randrange(40, 80),
                    },
                    "diastolic": {
                        "upper": randrange(80, 160),
                        "lower": randrange(40, 80),
                    },
                }
            case Measurements.CONDITIONS:
                return {"unknown": 1}
            case Measurements.HEADACHE:
                return {"head_headache": 1}
            case Measurements.INJURIES:
                return {"had_injuries": 1}
            case Measurements.PULSE:
                return {"pulse": randrange(40, 180)}
            case Measurements.SLEEP:
                return {"insomnia": 1}
            case Measurements.FRACTURE:
                return {"fracture": 1}

    @staticmethod
    def _get_end_of_exam_event(base: EventBase) -> Event:
        return Event(
            inspection_id=str(base.inspection_id),
            worker_id=str(base.worker.id),
            device_id=str(base.device.id),
            event_type=EventType.END,
            datetime=base.datetime + timedelta(seconds=randrange(5, 45)),
            event_data=json.dumps(dict()).replace('"', "'"),
        )

    @staticmethod
    def _get_inspection_result_event(base: EventBase) -> Event:
        result = bool(getrandbits(1))
        data = dict()
        if not result:
            data["reason"] = str(
                InspectionFailReason(randrange(0, InspectionFailReason.max()))
            )

        return Event(
            inspection_id=str(base.inspection_id),
            worker_id=str(base.worker.id),
            device_id=str(base.device.id),
            event_type=EventType.RESULT,
            datetime=base.datetime + timedelta(minutes=randrange(2, 25)),
            event_data=json.dumps(
                {"result": "PASS" if result else "FAILED", "data": data}
            ).replace('"', "'"),
        )
