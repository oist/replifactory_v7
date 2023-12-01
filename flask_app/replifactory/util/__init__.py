import contextlib
import copy
import os
import pickle
import queue
import re
import shutil
import sys
import tempfile
import threading
import time
import unicodedata
from collections.abc import Set
from typing import Iterable, Literal, Union

import numpy as np
import pandas as pd


def read_file_tail(filepath, lines=1000, _buffer=4096):
    lines = int(lines)
    with open(filepath, "rb") as f:
        # place holder for the lines found
        lines_found = []

        # block counter will be multiplied by buffer
        # to get the block size from the end
        block_counter = -1

        # loop until we find X lines
        while len(lines_found) < lines + 1:
            try:
                f.seek(block_counter * _buffer, os.SEEK_END)
            except IOError:  # either file is too small, or too many lines requested
                f.seek(0)
                lines_found = f.readlines()
                break
            lines_found = f.readlines()
            # we found enough lines, get out
            # decrement the block counter to get the
            # next X bytes
            block_counter -= 1
    return lines_found


def read_csv_tail(filepath, lines=1000, _buffer=4096):
    """Tail a file and get X lines from the end
    modified from https://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-similar-to-tail/136368#136368
    """
    header = open(filepath).readline().rstrip().split(",")
    lines_found = read_file_tail(filepath=filepath, lines=lines, _buffer=_buffer)

    lines_found = lines_found[1:]  # cut header if lines > total lines in file
    lines_found = lines_found[-lines:]
    lines_found = [
        line.decode().rstrip().replace(" ", "").split(",") for line in lines_found
    ]
    lines_found = np.array(lines_found)
    data = lines_found[:, 1:]
    d = []
    for data_line in data:
        try:
            d += [pd.to_numeric(data_line)]
        except ValueError:
            line = []
            for value in data_line:
                try:
                    line += [pd.to_numeric(value)]
                except ValueError:
                    line += [np.nan]
            d += line
    data = d

    data = [pd.to_numeric(data_line) for data_line in data]
    timestamp = lines_found[:, 0]

    df = pd.DataFrame(data, columns=header[1:])

    try:
        timestamp = pd.to_numeric(timestamp)  # 5 ms  for 10 000 lines
    except ValueError:
        timestamp = pd.to_datetime(timestamp)  # 1.3 seconds for 10 000 lines
        timestamp = pd.to_numeric(timestamp)

    df.index = timestamp

    df.index.name = header[0]
    return df


class CultureDict(dict):
    def __init__(self, device):
        super().__init__()
        self.device = device

    def __setitem__(self, vial, c):
        if c is not None:
            assert os.path.exists(
                self.device.directory
            ), "device directory does not exist:"
            new_culture_directory = os.path.join(
                self.device.directory, "vial_%d" % vial
            )

            existing_config = os.path.join(new_culture_directory, "culture_config.yaml")
            if c.directory is None and os.path.exists(existing_config):
                raise RuntimeError("Culture %d config exists" % vial)
                # q = input("replace culture %d config?[y/n]" % vial)
                # assert q == "y"
            if not os.path.exists(new_culture_directory):
                os.mkdir(new_culture_directory)
            c.vial_number = vial
            # c.experiment_directory = self.device.directory
            c.directory = new_culture_directory
            c.device = self.device

        super().__setitem__(vial, c)


def write_variable(culture, variable_name, value):
    filepath = os.path.join(culture.directory, "%s.csv" % variable_name)
    if not os.path.exists(filepath):
        with open(filepath, "w+") as f:
            f.write("time,%s\n" % variable_name)
    with open(filepath, "a") as f:
        data_string = "%.1f, %.5f\n" % (int(time.time()), value)
        f.write(data_string)


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class BraceMessage:
    def __init__(self, fmt, /, *args, **kwargs):
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        try:
            return self.fmt.format(*self.args, **self.kwargs)
        except TypeError:
            return f"Wron args for format {self.fmt}. args: {self.args}, kwargs: {self.kwargs}"


