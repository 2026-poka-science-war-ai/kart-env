# Prerequisites

1. Need Docker and NVIDIA Container Toolkit installed on host machine.
2. `MarioKartWii.iso` should be in the project root directory.
3. You need to clone [dolphin source](https://github.com/2026-poka-science-war-ai/dolphin) to project root directory.
4. You need to clone [dwc source](https://github.com/2026-poka-science-war-ai/dwc-network-server) to project root directory.
5. This repository should be in the same directory as dolphin source.


The directory structure should look like this:
```
.
├── dolphin/
├── dwc/
├── kart-env/
├── MarioKartWii.iso
```

# How to run

```
cd kart-env
docker compose up -d --build
```