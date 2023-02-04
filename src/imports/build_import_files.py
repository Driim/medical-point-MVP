import csv
from dataclasses import dataclass
from os import path

from pydantic import BaseModel

from src.imports.distributions import (
    get_amount_of_devices,
    get_amount_of_outlets,
    get_amount_of_workers,
    get_level_ou_amount,
    get_subtree_depth,
)
from src.imports.generators import (
    generate_device,
    generate_ou,
    generate_outlet,
    generate_worker,
)
from src.structures.domain.devices.models import DeviceBase
from src.structures.domain.organization_units.models import OrganizationUnitBase
from src.structures.domain.outlets.models import OutletBase
from src.structures.domain.workers.models import WorkerBase

OU_FILE = "organization-units.csv"
WORKERS_FILE = "workers.csv"
OUTLETS_FILE = "outlets.csv"
DEVICES_FILE = "devices.csv"


@dataclass
class Writers:
    ou: csv.DictWriter
    outlet: csv.DictWriter
    device: csv.DictWriter
    worker: csv.DictWriter


class Counters(BaseModel):
    ou: int = 0
    outlets: int = 0
    devices: int = 0
    workers: int = 0


def get_writers(directory: str) -> Writers:
    ou_file = open(path.join(directory, OU_FILE), "w")
    outlet_file = open(path.join(directory, OUTLETS_FILE), "w")
    worker_file = open(path.join(directory, WORKERS_FILE), "w")
    device_file = open(path.join(directory, DEVICES_FILE), "w")

    ou_writer = csv.DictWriter(ou_file, OrganizationUnitBase.__fields__.keys())
    ou_writer.writeheader()

    outlet_writer = csv.DictWriter(outlet_file, OutletBase.__fields__.keys())
    outlet_writer.writeheader()

    worker_writer = csv.DictWriter(worker_file, WorkerBase.__fields__.keys())
    worker_writer.writeheader()

    device_writer = csv.DictWriter(device_file, DeviceBase.__fields__.keys())
    device_writer.writeheader()

    return Writers(
        ou=ou_writer, outlet=outlet_writer, device=device_writer, worker=worker_writer
    )


def build_ou(
    writers: Writers, counters: Counters, root: str, level: int
) -> OrganizationUnitBase:
    # build ou, outlets, devices and workers
    ou = generate_ou(level, counters.ou, root)
    writers.ou.writerow(ou.dict())

    for i in range(1, get_amount_of_workers()):
        worker = generate_worker(ou.id, counters.ou, i)
        writers.worker.writerow(worker.dict())

        counters.workers += 1

    for i in range(1, get_amount_of_outlets()):
        outlet = generate_outlet(ou.id, counters.ou, i)

        writers.outlet.writerow(outlet.dict())
        counters.outlets += 1

        for x in range(1, get_amount_of_devices()):
            device = generate_device(outlet.id, counters.ou, x)

            writers.device.writerow(device.dict())
            counters.devices += 1

    counters.ou += 1

    return ou


def generate_ou_subtree(
    writers: Writers, counters: Counters, root: str, depth: int, level: int
):
    if depth <= 0:
        # exit recursion
        return

    for _ in range(1, get_level_ou_amount()):
        print(f"Generating new subtree depth: {depth}, level: {level}, root: {root}")
        # TODO: can not leaf OU have outlets and devices?
        ou = build_ou(writers, counters, root, level)

        generate_ou_subtree(writers, counters, ou.id, depth - 1, level + 1)


def generate_database(directory: str, max_ou: int, root: str):
    writers = get_writers(directory)
    counters = Counters()

    ou = generate_ou(0, 0, root)
    ou.id = root  # root OU
    ou.parent_organization_unit = None
    writers.ou.writerow(ou.dict())

    while counters.ou < max_ou:
        print(f"{counters.ou} from {max_ou}")
        depth = get_subtree_depth()
        print(f"Generating new subtree depth: {depth}")

        generate_ou_subtree(writers, counters, root, depth, 1)

    print("Generated:")
    print(counters)


if __name__ == "__main__":
    generate_database(
        "/Users/dmitriyfalko/work/import-data/",
        100,
        "68d7de47-6f57-452c-9c7c-d3f3fdc4d041",
    )
