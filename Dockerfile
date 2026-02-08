FROM pytorch/pytorch:2.1.1-cuda12.1-cudnn8-devel

WORKDIR /kart_env

RUN sed -i 's/archive.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    locales \
    dolphin-emu xvfb \
    x11vnc novnc websockify \
    && wget https://github.com/VirtualGL/virtualgl/releases/download/3.1.4/virtualgl_3.1.4_amd64.deb && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ./virtualgl_3.1.4_amd64.deb \
    && rm virtualgl_3.1.4_amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && locale-gen en_US.UTF-8

ENV NVIDIA_DRIVER_CAPABILITIES="all"
