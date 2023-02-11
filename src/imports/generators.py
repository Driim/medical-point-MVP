# flake8: noqa: S311
from random import randrange
from uuid import uuid4

from faker import Faker
from faker.providers import address, company, lorem, person

from src.structures.domain.devices.models import DeviceBase
from src.structures.domain.organization_units.models import OrganizationUnitBase
from src.structures.domain.outlets.models import OutletBase
from src.structures.domain.workers.models import WorkerBase

fake = Faker("ru_RU")
fake.add_provider(company)
fake.add_provider(address)
fake.add_provider(lorem)

fake_person = Faker("ru_RU")
fake_person.add_provider(address)
fake_person.add_provider(person)


def get_bool_with_80_percent_chance_to_have_true():
    num = randrange(10)
    return True if num <= 7 else False


def generate_ou(level: int, ou_count: int, parent_ou: str) -> OrganizationUnitBase:
    return OrganizationUnitBase(
        id=str(uuid4()),
        name=f"{level}-{ou_count}-{fake.company()}",
        inn=fake.businesses_inn(),
        kpp=fake.kpp(),
        legal_address=fake.address(),
        ogrn=fake.businesses_ogrn(),
        filler="",
        parent_organization_unit=parent_ou,
        active=get_bool_with_80_percent_chance_to_have_true(),
    )


def generate_outlet(parent_ou: str, ou_count: int, outlet_count: int) -> OutletBase:
    return OutletBase(
        id=str(uuid4()),
        name=f"{ou_count}-{outlet_count}-{fake.word()}",
        address=fake.address(),
        active=get_bool_with_80_percent_chance_to_have_true(),
        organization_unit_id=parent_ou,
    )


def generate_device(parent_outlet: str, ou_count: int, device_count: int) -> DeviceBase:
    return DeviceBase(
        id=str(uuid4()),
        license=f"{ou_count}-{device_count}-{fake.businesses_inn()}",
        active=get_bool_with_80_percent_chance_to_have_true(),
        outlet_id=parent_outlet,
    )


def generate_worker(parent_ou: str, ou_count: int, worker_count: int) -> WorkerBase:
    return WorkerBase(
        id=str(uuid4()),
        fio=f"{ou_count}-{worker_count}-{fake_person.name()}",
        drivers_license=f"{ou_count}{worker_count}{fake.businesses_inn()}",
        active=get_bool_with_80_percent_chance_to_have_true(),
        organization_unit_id=parent_ou,
    )
