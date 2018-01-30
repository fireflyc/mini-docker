import os
import subprocess
import signal
import logging

LOG = logging.getLogger(__name__)


def execute(cmd, process_input=None, addl_env=None, check_exit_code=True, extra_ok_codes=None, is_async=False,
            with_sudo=False):
    if (process_input is None or
            isinstance(process_input, str)):
        _process_input = process_input
    else:
        _process_input = process_input.encode('utf-8')
    if with_sudo:
        cmd = sudo(cmd)
    obj, cmd = create_process(cmd, addl_env=addl_env)
    if is_async:
        return obj, cmd, 0

    _stdout, _stderr = obj.communicate(_process_input)
    returncode = obj.returncode
    obj.stdin.close()

    extra_ok_codes = extra_ok_codes or []
    if returncode and returncode not in extra_ok_codes:
        msg = ("Exit code: %(returncode)d; "
               "Stdin: %(stdin)s; "
               "Stdout: %(stdout)s; "
               "Stderr: %(stderr)s") % {
                  'returncode': returncode,
                  'stdin': process_input or '',
                  'stdout': _stdout,
                  'stderr': _stderr}
        if check_exit_code:
            raise RuntimeError(msg)
    else:
        LOG.debug("Exit code: %d", returncode)

    return _stdout, _stderr, returncode


def _subprocess_setup():
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def subprocess_popen(args, stdin=None, stdout=None, stderr=None,
                     env=None, preexec_fn=_subprocess_setup, close_fds=True):
    return subprocess.Popen(args, stdin=stdin, stdout=stdout,
                            stderr=stderr, preexec_fn=preexec_fn,
                            close_fds=close_fds, env=env)


def create_process(cmd, addl_env):
    LOG.debug("Running command: %s", " ".join(cmd))
    obj = subprocess_popen(cmd, env=addl_env,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

    return obj, cmd


def sudo(cmd):
    if os.geteuid() == 0:
        return cmd
    command = ["/usr/bin/sudo", "-n"]
    command.extend(cmd)
    return command
