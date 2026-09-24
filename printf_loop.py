from cffi import FFI
import struct
import time

ffi=FFI()

ffi.cdef("""void* __acrt_iob_func(int handle);
            int __stdio_common_vfprintf(unsigned long long options,
            void* stream, const char* formats, void* locale, void* va_list);""")

ucrtbase=ffi.dlopen('ucrtbase.dll')
stdout_ptr=ucrtbase.__acrt_iob_func(1)

def pack_int(v):
    return struct.pack('<q',v)

def pack_double(v):
    return struct.pack('<d',v)

def pack_ptr(cdata):
    return struct.pack('<Q',int(ffi.cast("uintptr_t",cdata)))

counter=0

while True:
    ratio=counter*1.5
    tag=ffi.new('char[]',b'loop')

    raw=pack_int(counter) + pack_double(ratio) + pack_ptr(tag)
    valist_buf=ffi.new('char[]',raw)

    ucrtbase.__stdio_common_vfprintf(
        0,
        stdout_ptr,
        b"Original: %d, Ratio: %f, Tag: %s\n",
        ffi.NULL,
        valist_buf
    )
    counter+=1
    time.sleep(1)
    