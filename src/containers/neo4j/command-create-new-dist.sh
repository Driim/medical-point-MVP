yc compute instance create-with-container \
  --name neo4j-vm \
  --zone ru-central1-a \
  --create-boot-disk size=30 \
  --create-disk name=data-disk,size=10,device-name=coi-data \
  --network-interface subnet-name=testing,nat-ip-version=ipv4 \
  --ssh-key ~/.ssh/id_ed25519.pub \
  --docker-compose-file docker-compose.yaml