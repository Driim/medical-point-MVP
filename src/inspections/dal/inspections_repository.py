# flake8: noqa: S311
import json
import logging

from clickhouse_sqlalchemy.types import UUID
from fastapi import Depends, HTTPException
from sqlalchemy import ARRAY, Column, DateTime, String, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base

from src.common.clickhouse.middleware import get_session
from src.common.models import Pagination, PaginationQueryParams
from src.inspections.domain.inspections.models import (
    Inspection,
    InspectionsFindBByWorkerDto,
    InspectionsFindDto,
    InspectionsPaginatedDto,
)

logger = logging.getLogger(__name__)
Base = declarative_base()


class InspectionModel(Base):
    __tablename__ = "materialized_inspections"
    # eager_defaults is required in order to access columns
    # with server defaults or SQL expression defaults,
    # after a flush without triggering an expired load
    __mapper_args__ = {"eager_defaults": True}

    inspection_id = Column(UUID, primary_key=True)
    worker_id = Column(UUID)
    worker_path = Column(ARRAY(UUID))
    device_id = Column(UUID)
    device_path = Column(ARRAY(UUID))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    data = Column(ARRAY(String))
    # result_time = Column(DateTime)
    # result = Column(String)
    # result_data = Column(String)


class InspectionsRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self._session = session

    async def find_inspections(
        self,
        dto: InspectionsFindDto,
        available_ou: list[str],
        pagination: PaginationQueryParams,
    ) -> InspectionsPaginatedDto:
        data_select = select(InspectionModel)

        if dto.worker_id:
            data_select = data_select.where(InspectionModel.worker_id == dto.worker_id)

        if dto.from_datetime:
            data_select = data_select.where(
                InspectionModel.end_time >= dto.from_datetime
            )

        if dto.to_datetime:
            data_select = data_select.where(InspectionModel.end_time <= dto.to_datetime)

        if dto.device_id:
            data_select = data_select.where(InspectionModel.device_id == dto.device_id)

        available_ou_uuids = [f"toUUID('{s}')" for s in available_ou]
        available_ou_query = ",".join(available_ou_uuids)
        data_select = data_select.where(
            text(
                f"hasAny(materialized_inspections.worker_path, [{available_ou_query}])"
            )
        )

        count_select = data_select.with_only_columns(
            [func.count()], maintain_column_froms=True
        )
        # count_select.filter(and_(*where_clause))
        count = (await self._session.execute(count_select)).scalars()

        logger.info(f"Count of rows: {count}")

        data_select = data_select.limit(pagination.limit)
        data_select = data_select.offset((pagination.page - 1) * pagination.limit)

        models = (await self._session.execute(data_select)).scalars().all()

        inspections = []

        for model in models:
            inspections.append(self.model_to_inspection(model))

        return InspectionsPaginatedDto(
            data=inspections,
            pagination=Pagination(
                page=pagination.page,
                limit=pagination.limit,
                count=count.first(),
            ),
        )

    async def find_inspections_by_worker(
        self,
        dto: InspectionsFindBByWorkerDto,
    ) -> list[Inspection]:
        if dto.worker_id is None:
            raise HTTPException(400)

        limit = None
        if dto.from_datetime is None:
            limit = 10

        data_select = select(InspectionModel)

        data_select = data_select.where(InspectionModel.worker_id == dto.worker_id)

        if limit is None:
            data_select = data_select.where(
                InspectionModel.end_time >= dto.from_datetime
            )

        if limit is not None:
            logger.info("Using limit instead of time")
            data_select = data_select.limit(limit)

        result = await self._session.execute(data_select)
        models = result.scalars().all()

        resulting_inspections = []

        for model in models:
            resulting_inspections.append(self.model_to_inspection(model))

        return resulting_inspections

    @staticmethod
    def model_to_inspection(model: InspectionModel) -> Inspection:
        data = []

        for d in model.data:
            data.append(json.loads(d.replace("'", '"')))

        return Inspection(
            id=str(model.inspection_id),
            worker_id=str(model.worker_id),
            device_id=str(model.device_id),
            inspection_start=model.start_time,
            inspection_end=model.end_time,
            inspection_data=data,
            # result=model.result,
            # result_data=json.loads(model.result_data),
        )
