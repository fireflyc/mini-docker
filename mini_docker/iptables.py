# coding=utf-8
from mini_docker import command

_IPTABLES_BIN = "iptables"


def create_snat(ip_addr_cidr, ifi_name):
    cmd = ["POSTROUTING", "-t", "nat", "-s", ip_addr_cidr, "-o", ifi_name, "-j", "MASQUERADE"]
    _, _, returncode = command.execute([_IPTABLES_BIN, "-C"] + cmd, check_exit_code=False)
    if returncode != 0:
        command.execute([_IPTABLES_BIN, "-A"] + cmd, check_exit_code=False)


def create_forward(ifi_name):
    cmd = ["FORWARD", "-i", ifi_name, "!", "-o", ifi_name, "-j", "ACCEPT"]
    _, _, returncode = command.execute([_IPTABLES_BIN, "-C"] + cmd, check_exit_code=False)
    if returncode != 0:
        command.execute([_IPTABLES_BIN, "-A"] + cmd, check_exit_code=False)

    cmd = ["FORWARD", "-o", ifi_name, "-m", "conntrack", "--ctstate", "RELATED,ESTABLISHED", "-j", "ACCEPT"]
    _, _, returncode = command.execute([_IPTABLES_BIN, "-C"] + cmd, check_exit_code=False)
    if returncode != 0:
        command.execute([_IPTABLES_BIN, "-A"] + cmd, check_exit_code=False)
