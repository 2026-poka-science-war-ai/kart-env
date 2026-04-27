# Mario Kart Wii Environment

## Prerequisites

1. Need Docker and NVIDIA Container Toolkit installed on host machine.
2. `MarioKartWii.iso` should be in the project root directory.
3. You need to clone [dolphin source](https://github.com/2026-poka-science-war-ai/dolphin) to project root directory.
4. This repository should be in the same directory as dolphin source.

The directory structure should look like this:

```plaintext
.
├── dolphin/
├── kart-env/
├── MarioKartWii.iso
```

## Before running

Copy `compose.override.yml.example` to `compose.override.yml` and modify it if necessary.

## How to run

```bash
cd kart-env
docker compose up -d --build
```
