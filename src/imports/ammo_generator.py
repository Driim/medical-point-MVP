#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from faker import Faker
from faker.providers import address, company, lorem, person

fake_person = Faker("ru_RU")
fake_person.add_provider(address)
fake_person.add_provider(person)

from src.structures.domain.workers.models import WorkerCreateDto


def make_ammo(method, url, headers, case, body):
    """ makes phantom ammo """
    # http request w/o entity body template
    req_template = (
          "%s %s HTTP/1.1\r\n"
          "%s\r\n"
          "\r\n"
    )

    # http request with entity body template
    req_template_w_entity_body = (
          "%s %s HTTP/1.1\r\n"
          "%s\r\n"
          "Content-Length: %d\r\n"
          "\r\n"
          "%s\r\n"
    )

    if not body:
        req = req_template % (method, url, headers)
    else:
        req = req_template_w_entity_body % (method, url, headers, len(body), body)

    # phantom ammo template
    ammo_template = (
        "%d %s\n"
        "%s"
    )

    return ammo_template % (len(req), case, req)


def create_json_body(i: int, ou_id: str) -> str:
    worker = WorkerCreateDto(
        fio=f"{fake_person.name()}",
        drivers_license=f"{i}",
        active=True,
        organization_unit_id=ou_id,
    )

    return worker.json()


def main():
    method = "POST"
    url = "/workers"
    ou_id = "c96fa86b-0d0b-4047-b3d3-7f3d2a421c13"

    headers = "Host: 51.250.44.86\r\n" + \
              "X-User-Id: b75de436-e162-43a7-8f1a-ebaa26c74b69\r\n" + \
              "User-Agent: tank\r\n" + \
              "Accept: */*\r\n" + \
              "Content-Type: application/json\r\n" + \
              "Connection: keep-alive"

    for i in range(1, 10800):
        body = create_json_body(i, ou_id)

        sys.stdout.write(make_ammo(method, url, headers, "", body))


if __name__ == "__main__":
    main()
