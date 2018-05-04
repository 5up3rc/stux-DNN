# attack on toyNN on linux 
# copied from:
# https://unix.stackexchange.com/questions/6267/how-to-re-load-all-running-applications-from-swap-space-into-ram/6271#6271
 
#!/usr/bin/env python
import ctypes, re, sys

## Partial interface to ptrace(2), only for PTRACE_ATTACH and PTRACE_DETACH.
c_ptrace = ctypes.CDLL("libc.so.6").ptrace
c_pid_t = ctypes.c_int32 # This assumes pid_t is int32_t
c_ptrace.argtypes = [ctypes.c_int, c_pid_t, ctypes.c_void_p, ctypes.c_void_p]
def ptrace(attach, pid):
    op = ctypes.c_int(16 if attach else 17) #PTRACE_ATTACH or PTRACE_DETACH
    c_pid = c_pid_t(pid)
    null = ctypes.c_void_p()
    err = c_ptrace(op, c_pid, null, null)
    if err != 0: raise SysError, 'ptrace', err

## Parse a line in /proc/$pid/maps. Return the boundaries of the chunk
## the read permission character.
def maps_line_range(line):
    m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r])', line)
    return [int(m.group(1), 16), int(m.group(2), 16), m.group(3)]

## Dump the readable chunks of memory mapped by a process
'''
def cat_proc_mem(pid):
    ## Apparently we need to ptrace(PTRACE_ATTACH, $pid) to read /proc/$pid/mem
    ptrace(True, int(pid))
    ## Read the memory maps to see what address ranges are readable
    maps_file = open("/proc/" + pid + "/maps", 'r')
    ranges = map(maps_line_range, maps_file.readlines())
    maps_file.close()
    ## Read the readable mapped ranges
    mem_file = open("/proc/" + pid + "/mem", 'r', 0)
    for r in ranges:
        if r[2] == 'r':
            try:
                mem_file.seek(r[0])
                chunk = mem_file.read(r[1] - r[0])
                print chunk
            except:
                continue
    mem_file.close()
    ## Cleanup
    ptrace(False, int(pid))
'''

## Find memory wiht in a process memory mapped by a process
def locate_proc_mem(pid, patch_str):
    mem_list = []
    addresses = []
    pattern = re.compile(patch_str)
    maps_file = open("/proc/" + pid + "/maps", 'r')
    ranges = map(maps_line_range, maps_file.readlines())
    maps_file.close()
    ## Read the readable mapped ranges
    mem_file = open("/proc/" + pid + "/mem", 'rb', 0)
    for r in ranges:
        if r[2] == 'r':
            try:
                mem_file.seek(r[0])
                chunk = mem_file.read(r[1] - r[0])
                if pattern.search(bytearray(chunk)):
                    addresses.append((pattern.search(chunk), r[0]))
            except:
                continue
    mem_file.close()
    return addresses

def patch_proc_mem(pid, addr, target):
    mem_file = open("/proc/" + pid + "/mem", 'wb', 0)
    mem_file.seek(addr)
    mem_file.write(target)


if __name__ == "__main__":
    for pid in sys.argv[1:]:
        
        target = '\x00\x00\x80\xbf\x00\x00\x80\xbf'


        w1 = '\x00\x00\x80\xbf\x00\x00\x80\x3f'
        found_1 = locate_proc_mem(pid, w1)
        if len(found_1):
            print("Found addresses for w1")
            for first in found_1:
                patch_proc_mem(pid, first[0].start() + first[1], target)
        else:
            print("couldn't find weight")

        ''''

        w2 = '\x00\x00\x80\x3f\x00\x00\x80\xbf'
        found_2 = locate_proc_mem(pid, w2)
        if len(found_2):
            print("Found addresses for w2")
            for second in found_2:
                patch_proc_mem(pid, second[0].start() + second[1], target)
        else:
            print("couldn't find weight")
 
        w3 = '\x00\x00\x80\x3f\x00\x00\x80\x3f'
        found_3 = locate_proc_mem(pid, w3)
        if len(found_3):
            print("Found addresses for w3")
            for third in found_3:
                patch_proc_mem(pid, third[0].start() + third[1], target)
        else:
            print("couldn't find weight")

        '''



