# coding=utf-8
import os
from ctypes import CFUNCTYPE, c_int, create_string_buffer, c_void_p, cast
from signal import SIGCHLD
from mini_docker import libc, ip_link, command, iptables

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
    os.execle("/bin/bash", {"PS1": "[mini-docker]", "PATH": "/bin:/sbin:/usr/bin:/usr/local/bin"})
    return 0


def alloc_network(pid, container, ip_cidr, gateway_cidr):
    ns_path = "/var/run/netns/"
    if not os.path.exists(ns_path):
        os.mkdir(ns_path)
    command.execute(["ln", "-sf", "/proc/%s/ns/net" % pid, ns_path + container])
    veth_dp, veth_ns = "veth_%s_dp" % container, "veth_%s_ns" % container
    ip_link.add_veth(veth_dp, veth_ns)
    ip_link.add_link_to_ns(veth_ns, ns_name=container)
    ip_link.ip_link_up(veth_ns, ns_name=container)
    ip_link.add_link_ip_addr(veth_ns, ip_cidr, ns_name=container)
    ip_link.add_default_route(gateway_cidr.split("/")[0], ns_name=container)
    ip_link.ip_link_up(veth_dp)
    return veth_dp


def main():
    # 配置Host的Linux Bridge、NAT
    gateway_cidr = "10.100.0.1/16"
    bridge_name = "mini_docker_br0"
    ip_link.create_bridge(bridge_name)
    ip_link.add_link_ip_addr(bridge_name, gateway_cidr)
    ip_link.ip_link_up(bridge_name)
    iptables.create_forward(bridge_name)
    iptables.create_snat(gateway_cidr, "ens33")

    container_name = "mytest"
    container_ip = "10.100.0.2/16"

    child = CFUNCTYPE(c_int)(child_func)
    child_stack = create_string_buffer(STACK_SIZE)
    child_stack_pointer = c_void_p(cast(child_stack, c_void_p).value + STACK_SIZE)
    flags = libc.CLONE_NEWUTS | libc.CLONE_NEWPID | libc.CLONE_NEWIPC \
            | libc.CLONE_NEWNS | libc.CLONE_NEWNET | libc.CLONE_NEWUSER
    pid = libc.clone(child, child_stack_pointer, flags | SIGCHLD, )
    print("parent pid=%d ppid=%d child_pid=%d" % (os.getpid(), os.getppid(), pid))
    libc.uid_gid_mapping(pid, "0 %d 1" % os.getuid(), "0 %d 1" % os.getgid())

    # 设置
    veth_dp = alloc_network(pid, container_name, container_ip, gateway_cidr)
    ip_link.add_interface(bridge_name, veth_dp)
    os.waitpid(pid, 0)
    ip_link.del_ns(container_name)


if __name__ == "__main__":
    main()
