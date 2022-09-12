"""
See Through Exits - Needs Testing
A Mixin that allows an Exit to return it's locations description when it's the
target of a look command.
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
        
        Will return different things depending on exit.db.return_appearance_type
            "exit_desc" - will use the description of the exit object (default).
            "destination_desc" - will use the description of the destination object only - no content lists.
            "destination_appearance" - will use the full appearance of the destination object - incl contents.
        
        Args:
            looker (Object): Object doing the looking.
        """
        if not looker:
            return ""
        
        # Initiate description string
        string = f"|c{self.get_display_name(looker, pose=True)}|n\n"
        
        # Determine contents of description string
        return_appearance_type = self.attributes.get("return_appearance_type", 
                                default = "exit_desc")
        
        # If 'exit_desc' then use default description
        if return_appearance_type == "exit_desc":
            return super().return_appearance(looker)
        
        # If no 'destination' then use default description
        destination = self.destination
        if not destination:
            return super().return_appearance(looker)
        
        # Prepare for using destination descs
        preamble = self.attributes.get("preamble", 
                                default = "Looking in this direction you see:")
        
        # If 'destination_desc' then display preamble and it's description.
        if return_appearance_type == "destination_desc":
            string += f"{preamble}\n"
            string += f"{destination.db.desc}"
            return string
                    
        # If 'destination_appearance' then display preamble and it's return_appearance.
        if return_appearance_type == "destination_appearance":
            string += f"{preamble}\n"
            string += f"{looker.at_look(destination)}"
            return string
