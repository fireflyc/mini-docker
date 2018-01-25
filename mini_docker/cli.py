# coding=utf-8
import os
from ctypes import CFUNCTYPE, c_int, create_string_buffer, c_void_p, cast
from signal import SIGCHLD
from mini_docker import libc

STACK_SIZE = 1024


def child_func():
    print("child pid=%d ppid=%d" % (os.getpid(), os.getppid()))
    libc.sethostname("mytest")
    new_root_path = "/tmp/rootfs"
    target = os.path.join(new_root_path, "proc")

    if not os.path.exists(target):
        os.mkdir(target, 0x755)
    libc.mount("proc", target, "proc")

    libc.mount(new_root_path, new_root_path, "", libc.MS_BIND | libc.MS_REC)
    putold = os.path.join(new_root_path, ".pivot_root")

    if not os.path.exists(putold):
        os.mkdir(putold, 0x700)
    libc.pivot_root(new_root_path, putold)
    os.chdir("/")

    putold = "/.pivot_root"
    libc.umount(putold, libc.MNT_DETACH)
    os.removedirs(putold)
    # 这里会使用新的文件系统
    os.execle("/bin/bash", {"PS1": "[mini-docker]"})
    return 0


def main():
    child = CFUNCTYPE(c_int)(child_func)
    child_stack = create_string_buffer(STACK_SIZE)
    child_stack_pointer = c_void_p(cast(child_stack, c_void_p).value + STACK_SIZE)
    flags = libc.CLONE_NEWUTS | libc.CLONE_NEWPID | libc.CLONE_NEWIPC \
            | libc.CLONE_NEWNS | libc.CLONE_NEWNET | libc.CLONE_NEWUSER
    pid = libc.clone(child, child_stack_pointer, flags | SIGCHLD, )
    print("parent pid=%d ppid=%d child_pid=%d" % (os.getpid(), os.getppid(), pid))
    libc.uid_gid_mapping(pid, "0 %d 1" % os.getuid(), "0 %d 1" % os.getgid())
    os.waitpid(pid, 0)


if __name__ == "__main__":
    main()
