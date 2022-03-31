# The MIT License (MIT)

# Copyright (c) 2021 Tom J. Sun

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
FROM gcc:9.4.0-buster AS build-base

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
    git clone --recursive https://github.com/kendryte/kendryte-gnu-toolchain && \
    cd kendryte-gnu-toolchain && \
    git checkout fbf55383711b68c00ecf67e23959822180010398 && \
    export PATH=$PATH:/opt/kendryte-toolchain/bin && \
    ./configure --prefix=/opt/kendryte-toolchain --with-cmodel=medany --with-arch=rv64imafc --with-abi=lp64f --enable-threads=posix --enable-libatomic && \
    make -j8

RUN wget https://github.com/Kitware/CMake/releases/download/v3.21.0/cmake-3.21.0.tar.gz && \
    echo "4a42d56449a51f4d3809ab4d3b61fd4a96a469e56266e896ce1009b5768bd2ab  cmake-3.21.0.tar.gz" | sha256sum -c && \
    tar -xzvf cmake-3.21.0.tar.gz && \
    cd cmake-3.21.0 && ./bootstrap && make && make install

RUN pip3 install astor

FROM build-base as build-software
ARG DEVICE="maixpy_m5stickv"
RUN mkdir /src
COPY ./LICENSE.md /src/LICENSE.md
COPY ./firmware /src/firmware
COPY ./src /src/src
COPY ./vendor /src/vendor
WORKDIR /src
RUN cd vendor/embit && pip3 install -e .
RUN mkdir build && \
    cp -r src/. build && \
    cp -r vendor/embit/src/embit build && \
    rm -rf build/embit/util/prebuilt && \
    rm -f build/embit/util/ctypes_secp256k1.py && \
    rm -f build/embit/util/py_secp256k1.py && \
    cp -r vendor/urtypes/src/urtypes build && \
    cp -r vendor/foundation-ur-py/src/ur build && \
    cp -r firmware/MaixPy/projects/"${DEVICE}"/builtin_py/. build && \
    cp LICENSE.md build/LICENSE.md && \
    find build -type f -name '*.py[co]' -delete && \
    find build -type f -name '.DS_Store' -delete && \
    find build -type d -name '__pycache__' -exec rm -rv {} + -depth && \
    find build -type d -name '.pytest_cache' -exec rm -rv {} + -depth && \
    find build -type d -name '*.egg-info' -exec rm -rv {} + -depth
RUN find /src/build -type f -name \*.py -exec sh -c "python3 ./firmware/scripts/minify.py {}" \;

FROM build-software AS build-firmware
ARG DEVICE="maixpy_m5stickv"
WORKDIR /src/firmware/MaixPy
RUN pip3 install -r requirements.txt
RUN python3 ./components/micropython/core/lib/memzip/make-memzip.py --zip-file ./components/micropython/port/memzip-files.zip --c-file ./components/micropython/port/memzip-files.c /src/build
RUN cp -rf projects/"${DEVICE}"/compile/overrides/. ./
RUN cd projects/"${DEVICE}" && \
    python3 project.py clean && \
    python3 project.py distclean && \
    python3 project.py build && \
    mv build/maixpy.bin build/firmware.bin

FROM build-firmware AS build
ARG DEVICE="maixpy_m5stickv"
WORKDIR /src/firmware/Kboot/build
RUN cp /src/firmware/MaixPy/projects/"${DEVICE}"/build/firmware.bin .
RUN ./CLEAN.sh && ./BUILD.sh
