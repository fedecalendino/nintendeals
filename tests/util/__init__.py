from contextlib import contextmanager
from types import ModuleType
from unittest import mock


@contextmanager
def spy(module: ModuleType, name: str) -> mock.Mock:
    target = getattr(module, name)
    mocked = mock.Mock(wraps=target)
    setattr(module, name, mocked)

    yield mocked

    setattr(module, name, target)
