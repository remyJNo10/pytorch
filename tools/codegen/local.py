import threading
from contextlib import contextmanager
from typing import Optional, Iterator

from tools.codegen.model import UseC10Dispatcher

# Simple dynamic scoping implementation.  The name "parametrize" comes
# from Racket.
#
# WARNING WARNING: LOOKING TO EDIT THIS FILE?  Think carefully about
# why you need to add a toggle to the global behavior of code
# generation.  The parameters here should really only be used
# for "temporary" situations, where we need to temporarily change
# the codegen in some cases because we cannot conveniently update
# all call sites, and are slated to be eliminated once all call
# sites are eliminated.  If you don't have a plan for how to get there,
# DON'T add a new entry here.

class Locals(threading.local):
    use_c10_dispatcher: Optional[UseC10Dispatcher] = None
    hack_const_mutable_self: bool = False
_locals = Locals()

# The use_c10_dispatcher field in native_functions.yaml is used to
# control codegen behavior, so that we can handle cases where
# Dispatcher templating logic can't handle.  In the terminal
# state, use_c10_dispatcher should always be UseC10Dispatcher.full
# and this flag can be eliminated.
def use_c10_dispatcher() -> UseC10Dispatcher:
    assert _locals.use_c10_dispatcher is not None, \
        "need to initialize local.use_c10_dispatcher with local.parametrize"
    return _locals.use_c10_dispatcher

# This is used to maintain compat, see Note [Byte-for-byte compatibility]
# It can be removed when we drop compat.
def hack_const_mutable_self() -> bool:
    return _locals.hack_const_mutable_self

@contextmanager
def parametrize(*, use_c10_dispatcher: UseC10Dispatcher, hack_const_mutable_self: bool) -> Iterator[None]:
    old_use_c10_dispatcher = _locals.use_c10_dispatcher
    old_hack_const_mutable_self = _locals.hack_const_mutable_self
    try:
        _locals.use_c10_dispatcher = use_c10_dispatcher
        _locals.hack_const_mutable_self = hack_const_mutable_self
        yield
    finally:
        _locals.use_c10_dispatcher = old_use_c10_dispatcher
        _locals.hack_const_mutable_self = old_hack_const_mutable_self
