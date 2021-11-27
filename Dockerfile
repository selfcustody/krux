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
        libisl-dev \
        python3 \
        python3-pip \
        python3-setuptools

RUN wget https://github.com/Kitware/CMake/releases/download/v3.21.0/cmake-3.21.0.tar.gz && \
    echo "4a42d56449a51f4d3809ab4d3b61fd4a96a469e56266e896ce1009b5768bd2ab  cmake-3.21.0.tar.gz" | sha256sum -c && \
    tar -xzvf cmake-3.21.0.tar.gz && \
    cd cmake-3.21.0 && ./bootstrap && make && make install

RUN mkdir -p /opt && \
    wget https://github.com/kendryte/kendryte-gnu-toolchain/releases/download/v8.2.0-20190213/kendryte-toolchain-ubuntu-amd64-8.2.0-20190213.tar.gz && \
    echo "aa2fcc76ff61261b3667a422d4f67dec19c4547474bff4ebadaa1258b87985da  kendryte-toolchain-ubuntu-amd64-8.2.0-20190213.tar.gz" | sha256sum -c && \
    tar -xzvf kendryte-toolchain-ubuntu-amd64-8.2.0-20190213.tar.gz -C /opt

RUN pip3 install astor

FROM build-base as build-software
COPY . /src
WORKDIR /src
ARG LOCALE="en-US"
RUN cd vendor/embit && pip3 install -e .
RUN mkdir build && \
    cp -r src/. build && \
    cp -r vendor/embit/src/embit build && \
    rm -rf build/embit/util/prebuilt && \
    rm -f build/embit/util/ctypes_secp256k1.py && \
    cp -r vendor/urtypes/src/urtypes build && \
    cp -r vendor/foundation-ur-py/ur build && \
    cp -r firmware/MaixPy/projects/maixpy_m5stickv/builtin_py/. build && \
    rm -f build/_boot.py && \
    cp LICENSE.md build/LICENSE.md && \
    find build -regex '^.*\(__pycache__\|\.py[co]\|\.DS_Store\)$' -delete
RUN cd i18n && \
    python3 i18n.py translate "${LOCALE}" /src/build
RUN find /src/build -type f -name \*.py -exec sh -c "python3 ./firmware/scripts/minify.py {}" \;

FROM build-software AS build-firmware
WORKDIR /src/firmware/MaixPy
RUN pip3 install -r requirements.txt
RUN python3 ./components/micropython/core/lib/memzip/make-memzip.py --zip-file ./components/micropython/port/memzip-files.zip --c-file ./components/micropython/port/memzip-files.c /src/build
RUN cd projects/maixpy_m5stickv && \
    python3 project.py clean && \
    python3 project.py distclean && \
    python3 project.py build && \
    mv build/maixpy.bin build/firmware.bin

FROM build-firmware AS build
WORKDIR /src/firmware/Kboot/build
RUN cp /src/firmware/MaixPy/projects/maixpy_m5stickv/build/firmware.bin .
RUN ./CLEAN.sh && ./BUILD.sh
