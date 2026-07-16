#!/usr/bin/env bash

set -euo pipefail

echo "========================================"
echo " RetroScope PortAudio Builder"
echo "========================================"

sudo apt update

sudo apt install -y \
    git \
    build-essential \
    cmake \
    pkg-config \
    libasound2-dev \
    libpulse-dev

mkdir -p third_party
cd third_party

if [ ! -d portaudio ]; then
    echo
    echo "Cloning PortAudio..."
    git clone https://github.com/PortAudio/portaudio.git
else
    echo
    echo "Updating PortAudio..."
    cd portaudio
    git pull
    cd ..
fi

cd portaudio

rm -rf build
mkdir build
cd build

echo
echo "Configuring..."

cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DPA_USE_ALSA=ON \
    -DPA_USE_PULSEAUDIO=ON

echo
echo "Building..."

make -j"$(nproc)"

echo
echo "Installing..."

sudo make install

echo
echo "Updating linker cache..."

echo "/usr/local/lib" | sudo tee /etc/ld.so.conf.d/portaudio.conf >/dev/null

sudo ldconfig

echo
echo "Installed libraries:"
ldconfig -p | grep portaudio

echo
echo "Checking PulseAudio backend..."

if strings /usr/local/lib/libportaudio.so.2 | grep -qi PulseAudio; then
    echo "✓ PulseAudio backend detected."
else
    echo "✗ PulseAudio backend NOT found."
    exit 1
fi

echo
echo "========================================"
echo " Build completed successfully."
echo "========================================"
echo
echo "If using a Python virtual environment,"
echo "activate it and run:"
echo
echo "export LD_LIBRARY_PATH=/usr/local/lib:\$LD_LIBRARY_PATH"
echo
echo "Then verify:"
echo
echo "python - <<'EOF'"
echo "import sounddevice as sd"
echo "print(sd.get_portaudio_version())"
echo "print(sd.query_hostapis())"
echo "EOF"
