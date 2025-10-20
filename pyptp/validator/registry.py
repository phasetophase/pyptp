"""Discover validator subclasses located inside ``pyptp.validator``."""

import importlib
import inspect
import pkgutil

from pyptp.ptp_log import logger

from . import __name__ as _package_name
from . import __path__ as _validators_path
from .base import Validator


def discover_validators() -> list[type[Validator]]:
    """Return concrete :class:`Validator` subclasses found under the package."""
    found: list[type[Validator]] = []

    for _finder, module_name, _ispkg in pkgutil.walk_packages(_validators_path, prefix=_package_name + "."):
        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            logger.debug("Failed to import %s: %s", module_name, exc)
            continue

        for _cls_name, cls_obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls_obj, Validator) and cls_obj is not Validator:
                found.append(cls_obj)

    return found
