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
FROM gcc:9.4.0-buster AS builder

RUN apt-get update -y && \
    apt-get install --no-install-recommends -y -q \
        wget \
        tar \
        unzip \
        build-essential \
        libtool \
        autoconf \
        libisl-dev \
        python3 \
        python3-pip

RUN wget https://github.com/Kitware/CMake/releases/download/v3.21.0/cmake-3.21.0.tar.gz
RUN echo "4a42d56449a51f4d3809ab4d3b61fd4a96a469e56266e896ce1009b5768bd2ab  cmake-3.21.0.tar.gz" | sha256sum -c
RUN tar -xzvf cmake-3.21.0.tar.gz
RUN cd cmake-3.21.0 && ./bootstrap && make && make install

RUN mkdir -p /opt
RUN wget https://github.com/kendryte/kendryte-gnu-toolchain/releases/download/v8.2.0-20190213/kendryte-toolchain-ubuntu-amd64-8.2.0-20190213.tar.gz
RUN echo "aa2fcc76ff61261b3667a422d4f67dec19c4547474bff4ebadaa1258b87985da  kendryte-toolchain-ubuntu-amd64-8.2.0-20190213.tar.gz" | sha256sum -c
RUN tar -xzvf kendryte-toolchain-ubuntu-amd64-8.2.0-20190213.tar.gz -C /opt

FROM builder AS build
COPY . /src
WORKDIR /src/MaixPy

RUN pip3 install -r requirements.txt

RUN cd projects/maixpy_m5stickv && \
    python3 project.py clean && \
    python3 project.py distclean && \
    python3 project.py build
