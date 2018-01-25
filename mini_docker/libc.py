import ctypes

import os
from signal import SIGKILL

libc = ctypes.CDLL("libc.so.6", use_errno=True)

# namespace flag
CLONE_NEWNS = 0x00020000  # /* New mount namespace group */
CLONE_NEWUTS = 0x04000000  # /* New utsname namespace */
CLONE_NEWIPC = 0x08000000  # /* New ipc namespace */
CLONE_NEWUSER = 0x10000000  # /* New user namespace */
CLONE_NEWPID = 0x20000000  # /* New pid namespace */
CLONE_NEWNET = 0x40000000  # /* New network namespace */

# mount flag
MS_RDONLY = 1  # /* Mount read-only */
MS_NOSUID = 2  # /* Ignore suid and sgid bits */
MS_NODEV = 4  # /* Disallow access to device special files */
MS_NOEXEC = 8  # /* Disallow program execution */
MS_SYNCHRONOUS = 16  # /* Writes are synced at once */
MS_REMOUNT = 32  # /* Alter flags of a mounted FS */
MS_MANDLOCK = 64  # /* Allow mandatory locks on an FS */
MS_DIRSYNC = 128  # /* Directory modifications are synchronous */
MS_NOATIME = 1024  # /* Do not update access times. */
MS_NODIRATIME = 2048  # /* Do not update directory access times */
MS_BIND = 4096
MS_MOVE = 8192
MS_REC = 16384
MS_VERBOSE = 32768  # /* War is peace. Verbosity is silence. MS_VERBOSE is deprecated. */
MS_SILENT = 32768
MS_POSIXACL = (1 << 16)  # /* VFS does not apply the umask */
MS_UNBINDABLE = (1 << 17)  # /* change to unbindable */
MS_PRIVATE = (1 << 18)  # /* change to private */
MS_SLAVE = (1 << 19)  # /* change to slave */
MS_SHARED = (1 << 20)  # /* change to shared */
MS_RELATIME = (1 << 21)  # /* Update atime relative to mtime/ctime. */
MS_KERNMOUNT = (1 << 22)  # /* this is a kern_mount call */
MS_I_VERSION = (1 << 23)  # /* Update inode I_version field */
MS_STRICTATIME = (1 << 24)  # /* Always perform atime updates */
MS_LAZYTIME = (1 << 25)  # /* Update the on-disk [acm]times lazily */

# umount flag
MNT_FORCE = 0x00000001  # /* Attempt to forcibily umount */
MNT_DETACH = 0x00000002  # /* Just detach from the tree */
MNT_EXPIRE = 0x00000004  # /* Mark for expiry */
UMOUNT_NOFOLLOW = 0x00000008  # /* Don't follow symlink on umount */
UMOUNT_UNUSED = 0x80000000  # /* Flag guaranteed to be unused */


def clone(func, stack, flags):
    result = libc.clone(func, stack, flags)
    if result < 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))
    return result


def sethostname(hostname):
    result = libc.sethostname(hostname, len(hostname))
    if result < 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))
    return result


def mount(src, target, fs, flags=0, data=""):
    result = libc.mount(src, target, fs, flags, data)
    if result < 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))
    return result


def pivot_root(new_root, old_root):
    print(new_root)
    print(old_root)
    result = libc.pivot_root(new_root, old_root)
    if result < 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))
    return result


def umount(target, flags=0):
    result = libc.umount2(target, flags)
    if result < 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))
    return result


def uid_gid_mapping(pid, uid_map, gid_map):
    proc = "/proc"

    def write_map_file(mapping, map_file):
        try:
            with open(map_file, 'w') as f:
                f.write(mapping)
        except IOError as e:
            os.kill(pid, SIGKILL)
            raise IOError(
                "Can not write %s: %s\nAborting!" % (map_file, e)
            )

    if uid_map:
        write_map_file(uid_map, "%s/%s/uid_map" % (proc, pid))

    if gid_map:
        write_map_file(gid_map, "%s/%s/gid_map" % (proc, pid))