class ArrayOfBytesAsInt:
    def __init__(
        self,
        value: Union[bytes, bytearray, Iterable[int]],
        byteorder: Literal["little", "big"] = "big",
    ):
        self.value = value
        self.byteorder = byteorder

    def __str__(self):
        result: int = 0
        byte_counter = 0
        for byte in self.value:
            if self.byteorder == "little":
                result |= byte << byte_counter * 8
            else:
                result = result << 8 | byte
            byte_counter += 1
        return result.__str__()


class InvariantContainer:
    def __init__(self, initial_data=None, guarantee_invariant=None):
        from threading import RLock

        if guarantee_invariant is None:
            guarantee_invariant = lambda data: data

        self._data = []
        self._mutex = RLock()
        self._invariant = guarantee_invariant

        if initial_data is not None and isinstance(initial_data, Iterable):
            for item in initial_data:
                self.append(item)

    def append(self, item):
        with self._mutex:
            self._data.append(item)
            self._data = self._invariant(self._data)

    def remove(self, item):
        with self._mutex:
            self._data.remove(item)
            self._data = self._invariant(self._data)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self._data.__iter__()


class CaseInsensitiveSet(Set):
    """
    Basic case insensitive set

    Any str values will be stored and compared in lower case. Other value types are left as-is.
    """

    def __init__(self, *args):
        self.data = {x.lower() if isinstance(x, str) else x for x in args}

    def __contains__(self, item):
        if isinstance(item, str):
            return item.lower() in self.data
        else:
            return item in self.data

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)


def silent_remove(file):
    """
    Silently removes a file. Does not raise an error if the file doesn't exist.

    Arguments:
        file (string): The path of the file to be removed
    """

    try:
        os.remove(file)
    except OSError:
        pass


# figure out current umask - sadly only doable by setting a new one and resetting it, no query method
UMASK = os.umask(0)
os.umask(UMASK)


@contextlib.contextmanager
def atomic_write(
    filename,
    mode="w+b",
    encoding="utf-8",
    prefix="tmp",
    suffix="",
    permissions=None,
    max_permissions=0o777,
):
    if permissions is None:
        permissions = 0o664 & ~UMASK
    if os.path.exists(filename):
        permissions |= os.stat(filename).st_mode
    permissions &= max_permissions

    # Ensure we create the file in the target dir so our move is atomic. See #3719
    dir = os.path.dirname(filename)
    kwargs = {
        "mode": mode,
        "prefix": prefix,
        "suffix": suffix,
        "dir": dir,
        "delete": False,
    }
    if "b" not in mode:
        kwargs["encoding"] = encoding

    fd = tempfile.NamedTemporaryFile(**kwargs)
    try:
        try:
            yield fd
        finally:
            fd.close()
        os.chmod(fd.name, permissions)
        shutil.move(fd.name, filename)
    finally:
        silent_remove(fd.name)


def fast_deepcopy(obj):
    # the best way to implement this would be as a C module, that way we'd be able to use
    # the fast path every time.
    try:
        # implemented in C and much faster than deepcopy:
        # https://stackoverflow.com/a/29385667
        return pickle.loads(pickle.dumps(obj, pickle.HIGHEST_PROTOCOL))
    except (AttributeError, pickle.PicklingError):
        # fall back when something unpickable is found
        return copy.deepcopy(obj)


