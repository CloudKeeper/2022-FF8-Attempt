"""
DEFAULT TYPECLASSES

"""

from evennia import (DefaultAccount, DefaultChannel, DefaultCharacter, 
                    DefaultExit, DefaultGuest, DefaultObject, DefaultRoom, 
                    DefaultScript)
from features.searchlock import SearchLockMixin
from features.delayed_exits import DelayedExitMixin
from features.seethrough_exits import SeeThroughExitMixin

class Account(DefaultAccount):
    """

    """

    pass


class Channel(DefaultChannel):
    """

    """

    pass


class Character(SearchLockMixin, DefaultCharacter): 
    """

    """

    pass


class Exit(DelayedExitMixin, SeeThroughExitMixin, DefaultExit):
    """

    """

    pass


class Guest(DefaultGuest):
    """

    """

    pass


class Object(SearchLockMixin, DefaultObject):
    """

    """

    pass


class Room(SearchLockMixin, DefaultRoom):
    """

    """

    pass


class Script(DefaultScript):
    """

    """

    pass
