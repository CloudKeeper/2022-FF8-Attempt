"""
See Through Exits - Needs Testing
A Mixin that allows an Exit to return it's locations description when it's the
target of a look command.
NOTES:
-Have levels? One where only the description, not items are given. Another
where all of it is given?
"""
from evennia import DefaultExit


class SeeThroughExitMixin(DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property.
    
    Attributes - Used if available:
        destination - The room who's description will be displayed on look.
        desc - Will display instead of target's description.
        preamble - Displayed before destination's description.
    """

    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.
        Args:
            looker (Object): Object doing the looking.
        """
        if not looker:
            return ""
        
        # Build description string
        string = f"|c{self.get_display_name(looker, pose=True)}|n\n"
        
        # If exit has a description, use that instead.
        desc = self.db.desc
        if desc:
            string += "%s" % desc
            return string
        
        # If destination, display preamble and it's description.
        destination = self.db.destination
        if destination:
            
            # Add preamble
            preamble = self.attributes.get("preamble", 
                           default = "Looking in this direction you see:")
            string += f"{preamble}\n"
            
            # Add target description
            string += f"{looker.at_look(destination)}"
        return string
            