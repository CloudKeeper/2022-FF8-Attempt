"""
Pose System
Pose system to set room-persistent poses, visible in room descriptions and 
when looking at the person/object.  This is a simple Attribute that modifies 
how the characters is viewed when in a room as sdesc + pose. Moving to a 
new room resets your pose to the default.
Currently allows player from being able to pose himself when locked from editting.
TO DO:
-I currently use "edit" permission to pose objects. Do I want to be more specific?
"""
from evennia import DefaultObject
from django.conf import settings
from evennia.utils import utils

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class PoseMixin(DefaultObject):
    """
    This class implements the base functionality for poses.
    
    PoseMixin - Overwrites:
        (super) at_object_creation
        get_display_name
        return_appearance
    """

    def at_object_creation(self):
        """
        Called at initial creation.
        """
        super().at_object_creation()

        # emoting/recog data
        self.db.pose = ""
        self.db.pose_default = ""
        
    def get_display_name(self, looker, **kwargs):
        """
        Displays the name of the object in a viewer-aware manner.
        Args:
            looker (TypedObject): The object or account that is looking
                at/getting inforamtion for this object.
        Kwargs:
            pose (bool): Include the pose (if available) in the return.
        Returns:
            name (str): A string containing the name of the object, DBREF for
                        builers and above, and pose if requested.
        """
        dbref = "(#%s)" % self.id if self.access(looker, access_type="control") else ""
        pose = " %s" % (self.db.pose or "") if kwargs.get("pose", False) else ""
        return "%s%s%s" % (self.name, dbref, pose)

    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.
        Args:
            looker (Object): Object doing the looking.
        """
        if not looker:
            return ""
        # get and identify all objects
        visible = (con for con in self.contents if con != looker and con.access(looker, "view"))
        exits, users, things = [], [], []
        for con in visible:
            key = con.get_display_name(looker, pose=True)
            if con.destination:
                exits.append(key)
            elif con.has_account:
                users.append(key)
            else:
                things.append(key)
        # get description, build string
        string = "|c%s|n\n" % self.get_display_name(looker, pose=True)
        desc = self.db.desc
        if desc:
            string += "%s" % desc
        if exits:
            string += "\n|wExits:|n " + ", ".join(exits)
        if users or things:
            string += "\n " + "\n ".join(users + things)
        return string

    def at_after_move(self, source_location, **kwargs):
        """
        Called after move has completed, regardless of quiet mode or
        not.  Allows changes to the object due to the location it is
        now in.
        Args:
            source_location (Object): Wwhere we came from. This may be `None`.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        super().at_object_creation(source_location, **kwargs)
        self.db.pose = self.attributes.get("pose_default", default = "")



class CmdPose(COMMAND_DEFAULT_CLASS):
    """
    Set a static pose
    Usage:
        pose <pose> # Sets pose
        pose/reset #Resets pose
        pose/default <pose> # Set default pose to be reset to
        
        pose obj = <pose> # Pose another object
        pose/reset obj # Reset another objects pose
        pose/default obj = <pose> # Set objects pose to reset to
    Examples:
        pose leans against the tree
        pose is talking to the barkeep.
        pose box = sitting on the floor.
    """

    key = "pose"
    # aliases = [""]
    switch_options = ("default")

    def func(self):
        """
        This is the hook function that actually does all the work. It is called
        by the cmdhandler right after self.parser() finishes, and so has access
        to all the variables defined therein.
        """
        caller = self.caller

        # FIND TARGET FOR COMMAND ---------------------------------------------
        # If there is an = sign, the target is to the left.
        if self.rhs:
            target = self.lhs
        # If there's no = but it's a reset command, the target will be the argument
        elif any(switch in self.switches for switch in ["reset"]):
            target = self.args
        # Otherwise, it's the caller and will be assigned later
        else:
            target = None
        
        # Find target.
        if target:
            target = caller.search(target)
            if not target:
                # caller.search alerts caller of no find.
                return
        else:
            # Didn't need to seach for the caller.
            target = self.caller
        
        # CHECK WE'RE ALLOWED TO POSE THE TARGET -----------------------------
        if not target.access(caller, "edit"):
            caller.msg("You canont pose that.")
            return
        if not target.attributes.has("pose"):
            caller.msg(f"{target.name} cannot be posed.")
            return


        # HANDLE RESET SWITCH ------------------------------------------------
        # pose/reset
        # pose/reset obj
        
        # Reset target/self to default pose
        if any(switch in self.switches for switch in ["reset"]):
            target.db.pose = target.attributes.get("pose_default", default = "")
            caller.msg(f"Pose of {target.name} has been reset to '{target.name} {target.db.pose}'")
            return

        # DETERMINE POSE STRING------------------------------------------------
        pose = self.rhs if self.rhs else self.args

        # Handle no pose given
        if not pose:
            caller.msg("Usage: pose <pose> OR pose obj = <pose>")

        # Add punctuation
        if not pose.endswith("."):
            pose = f"{pose}."
            
        # Length check pose.
        if len(target.name) + len(pose) > 60:
            caller.msg(f"Your pose '{pose}' is too long.")
            return
        
        # HANDLE SETTING DEFAULT POSE STRING-----------------------------------
        # pose/default <pose>
        # pose/default obj = <pose>
        
        # Set new default pose
        if any(switch in self.switches for switch in ["default"]):
            target.db.pose_default = pose
            caller.msg(f"Default pose of {target.name} is now '{target.name} {pose}'.")
            return

        # SET POSE STRING -----------------------------------------------------
        target.db.pose = pose
        caller.msg(f"Pose will read '{target.name} {pose}'.")