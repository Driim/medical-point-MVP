docker exec --interactive --tty 598a2d9c972c neo4j-admin database import full \
  --overwrite-destination \
  --nodes=OrganizationUnit=import/big-set-with-headers/organization_unit_header.csv,import/big-set-with-headers/organization-units.csv \
  --relationships=CHILD_OF=import/big-set-with-headers/ou_to_ou_header.csv,import/big-set-with-headers/ou_to_ou.csv \
  --nodes=Outlet=import/big-set-with-headers/outlets_header.csv,import/big-set-with-headers/outlets.csv \
  --relationships=BELONG_TO=import/big-set-with-headers/outlets_to_ou_header.csv,import/big-set-with-headers/outlets_to_ou.csv \
  --nodes=Device=import/big-set-with-headers/devices_header.csv,import/big-set-with-headers/devices.csv \
  --relationships=LOCATED_AT=import/big-set-with-headers/device_to_outlet_header.csv,import/big-set-with-headers/devices_to_outlets.csv \
  --nodes=Worker=import/big-set-with-headers/workers_header.csv,import/big-set-with-headers/workers.csv \
  --relationships=WORK_IN=import/big-set-with-headers/worker_to_ou_header.csv,import/big-set-with-headers/workers_to_ou.csv