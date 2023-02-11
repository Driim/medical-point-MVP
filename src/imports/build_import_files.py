import csv
from dataclasses import dataclass
from itertools import cycle
from os import path
from random import seed

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
OU_RELATION_FILE = "ou_to_ou.csv"
OUTLETS_RELATION_FILE = "outlets_to_ou.csv"
DEVICES_RELATION_FILE = "devices_to_outlets.csv"
WORKERS_RELATION_FILE = "workers_to_ou.csv"
REQUESTS_EXAMS_FILE = "ammo-exams.txt"
REQUESTS_DEVICES_FILE = "ammo-devices.txt"
REQUESTS_WORKERS_FILE = "ammo-workers.txt"


@dataclass
class Writers:
    ou: csv.DictWriter
    outlet: csv.DictWriter
    device: csv.DictWriter
    worker: csv.DictWriter
    ou_to_ou: any
    outlet_to_ou: any
    device_to_outlet: any
    worker_to_ou: any
    requests_exams: any
    requests_devices: any
    requests_workers: any


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
    ou_to_ou_file = open(path.join(directory, OU_RELATION_FILE), "w")
    outlet_to_ou_file = open(path.join(directory, OUTLETS_RELATION_FILE), "w")
    device_to_outlet_file = open(path.join(directory, DEVICES_RELATION_FILE), "w")
    worker_to_ou_file = open(path.join(directory, WORKERS_RELATION_FILE), "w")
    requests_exams_file = open(path.join(directory, REQUESTS_EXAMS_FILE), "w")
    requests_devices_file = open(path.join(directory, REQUESTS_DEVICES_FILE), "w")
    requests_workers_file = open(path.join(directory, REQUESTS_WORKERS_FILE), "w")

    ou_writer = csv.DictWriter(ou_file, OrganizationUnitBase.__fields__.keys())
    # ou_writer.writeheader()

    outlet_writer = csv.DictWriter(outlet_file, OutletBase.__fields__.keys())
    # outlet_writer.writeheader()

    worker_writer = csv.DictWriter(worker_file, WorkerBase.__fields__.keys())
    # worker_writer.writeheader()

    device_writer = csv.DictWriter(device_file, DeviceBase.__fields__.keys())
    # device_writer.writeheader()

    ou_to_ou_writer = csv.writer(ou_to_ou_file)
    outlet_to_ou_writer = csv.writer(outlet_to_ou_file)
    device_to_outlet_writer = csv.writer(device_to_outlet_file)
    worker_to_ou_writer = csv.writer(worker_to_ou_file)

    return Writers(
        ou=ou_writer,
        outlet=outlet_writer,
        device=device_writer,
        worker=worker_writer,
        ou_to_ou=ou_to_ou_writer,
        outlet_to_ou=outlet_to_ou_writer,
        device_to_outlet=device_to_outlet_writer,
        worker_to_ou=worker_to_ou_writer,
        requests_exams=requests_exams_file,
        requests_devices=requests_devices_file,
        requests_workers=requests_workers_file,
    )


def build_ou(
    writers: Writers, counters: Counters, root: str, level: int
) -> OrganizationUnitBase:
    # build ou, outlets, devices and workers
    ou = generate_ou(level, counters.ou, root)
    writers.ou.writerow(ou.dict())
    writers.ou_to_ou.writerow([ou.id, root])

    device_ids = []

    for i in range(1, get_amount_of_outlets()):
        outlet = generate_outlet(ou.id, counters.ou, i)

        writers.outlet.writerow(outlet.dict())
        writers.outlet_to_ou.writerow([outlet.id, ou.id])
        counters.outlets += 1

        for x in range(1, get_amount_of_devices()):
            device = generate_device(outlet.id, counters.ou, x)

            writers.device.writerow(device.dict())
            writers.device_to_outlet.writerow([device.id, outlet.id])
            device_ids.append(device.id)
            writers.requests_devices.write(f"/devices/{device.id}\n")
            counters.devices += 1

    devices_cycle_iterator = cycle(device_ids)
    for i in range(1, get_amount_of_workers()):
        worker = generate_worker(ou.id, counters.ou, i)
        writers.worker.writerow(worker.dict())
        writers.worker_to_ou.writerow([worker.id, ou.id])

        writers.requests_exams.write(
            f"/devices/{next(devices_cycle_iterator)}/exam/{worker.id}\n"
        )
        writers.requests_workers.write(f"/workers/{worker.id}\n")

        counters.workers += 1

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

    seed()

    ou = generate_ou(0, 0, root)
    ou.id = root  # root OU
    ou.active = True
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
        300000,
        "68d7de47-6f57-452c-9c7c-d3f3fdc4d041",
    )
