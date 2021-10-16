import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from clize import run
import prettytable

from . import __version__


def _get_mtime(path):
    stat = path.stat()
    return datetime.fromtimestamp(stat.st_mtime)


def _get_relative(path):
    try:
        return Path(path).relative_to(Path.cwd())
    except ValueError:
        return path


class Future:
    def __init__(self, delta):
        self._delta = delta
        self.now = datetime.now()

    def __contains__(self, path):
        return _get_mtime(path) > self.now + self._delta


class Fix:
    def __init__(self, path, future):
        self.path = path
        self._future = future
        self.mtime = _get_mtime(path)
        self.fixed_mtime = self._find_nearest_mtime(path)

    def execute(self):
        stat = self.path.stat()
        print(f"Fixing '{_get_relative(self.path.resolve())}'' modified '{self.mtime}'' to "
              f"'{self.fixed_mtime}'...")
        os.utime(self.path, (stat.st_atime, self.fixed_mtime.timestamp()))

    def _find_nearest_mtime(self, path):
        while path in self._future:
            if path == path.parent:
                return self._future.now
            path = path.parent
        return _get_mtime(path)


class Command:

    _DEFAULT_DELTA = timedelta(days=1)

    def __init__(self):
        self._future = Future(self._DEFAULT_DELTA)

    def run(self, path, execute, version):
        if version:
            print(__version__)
            sys.exit(1)

        if not path:
            path = Path.cwd()
        else:
            path = Path(path).resolve()

        nodes = self._find_nodes_in_future(path)
        fixes = [Fix(node, self._future) for node in nodes]

        t = prettytable.PrettyTable(["Path", "Modified", "Fixed modified"])
        t.align['Path'] = 'l'
        for fix in fixes:
            path = _get_relative(fix.path)
            t.add_row([path, fix.mtime, fix.fixed_mtime])
        print(t)

        if not execute:
            print("Use --execute to fix")
        else:
            for fix in fixes:
                fix.execute()

        sys.exit(0)

    def _find_nodes_in_future(self, path):
        nodes = []

        if path.is_symlink():
            return nodes

        try:

            if path in self._future:
                print("This node is in the future:", _get_relative(path))
                nodes.append(path)

            if path.is_dir():
                for node in path.iterdir():
                    nodes.extend(self._find_nodes_in_future(node))

        except OSError as e:
            print(e)
            return nodes

        return nodes


def fix_future(path=None, *, execute=False, version=False):
    c = Command()
    c.run(path, execute, version)


def main():
    run(fix_future)
