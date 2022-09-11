"""
Delayed Exit - Needs Testing
A Mixin that delays leaving a location.
TODO:
-Update pose
"""
from evennia import DefaultExit
from evennia import utils


class DelayedExitMixin(DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property.
    
    Attributes - Used if available:
        delay - Defines the delay (default - 5s)
        player_leave_msg - Response to exit command 
                           (default - "You start moving towards {self.key}")
        room_leave_msg - Message to room on exit command 
                         (default - "{traversing_object} starts moving towards {self.key}")
        err_traverse - Response to Player if unable to traverse after delay.
    """

    def at_traverse(self, traversing_object, target_location):
        """
        Implements the actual traversal, using utils.delay to delay the move_to.
        """
        
        # Call back handles the movement after a delay.
        def traverse_callback():
            "This callback will be called by utils.delay after self.db.delay seconds."
            # If movement has been stopped or interrupted, kill movement.
            if not traversing_object.ndb.destination == target_location:
                return
            
            # Otherwise deal with movement.
            source_location = traversing_object.location
            if traversing_object.move_to(target_location):
                 self.at_after_traverse(traversing_object, source_location)
            else:
                if self.db.err_traverse:
                    # if exit has a better error message, let's use it.
                    traversing_object.msg(self.db.err_traverse)
                else:
                    # No shorthand error message. Call hook.
                    self.at_failed_traverse(traversing_object)
        
        # Initialise Move
        traversing_object.ndb.destination = target_location
        delay = int(self.attributes.get("delay", default = 5))
        
        if delay == 0:
            # Move straight away.
            traverse_callback()
        
        if delay > 0:
            # Telegraph movement
            personal_leave_msg = self.attributes.get("player_leave_msg",
                            default = f"You start moving towards {self.name}")
            room_leave_msg = self.attributes.get("room_leave_msg",
                            default = f"{traversing_object.name} starts moving towards {self.name}")
            traversing_object.msg(personal_leave_msg)
            traversing_object.location.msg_contents(room_leave_msg)
            
            # Start delayed exit.
            utils.delay(delay, callback=traverse_callback)