FROM pytorch/pytorch:2.10.0-cuda12.8-cudnn9-devel

WORKDIR /kart_env

RUN sed -i 's/archive.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    locales wget xvfb x11vnc novnc websockify git dolphin-emu \
    # PkgConfig
    pkg-config \
    # OpenGL
    libgl1-mesa-dev \
    # X11
    libx11-dev \
    libxrandr-dev \
    libxi-dev \
    # EGL
    libegl1-mesa-dev \
    # FFMPEG
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswresample-dev \
    libswscale-dev \
    # udev (Use libeudev-dev if on non-systemd)
    libudev-dev \
    # evdev
    libevdev-dev \
    # SDL
    libsdl3-dev \
    # FMT
    libfmt-dev \
    # glslang
    glslang-dev \
    glslang-tools \
    # pugixml
    libpugixml-dev \
    # enet
    libenet-dev \
    # xxhash
    libxxhash-dev \
    # bzip2
    libbz2-dev \
    # LZMA
    liblzma-dev \
    # zstd
    libzstd-dev \
    # zlib
    zlib1g-dev \
    # minizip-ng
    ## Not packaged yet (but soon on Debian)
    # lzo
    liblzo2-dev \
    # lz4
    liblz4-dev \
    # spng
    libspng-dev \
    # cubeb
    libcubeb-dev \
    # libusb
    libusb-1.0-0-dev \
    # SFML
    ## libsfml-dev \
    ## SFML 3.0 is not yet shipped on Debian and Ubuntu
    # MiniUPNPC
    libminiupnpc-dev \
    # MbedTLS
    ## We are using an outdated 2.x version, and Debian/Ubuntu only ship 3.x now
    # cURL (this could also be libcurl4-gnutls-dev)
    libcurl4-openssl-dev \
    # hidapi
    libhidapi-dev \
    # mgba
    ## libmgba-dev \
    ## Newer MGBA versions are currently broken with Dolphin
    # systemd
    libsystemd-dev \
    # gtest
    libgtest-dev \
    # ALSA
    libasound2-dev \
    # PulseAudio
    libpulse-dev \
    # LLVM
    llvm-dev \
    # BlueZ
    libbluetooth-dev \
    # Qt6
    qt6-base-dev \
    qt6-base-private-dev \
    qt6-svg-dev \
    # Gettext
    gettext \
    && wget https://github.com/VirtualGL/virtualgl/releases/download/3.1.4/virtualgl_3.1.4_amd64.deb && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ./virtualgl_3.1.4_amd64.deb \
    && rm virtualgl_3.1.4_amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && locale-gen en_US.UTF-8

ENV NVIDIA_DRIVER_CAPABILITIES="all"
