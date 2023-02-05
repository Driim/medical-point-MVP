yc compute instance create-with-container \
  --name neo4j-vm \
  --zone ru-central1-a \
  --create-boot-disk size=30 \
  --attach-disk disk-name=data-disk-small,device-name=coi-data \
  --attach-disk disk-name=import-disk,device-name=coi-import \
  --network-interface subnet-name=testing,nat-ip-version=ipv4 \
  --ssh-key ~/.ssh/id_ed25519.pub \
  --docker-compose-file docker-compose.yaml
