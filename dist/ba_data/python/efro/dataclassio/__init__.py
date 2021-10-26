# Released under the MIT License. See LICENSE for details.
#
"""Functionality for importing, exporting, and validating dataclasses.

This allows complex nested dataclasses to be flattened to json-compatible
data and restored from said data. It also gracefully handles and preserves
unrecognized attribute data, allowing older clients to interact with newer
data formats in a nondestructive manner.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from efro.dataclassio._outputter import _Outputter
from efro.dataclassio._inputter import _Inputter
from efro.dataclassio._base import Codec, IOAttrs
from efro.dataclassio._prep import ioprep, ioprepped, is_ioprepped_dataclass
from efro.dataclassio._pathcapture import DataclassFieldLookup

if TYPE_CHECKING:
    from typing import Any, Dict, Type, Tuple, Optional, List, Set

__all__ = [
    'Codec', 'IOAttrs', 'ioprep', 'ioprepped', 'is_ioprepped_dataclass',
    'DataclassFieldLookup', 'dataclass_to_dict', 'dataclass_to_json',
    'dataclass_from_dict', 'dataclass_from_json', 'dataclass_validate'
]

T = TypeVar('T')


def dataclass_to_dict(obj: Any,
                      codec: Codec = Codec.JSON,
                      coerce_to_float: bool = True) -> dict:
    """Given a dataclass object, return a json-friendly dict.

    All values will be checked to ensure they match the types specified
    on fields. Note that a limited set of types and data configurations is
    supported.

    Values with type Any will be checked to ensure they match types supported
    directly by json. This does not include types such as tuples which are
    implicitly translated by Python's json module (as this would break
    the ability to do a lossless round-trip with data).

    If coerce_to_float is True, integer values present on float typed fields
    will be converted to floats in the dict output. If False, a TypeError
    will be triggered.
    """

    out = _Outputter(obj,
                     create=True,
                     codec=codec,
                     coerce_to_float=coerce_to_float).run()
    assert isinstance(out, dict)
    return out


def dataclass_to_json(obj: Any,
                      coerce_to_float: bool = True,
                      pretty: bool = False) -> str:
    """Utility function; return a json string from a dataclass instance.

    Basically json.dumps(dataclass_to_dict(...)).
    """
    import json
    jdict = dataclass_to_dict(obj=obj,
                              coerce_to_float=coerce_to_float,
                              codec=Codec.JSON)
    if pretty:
        return json.dumps(jdict, indent=2, sort_keys=True)
    return json.dumps(jdict, separators=(',', ':'))


def dataclass_from_dict(cls: Type[T],
                        values: dict,
                        codec: Codec = Codec.JSON,
                        coerce_to_float: bool = True,
                        allow_unknown_attrs: bool = True,
                        discard_unknown_attrs: bool = False) -> T:
    """Given a dict, return a dataclass of a given type.

    The dict must be formatted to match the specified codec (generally
    json-friendly object types). This means that sequence values such as
    tuples or sets should be passed as lists, enums should be passed as their
    associated values, nested dataclasses should be passed as dicts, etc.

    All values are checked to ensure their types/values are valid.

    Data for attributes of type Any will be checked to ensure they match
    types supported directly by json. This does not include types such
    as tuples which are implicitly translated by Python's json module
    (as this would break the ability to do a lossless round-trip with data).

    If coerce_to_float is True, int values passed for float typed fields
    will be converted to float values. Otherwise a TypeError is raised.

    If allow_unknown_attrs is False, AttributeErrors will be raised for
    attributes present in the dict but not on the data class. Otherwise they
    will be preserved as part of the instance and included if it is
    exported back to a dict, unless discard_unknown_attrs is True, in which
    case they will simply be discarded.
    """
    return _Inputter(cls,
                     codec=codec,
                     coerce_to_float=coerce_to_float,
                     allow_unknown_attrs=allow_unknown_attrs,
                     discard_unknown_attrs=discard_unknown_attrs).run(values)


def dataclass_from_json(cls: Type[T],
                        json_str: str,
                        coerce_to_float: bool = True,
                        allow_unknown_attrs: bool = True,
                        discard_unknown_attrs: bool = False) -> T:
    """Utility function; return a dataclass instance given a json string.

    Basically dataclass_from_dict(json.loads(...))
    """
    import json
    return dataclass_from_dict(cls=cls,
                               values=json.loads(json_str),
                               coerce_to_float=coerce_to_float,
                               allow_unknown_attrs=allow_unknown_attrs,
                               discard_unknown_attrs=discard_unknown_attrs)


def dataclass_validate(obj: Any,
                       coerce_to_float: bool = True,
                       codec: Codec = Codec.JSON) -> None:
    """Ensure that values in a dataclass instance are the correct types."""

    # Simply run an output pass but tell it not to generate data;
    # only run validation.
    _Outputter(obj, create=False, codec=codec,
               coerce_to_float=coerce_to_float).run()
