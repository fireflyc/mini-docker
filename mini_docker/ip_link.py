import os

from mini_docker import libc, command


def add_link_to_ns(if_name, ns_name):
    cmd = ["ip", "netns", "exec", ns_name]
    cmd.extend(["ip", "addr", "show", "dev", if_name])
    out, _, _ = command.execute(cmd, check_exit_code=False)
    if out.strip() == "":
        command.execute(["ip", "link", "set", if_name, "netns", ns_name])


def add_link_ip_addr(if_name, ip_addr=None, mac_addr=None, ns_name=None):
    cmd = []
    if ns_name is not None:
        cmd.extend(["ip", "netns", "exec", ns_name])

    if mac_addr:
        mac_cmd = []
        mac_cmd.extend(cmd)
        mac_cmd.extend(["ip", "link", "set", if_name, "address", mac_addr])
        command.execute(mac_cmd)
    if ip_addr:
        cmd.extend(["ip", "addr", "add", ip_addr, "dev", if_name])
        command.execute(cmd, check_exit_code=False)


def get_link_ip_addr(if_name, ns_name=None):
    cmd = []
    if ns_name is not None:
        cmd.extend(["ip", "netns", "exec", ns_name])
    cmd.extend(["ip", "addr", "show", "dev", if_name])
    out, _, _ = command.execute(cmd)
    for line in out.split("\n"):
        if line.strip().startswith("inet"):
            return line.strip().split()[1].strip()


def del_link_ip_addr(if_name, ip_addr=None, ns_name=None):
    cmd = []
    if ns_name is not None:
        cmd.extend(["ip", "netns", "exec", ns_name])
    if ip_addr is None:
        cmd.extend(["ip", "addr", "flush", "dev", if_name])
    else:
        cmd.extend(["ip", "addr", "del", ip_addr, "dev", if_name])
    command.execute(cmd, check_exit_code=False)


def del_link(if_name, ns_name=None):
    cmd = []
    if ns_name is not None:
        cmd.extend(["ip", "netns", "exec", ns_name])
    cmd.extend(["ip", "link", "del", if_name])
    command.execute(cmd)


def add_veth(if_name, peer_if_name, check_exit_code=False):
    out, _, _ = command.execute(["ip", "link", "show", if_name, "type", "veth"], check_exit_code=check_exit_code)
    if out.find(if_name) != -1:
        return
    cmd = ["ip", "link", "add", if_name, "type", "veth", "peer", "name", peer_if_name]
    command.execute(cmd, check_exit_code=check_exit_code)


def ip_link_up(if_name, ns_name=None):
    cmd = []
    if ns_name is not None:
        cmd.extend(["ip", "netns", "exec", ns_name])
    cmd.extend(["ip", "link", "set", if_name, "up"])
    command.execute(cmd)


def create_ns(ns_name, check_exit_code=False):
    command.execute(["ip", "netns", "add", ns_name], check_exit_code=check_exit_code)


def del_ns(ns_name):
    command.execute(["ip", "netns", "del", ns_name])


def add_route(ip_addr, via_gw, ns_name, check_exit_code=False):
    cmd = []
    if ns_name is not None:
        cmd.extend(["ip", "netns", "exec", ns_name])
    cmd.extend(["ip", "route", "add", ip_addr, "via", via_gw])
    command.execute(cmd, check_exit_code=check_exit_code)


def add_default_route(via_gw, ns_name, check_exit_code=False):
    cmd = []
    if ns_name is not None:
        cmd.extend(["ip", "netns", "exec", ns_name])
    cmd.extend(["ip", "route", "add", "default", "via", via_gw])
    command.execute(cmd, check_exit_code=check_exit_code)


def enable_ip_forward(ns_name, check_exit_code=False):
    cmd = []
    if ns_name is not None:
        cmd.extend(["ip", "netns", "exec", ns_name])
    cmd.extend(["sysctl", "net.ipv4.ip_forward=1"])
    command.execute(cmd, check_exit_code=check_exit_code)


def delete_router(ip_addr, ns_name, check_exit_code=False):
    cmd = []
    if ns_name is not None:
        cmd.extend(["ip", "netns", "exec", ns_name])
    cmd.extend(["ip", "route", "delete", ip_addr])
    command.execute(cmd, check_exit_code=check_exit_code)


def create_bridge(bridge_name):
    cmd = ["brctl", "addbr", bridge_name]
    command.execute(cmd, check_exit_code=False)


def add_interface(bridge_name, if_name):
    cmd = ["brctl", "addif", bridge_name, if_name]
    command.execute(cmd, check_exit_code=False)
