FROM ubuntu:24.04@sha256:c4a8d5503dfb2a3eb8ab5f807da5bc69a85730fb49b5cfca2330194ebcc41c7b

RUN sed -i 's/archive.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    locales wget xvfb x11vnc novnc websockify git gcc g++ make python3-dev cmake \
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
    # libsdl3-dev \
    # FMT
    # libfmt-dev \
    # glslang
    glslang-dev \
    glslang-tools \
    # pugixml
    libpugixml-dev \
    # enet
    # libenet-dev \
    # xxhash
    libxxhash-dev \
    # bzip2
    libbz2-dev \
    # LZMA
    liblzma-dev \
    # zstd
    libzstd-dev \
    # zlib
    # zlib1g-dev \
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
    && locale-gen en_US.UTF-8 && \
    wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run && \
    sh cuda_11.8.0_520.61.05_linux.run --override --silent --toolkit && \
    rm cuda_11.8.0_520.61.05_linux.run

COPY --from=dolphin-src / /dolphin-src
RUN cd /dolphin-src && \
    git -c submodule."Externals/Qt".update=none \
        -c submodule."Externals/FFmpeg-bin".update=none \
        -c submodule."Externals/libadrenotools".update=none \
        submodule update --init --recursive && \
    mkdir build && cd build && \
    cmake .. \
        -DUSE_SYSTEM_SDL3=OFF \
        -DUSE_SYSTEM_FMT=OFF \
        -DUSE_SYSTEM_MINIZIP-NG=OFF \
        -DUSE_SYSTEM_SFML=OFF \
        -DUSE_SYSTEM_MBEDTLS=OFF \
        -DUSE_SYSTEM_LIBMGBA=OFF \
        -DCMAKE_POLICY_VERSION_MINIMUM=3.5 && \
    make -j$(nproc) && \
    make install && \
    cd / && rm -rf /dolphin-src

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /kart_env
COPY pyproject.toml uv.lock .python-version ./
RUN uv pip install --system --break-system-packages -r pyproject.toml
COPY src ./src
RUN uv pip install --system --break-system-packages -e .

ENV NVIDIA_DRIVER_CAPABILITIES="all"

WORKDIR /workspace
