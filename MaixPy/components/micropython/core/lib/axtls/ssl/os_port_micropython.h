/*
 * Copyright (c) 2007-2015, Cameron Rich
 * 
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without 
 * modification, are permitted provided that the following conditions are met:
 *
 * * Redistributions of source code must retain the above copyright notice, 
 *   this list of conditions and the following disclaimer.
 * * Redistributions in binary form must reproduce the above copyright notice, 
 *   this list of conditions and the following disclaimer in the documentation 
 *   and/or other materials provided with the distribution.
 * * Neither the name of the axTLS project nor the names of its contributors 
 *   may be used to endorse or promote products derived from this software 
 *   without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/**
 * @file os_port.h
 *
 * Some stuff to minimise the differences between windows and linux/unix
 */

#ifndef HEADER_OS_PORT_H
#define HEADER_OS_PORT_H

#include "os_int.h"
#include <errno.h>
#include <sys/types.h>
#ifndef __ets__
#include <arpa/inet.h>
#endif
#include <sys/time.h>
#include "config.h"

ssize_t mp_stream_posix_write(void *sock_obj, const void *buf, size_t len);
ssize_t mp_stream_posix_read(void *sock_obj, void *buf, size_t len);
extern int mp_stream_errno;

#if 1
#define SOCKET_READ(A,B,C)      mp_stream_posix_read((void*)A,B,C)
#define SOCKET_WRITE(A,B,C)     mp_stream_posix_write((void*)A,B,C)
#define SOCKET_CLOSE(A)         NOT_USED_IN_LIB_CODE
#define SOCKET_ERRNO() mp_stream_errno
#else
#define SOCKET_READ(A,B,C)      read(A,B,C)
#define SOCKET_WRITE(A,B,C)     write(A,B,C)
#define SOCKET_CLOSE(A)         if (A >= 0) close(A)
#define SOCKET_ERRNO()          errno
#endif
#define ax_calloc(x, y) calloc(x, y)
#define ax_open(x, y) open(x, y)

#ifndef be64toh
#define be64toh(x) __be64_to_cpu(x)
#endif

#define SSL_CTX_MUTEX_INIT(A)
#define SSL_CTX_MUTEX_DESTROY(A)
#define SSL_CTX_LOCK(A)
#define SSL_CTX_UNLOCK(A)

#define TTY_FLUSH()

#include "../../../extmod/crypto-algorithms/sha256.h"

#define SHA256_CTX CRYAL_SHA256_CTX
#define SHA256_Init(a) sha256_init(a)
#define SHA256_Update(a, b, c) sha256_update(a, b, c)
#define SHA256_Final(a, b) sha256_final(b, a)

#endif
