r"""
Evennia settings file.

The available options are found in the default settings file found
here:

/home/ec2-user/environment/evennia/evennia/settings_default.py

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "ff8"

######################################################################
# Evennia pluggable modules
######################################################################

# The module holding text strings for the connection screen.
# This module should contain one or more variables
# with strings defining the look of the screen.
CONNECTION_SCREEN_MODULE = "features.pre_login"

######################################################################
# Typeclasses and other paths
######################################################################

# Typeclass for account objects (linked to a character) (fallback)
BASE_ACCOUNT_TYPECLASS = "typeclasses.default_typeclasses.Account"
# Typeclass and base for all objects (fallback)
BASE_OBJECT_TYPECLASS = "typeclasses.default_typeclasses.Object"
# Typeclass for character objects linked to an account (fallback)
BASE_CHARACTER_TYPECLASS = "typeclasses.default_typeclasses.Character"
# Typeclass for rooms (fallback)
BASE_ROOM_TYPECLASS = "typeclasses.default_typeclasses.Room"
# Typeclass for Exit objects (fallback).
BASE_EXIT_TYPECLASS = "typeclasses.default_typeclasses.Exit"
# Typeclass for Channel (fallback).
BASE_CHANNEL_TYPECLASS = "typeclasses.default_typeclasses.Channel"
# Typeclass for Scripts (fallback). You usually don't need to change this
# but create custom variations of scripts on a per-case basis instead.
BASE_SCRIPT_TYPECLASS = "typeclasses.default_typeclasses.Script"

######################################################################
# Default command sets and commands
######################################################################

# Command set used on session before account has logged in
CMDSET_UNLOGGEDIN = "features.pre_login.UnloggedinCmdSet"
# (Note that changing these three following cmdset paths will only affect NEW
# created characters/objects, not those already in play. So if you want to
# change this and have it apply to every object, it's recommended you do it
# before having created a lot of objects (or simply reset the database after
# the change for simplicity)).
# Command set used on the logged-in session
CMDSET_SESSION = "commands.default_cmdsets.SessionCmdSet"
# Default set for logged in account with characters (fallback)
CMDSET_CHARACTER = "commands.default_cmdsets.CharacterCmdSet"
# Command set for accounts without a character (ooc)
CMDSET_ACCOUNT = "commands.default_cmdsets.AccountCmdSet"

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