def dict_merge(a, b, leaf_merger=None, in_place=False):
    """
    Recursively deep-merges two dictionaries.

    Based on https://www.xormedia.com/recursively-merge-dictionaries-in-python/

    Example::

        >>> a = dict(foo="foo", bar="bar", fnord=dict(a=1))
        >>> b = dict(foo="other foo", fnord=dict(b=2, l=["some", "list"]))
        >>> expected = dict(foo="other foo", bar="bar", fnord=dict(a=1, b=2, l=["some", "list"]))
        >>> dict_merge(a, b) == expected
        True
        >>> dict_merge(a, None) == a
        True
        >>> dict_merge(None, b) == b
        True
        >>> dict_merge(None, None) == dict()
        True
        >>> def leaf_merger(a, b):
        ...     if isinstance(a, list) and isinstance(b, list):
        ...         return a + b
        ...     raise ValueError()
        >>> result = dict_merge(dict(l1=[3, 4], l2=[1], a="a"), dict(l1=[1, 2], l2="foo", b="b"), leaf_merger=leaf_merger)
        >>> result.get("l1") == [3, 4, 1, 2]
        True
        >>> result.get("l2") == "foo"
        True
        >>> result.get("a") == "a"
        True
        >>> result.get("b") == "b"
        True
        >>> c = dict(foo="foo")
        >>> dict_merge(c, {"bar": "bar"}) is c
        False
        >>> dict_merge(c, {"bar": "bar"}, in_place=True) is c
        True

    Arguments:
        a (dict): The dictionary to merge ``b`` into
        b (dict): The dictionary to merge into ``a``
        leaf_merger (callable): An optional callable to use to merge leaves (non-dict values)
        in_place (boolean): If set to True, a will be merged with b in place, meaning a will be modified

    Returns:
        dict: ``b`` deep-merged into ``a``
    """

    if a is None:
        a = {}
    if b is None:
        b = {}

    if not isinstance(b, dict):
        return b

    if in_place:
        result = a
    else:
        result = fast_deepcopy(a)

    for k, v in b.items():
        if k in result and isinstance(result[k], dict):
            result[k] = dict_merge(
                result[k], v, leaf_merger=leaf_merger, in_place=in_place
            )
        else:
            merged = None
            if k in result and callable(leaf_merger):
                try:
                    merged = leaf_merger(result[k], v)
                except ValueError:
                    # can't be merged by leaf merger
                    pass

            if merged is None:
                merged = fast_deepcopy(v)

            result[k] = merged
    return result


def generate_api_key():
    import uuid

    return "".join("%02X" % z for z in bytes(uuid.uuid4().bytes))


def to_unicode(
    s_or_u: Union[str, bytes], encoding: str = "utf-8", errors: str = "strict"
) -> str:
    """
    Make sure ``s_or_u`` is a string (str).

    Arguments:
        s_or_u (str or bytes): The value to convert
        encoding (str): encoding to use if necessary, see :meth:`python:bytes.decode`
        errors (str): error handling to use if necessary, see :meth:`python:bytes.decode`
    Returns:
        str: converted string.
    """
    if s_or_u is None:
        return s_or_u

    if not isinstance(s_or_u, (str, bytes)):
        s_or_u = str(s_or_u)

    if isinstance(s_or_u, bytes):
        return s_or_u.decode(encoding, errors=errors)
    else:
        return s_or_u


def is_hidden_path(path):
    if path is None:
        # we define a None path as not hidden here
        return False

    path = to_unicode(path)

    filename = os.path.basename(path)
    if filename.startswith("."):
        # filenames starting with a . are hidden
        return True

    if sys.platform == "win32":
        # if we are running on windows we also try to read the hidden file
        # attribute via the windows api
        try:
            import ctypes

            attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
            assert attrs != -1  # INVALID_FILE_ATTRIBUTES == -1
            return bool(attrs & 2)  # FILE_ATTRIBUTE_HIDDEN == 2
        except (AttributeError, AssertionError):
            pass

    # if we reach that point, the path is not hidden
    return False


def get_fully_qualified_classname(o):
    """
    Returns the fully qualified class name for an object.

    Based on https://stackoverflow.com/a/2020083

    Args:
            o: the object of which to determine the fqcn

    Returns:
            (str) the fqcn of the object
    """

    module = getattr(o.__class__, "__module__", None)
    if module is None:
        return o.__class__.__name__
    return module + "." + o.__class__.__name__


