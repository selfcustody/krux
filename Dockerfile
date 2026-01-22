# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# syntax=docker/dockerfile:1

############
# build-base
# install kendryte (k210), cmake and python dependencies
############
FROM gcc:9.5.0-bullseye AS build-base

RUN apt-get update -y && \
    apt-get install --no-install-recommends -y -q \
        wget \
        tar \
        zip \
        unzip \
        build-essential \
        libtool \
        autoconf \
        automake \
        autotools-dev \
        curl \
        libmpc-dev \
        libmpfr-dev \
        libgmp-dev \
        gawk \
        bison \
        flex \
        texinfo \
        gperf \
        libtool \
        patchutils \
        bc \
        zlib1g-dev \
        libexpat-dev \
        libisl-dev \
        python3 \
        python3-pip \
        python3-setuptools

RUN mkdir -p /opt && \
    GIT_TERMINAL_PROMPT=0 \
    git clone --depth 1 --branch v8.2.0-20190409 https://github.com/kendryte/kendryte-gnu-toolchain

RUN cd kendryte-gnu-toolchain && \
    sed -i 's|https://github.com/bminor/binutils-gdb.git|https://github.com/riscvarchive/riscv-binutils-gdb.git|' .gitmodules && \
    git submodule sync && \
    git submodule update \
      --init \
      --recursive \
      --depth 1

RUN cd kendryte-gnu-toolchain && \
    export PATH=$PATH:/opt/kendryte-toolchain/bin && \
    ./configure --prefix=/opt/kendryte-toolchain --with-cmodel=medany --with-arch=rv64imafc --with-abi=lp64f --enable-threads=posix --enable-libatomic && \
    make -j8

RUN wget https://github.com/Kitware/CMake/releases/download/v3.21.0/cmake-3.21.0.tar.gz && \
    echo "4a42d56449a51f4d3809ab4d3b61fd4a96a469e56266e896ce1009b5768bd2ab  cmake-3.21.0.tar.gz" | sha256sum -c && \
    tar -xzvf cmake-3.21.0.tar.gz && \
    cd cmake-3.21.0 && ./bootstrap && make && make install

RUN apt-get update && apt-get install python3-venv -y
RUN python3 -m venv /kruxenv
RUN /kruxenv/bin/pip install astor
RUN /kruxenv/bin/pip install pyserial==3.4


############
# build-software
# copy vendor, firmware and Krux (src) files
# install embit dependency
############
FROM build-base AS build-software
ARG DEVICE="maixpy_m5stickv"
ENV DEVICE_BUILTIN="firmware/MaixPy/projects/${DEVICE}/builtin_py"
RUN mkdir /src
WORKDIR /src

# copy vendor to WORKDIR (src)
COPY ./vendor vendor

# clean vendor/urtypes
RUN find vendor/urtypes -type d -name '__pycache__' -exec rm -rv {} + -depth

# clean vendor/foundation-ur-py
RUN find vendor/foundation-ur-py -type d -name '__pycache__' -exec rm -rv {} + -depth

# install vendor/embit
RUN /kruxenv/bin/pip install vendor/embit
# clean vendor/embit
RUN rm -rf vendor/embit/src/embit/util/prebuilt && \
    rm -rf vendor/embit/src/embit/liquid && \
    rm -f vendor/embit/src/embit/psbtview.py && \
    rm -f vendor/embit/src/embit/slip39.py && \
    rm -f vendor/embit/src/embit/wordlists/slip39.py && \
    rm -f vendor/embit/src/embit/util/ctypes_secp256k1.py && \
    rm -f vendor/embit/src/embit/util/py_secp256k1.py && \
    rm -f vendor/embit/src/embit/util/py_ripemd160.py && \
    find vendor/embit -type d -name '__pycache__' -exec rm -rv {} + -depth

# copy firmware to WORKDIR (src)
COPY ./firmware firmware
# clean firmware
RUN find firmware -type d -name '__pycache__' -exec rm -rv {} + -depth

# copy all vendors to DEVICE_BUILTIN
RUN cp -r vendor/urtypes/src/urtypes "${DEVICE_BUILTIN}"
RUN cp -r vendor/foundation-ur-py/src/ur "${DEVICE_BUILTIN}"
RUN cp -r vendor/embit/src/embit "${DEVICE_BUILTIN}"

# copy Krux (src) to WORKDIR (src)
COPY ./src src
# rename boot.py
RUN mv src/boot.py src/_boot.py
# clean it
RUN find src -type d -name '__pycache__' -exec rm -rv {} + -depth
# copy it to DEVICE_BUILTIN
RUN cp -r src/. "${DEVICE_BUILTIN}"


############
# build-firmware
# python compilation of Krux and its dependencies inside MaixPy
# creation of the firmware.bin
############
FROM build-software AS build-firmware
ARG DEVICE="maixpy_m5stickv"
WORKDIR /src/firmware/MaixPy

# overrides the DEVICE specific C files (font, sensor, ...) in componets/micropython
RUN cp -rf projects/"${DEVICE}"/compile/overrides/. ./

RUN cd projects/"${DEVICE}" && \
    /kruxenv/bin/python project.py clean && \
    /kruxenv/bin/python project.py distclean && \
    /kruxenv/bin/python project.py build && \
    mv build/maixpy.bin build/firmware.bin


############
# build
# creation of kboot.kfpkg using firmware.bin
############
FROM build-firmware AS build
ARG DEVICE="maixpy_m5stickv"
WORKDIR /src/firmware/Kboot/build
RUN cp /src/firmware/MaixPy/projects/"${DEVICE}"/build/firmware.bin .

# replace possible windows line endings
RUN sed -i -e 's/\r$//' *.sh

RUN ./CLEAN.sh && ./BUILD.sh
