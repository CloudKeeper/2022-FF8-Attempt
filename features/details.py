"""
Details
This is a Room mixin and command to implement Room Detials
Details are non-object descriptions stored on the room which a player can look
at to recieve a more detailed description.
TO DO:
Allow objects other than the room to have details?
"""

from evennia import utils, DefaultRoom, CmdSet, default_cmds
from django.conf import settings
_SEARCH_AT_RESULT = utils.object_from_module(settings.SEARCH_AT_RESULT)


# Mixin with Default Room

class DetailRoom():
    """
    This is a mixin that provides object functionality for details.
    """

    def return_detail(self, detailkey):
        """
        This looks for an Attribute "obj_details" and possibly
        returns the value of it.
        Args:
            detailkey (str): The detail being looked at. This is
                case-insensitive.
        """
        details = self.db.details
        if details:
            return details.get(detailkey.lower(), None)


# Give to Character Command Set

class CmdDetailLook(default_cmds.CmdLook):
    """
    Looks at the room and on details
    Usage:
        look
        look <obj>
        look <room detail>
        look *<account>
    Observes your location, details at your location or objects
    in your vicinity.
    """

    def func(self):
        """
        This is the hook function that actually does all the work. It is called
        by the cmdhandler right after self.parser() finishes, and so has access
        to all the variables defined therein.
        """
        caller = self.caller
        args = self.args
        
        # No arguement given, use room instead.
        if not args:
            target = [caller.location]
            # If no room, give error.
            if not target:
                caller.msg("You have no location to look at!")
                return
        else:
            target = caller.search(self.args, use_nicks=True, quiet=True)
        
        # If no target found, check for details.
        if not target:
            # Search for details.
            detail = caller.location.return_detail(args)
            if detail:
                self.msg((detail, {"type": "look"}), options=None)
                return
            # If no targets, default behaviour.
            _SEARCH_AT_RESULT(target, caller, args)
            return

        # If multiple targets, default behaviour.
        if len(target) > 1:
            _SEARCH_AT_RESULT(target, caller, args)
            return
        
        # If one target, return appearance.
        if target:
            self.msg((caller.at_look(target[0]), {"type": "look"}), options=None)