def slugify(value):
    # split accented characters into their base characters and diacritical marks
    value = unicodedata.normalize("NFKD", value)
    # remove all the accents, which happen to be all in the u03xx UNICODE block
    value = value.encode("ascii", "ignore").decode("ascii").lower()
    # remove non-alphanumeric characters and replace them with hyphens
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    # remove consecutive hyphens
    value = re.sub(r"[-]+", "-", value)
    return value


class TypeAlreadyInQueue(Exception):
    def __init__(self, t, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.type = t


class PrependableQueue(queue.Queue):
    def __init__(self, maxsize=0):
        queue.Queue.__init__(self, maxsize=maxsize)

    def prepend(self, item, block=True, timeout=True):
        from time import time as _time

        self.not_full.acquire()
        try:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() == self.maxsize:
                        raise queue.Full
                elif timeout is None:
                    while self._qsize() >= self.maxsize:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = _time() + timeout
                    while self._qsize() == self.maxsize:
                        remaining = endtime - _time()
                        if remaining <= 0:
                            raise queue.Full
                        self.not_full.wait(remaining)
            self._prepend(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()
        finally:
            self.not_full.release()

    def _prepend(self, item):
        self.queue.appendleft(item)


class JobQueue(PrependableQueue):
    pass


class TypedQueue(PrependableQueue):
    def __init__(self, maxsize=0):
        PrependableQueue.__init__(self, maxsize=maxsize)
        self._lookup = set()

    def put(self, item, item_type=None, *args, **kwargs):
        PrependableQueue.put(self, (item, item_type), *args, **kwargs)

    def get(self, *args, **kwargs):
        item, _ = PrependableQueue.get(self, *args, **kwargs)
        return item

    def prepend(self, item, item_type=None, *args, **kwargs):
        PrependableQueue.prepend(self, (item, item_type), *args, **kwargs)

    def _put(self, item):
        _, item_type = item
        if item_type is not None:
            if item_type in self._lookup:
                raise TypeAlreadyInQueue(
                    item_type, f"Type {item_type} is already in queue"
                )
            else:
                self._lookup.add(item_type)

        PrependableQueue._put(self, item)

    def _get(self):
        item = PrependableQueue._get(self)
        _, item_type = item

        if item_type is not None:
            self._lookup.discard(item_type)

        return item

    def _prepend(self, item):
        _, item_type = item
        if item_type is not None:
            if item_type in self._lookup:
                raise TypeAlreadyInQueue(
                    item_type, f"Type {item_type} is already in queue"
                )
            else:
                self._lookup.add(item_type)

        PrependableQueue._prepend(self, item)


class CountedEvent:
    def __init__(self, value=0, minimum=0, maximum=None, **kwargs):
        self._counter = 0
        self._min = minimum
        self._max = kwargs.get("max", maximum)
        self._mutex = threading.RLock()
        self._event = threading.Event()

        self._internal_set(value)

    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, val):
        with self._mutex:
            self._min = val

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, val):
        with self._mutex:
            self._max = val

    @property
    def is_set(self):
        return self._event.is_set

    @property
    def counter(self):
        with self._mutex:
            return self._counter

    def set(self):
        with self._mutex:
            self._internal_set(self._counter + 1)

    def clear(self, completely=False):
        with self._mutex:
            if completely:
                self._internal_set(0)
            else:
                self._internal_set(self._counter - 1)

    def reset(self):
        self.clear(completely=True)

    def wait(self, timeout=None):
        self._event.wait(timeout)

    def blocked(self):
        return self.counter <= 0

    def acquire(self, blocking=1):
        return self._mutex.acquire(blocking=blocking)

    def release(self):
        return self._mutex.release()

    def _internal_set(self, value):
        self._counter = value
        if self._counter <= 0:
            if self._min is not None and self._counter < self._min:
                self._counter = self._min
            self._event.clear()
        else:
            if self._max is not None and self._counter > self._max:
                self._counter = self._max
            self._event.set()
