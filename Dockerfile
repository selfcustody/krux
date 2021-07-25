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
