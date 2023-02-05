yc compute instance create-with-container \
  --name service-vm \
  --zone ru-central1-a \
  --create-boot-disk size=30 \
  --network-interface subnet-name=testing,nat-ip-version=ipv4 \
  --ssh-key ~/.ssh/id_ed25519.pub \
  --service-account-name docker-account \
  --docker-compose-file docker-compose.yaml