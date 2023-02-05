docker exec --interactive --tty 773a634a59f6 neo4j-admin database import full \
  --overwrite-destination \
  --nodes=OrganizationUnit=import/small-set-with-headers/organization_unit_header.csv,import/small-set-with-headers/organization-units.csv \
  --relationships=CHILD_OF=import/small-set-with-headers/ou_to_ou_header.csv,import/small-set-with-headers/ou_to_ou.csv \
  --nodes=Outlet=import/small-set-with-headers/outlets_header.csv,import/small-set-with-headers/outlets.csv \
  --relationships=BELONG_TO=import/small-set-with-headers/outlets_to_ou_header.csv,import/small-set-with-headers/outlets_to_ou.csv \
  --nodes=Device=import/small-set-with-headers/devices_header.csv,import/small-set-with-headers/devices.csv \
  --relationships=LOCATED_AT=import/small-set-with-headers/device_to_outlet_header.csv,import/small-set-with-headers/devices_to_outlets.csv \
  --nodes=Worker=import/small-set-with-headers/workers_header.csv,import/small-set-with-headers/workers.csv \
  --relationships=WORK_IN=import/small-set-with-headers/worker_to_ou_header.csv,import/small-set-with-headers/workers_to_ou.csv