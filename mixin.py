# Simple mixins for Python without multiple inheritance
# https://github.com/pfalcon/python-simple-mixin
# Copyright (c) 2021 Paul Sokolovsky
# Distributed under MIT License
import sys


def get_org_class(cls):
    if len(cls.__bases__) != 1:
        raise TypeError("base should be single fully-qualified name")
    if cls.__bases__[0] is not object:
        org_cls = cls.__bases__[0]
        in_bases = True
    else:
        mod = sys.modules[cls.__module__]
        org_cls = getattr(mod, cls.__name__)
        in_bases = False
    return org_cls, in_bases


def mix_one(to_cls, from_cls):
    for k, v in from_cls.__dict__.items():
        if k in ("__module__", "__dict__", "__weakref__"):
            continue
        if k == "__doc__" and v is None:
            continue
        setattr(to_cls, k, v)


def mixin(*classes):
    "Decorator to add mixins to a class at the time of creation."

    def _mixin(to_cls):
        for c in classes:
            mix_one(to_cls, c)
        return to_cls

    return _mixin


def postmixin(*classes):
    """Decorator to mix in to a class after its creation. Supports mixing
    in classes or just adhoc methods/class variables."""

    def _postmixin(cls):
        to_cls, in_bases = get_org_class(cls)
        for c in classes:
            mix_one(to_cls, c)
        mix_one(to_cls, cls)
        if in_bases:
            # If real class was specified as a base (supposedly, a class in
            # another module), we don't to "implicitly import it" under the
            # name of a class, so return None to be assigned to it. I.e.,
            # @postmixin
            # class Cls(mod.Cls):
            # Will lead to Cls being None in the current scope.
            return None
        else:
            return to_cls

    return _postmixin
