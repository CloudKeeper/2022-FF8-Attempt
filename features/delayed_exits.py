"""
Delayed Exit

This is an exit typeclass which creates a delayed exit, using the pose as a
check. If a player stops or poses whilst leaving, it stops the exit process.
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
        
        Delayed_exit traditionally uses traversing_object.ndb.destination
        to determine if the exit is going ahead. Here we use pose, so that the
        stop command will cover both posing and exiting.
        """

        # Initialise Move
        traversing_pose = " is leaving towards " + target_location.key
        traversing_object.db.pose = traversing_pose
        delay = int(self.attributes.get("delay", default = 0))

        def traverse_callback():
            """
            This callback will be called by utils.delay after self.db.delay 
            seconds, completing the actual movement.
            """
            # If leaving pose has been stopped or interrupted, kill movement.
            print(traversing_pose)
            print(traversing_object.db.pose)
            if not traversing_object.db.pose == traversing_pose:
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

        if delay == 0:
            # Move straight away.
            traverse_callback()
        
        if delay > 0:
            # Telegraph movement to traversing object
            traversing_object_msg = self.attributes.get("traversing_object_msg",
                            default = f"You start leaving towards {self.name}")
            traversing_object.msg(traversing_object_msg)

            # Telegraph movement to room
            room_leave_msg = self.attributes.get("room_leave_msg",
                            default = f"{traversing_object.name} starts leaving towards {self.name}")
            traversing_object.location.msg_contents(room_leave_msg, exclude=traversing_object)
            
            # Start delayed exit.
            utils.delay(delay, callback=traverse_callback)
