# -*- coding: utf-8 -*-
"""
This file contains all the custom functionality of the pre_login splash screen

Connection screen

This is the text to show the user when they first connect to the game (before
they log in).

Commands

Commands that are available from the connect screen.

"""

import re
import datetime
from codecs import lookup as codecs_lookup
from django.conf import settings
from evennia import CmdSet
from evennia.accounts.models import AccountDB
from evennia.accounts.accounts import AccountDB
from evennia.server.models import ServerConfig
from evennia.utils import class_from_module, create, logger, utils, gametime
from evennia.commands.cmdhandler import CMD_LOGINSTART
from evennia.commands.default import unloggedin
from evennia.utils import logger, utils, ansi
from evennia.utils.evmenu import EvMenu


CONNECTION_SCREEN = """
                              __◞ >◞ ◜> 
                           _◞     ╯   ╯◟◞ ◜> 
                          (                 ◜  
                            ◜◝              ╮ 
                               \              ◡) 
                             ◟◞             ◞ ╯ 
                             ◝ ◜◝              ◡ ◜> 
                                 ◡                ╭ ◜ 
                                 \              ◟◞ 
                                  \◞ ╮  ╭◝ ◟ ◞                  
                                    Ɛ>   <3     
                                     /   \ 
                                     \   / 
                                      \ /  
                                       V 

                       F I N A L   F A N T A S Y   V I I I 

                                   NEW GAME 
                                   Continue                                 """

MULTISESSION_MODE = settings.MULTISESSION_MODE
COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)
def clean_node(nodetext, optionstext, caller=None): return nodetext
def clean_options(optionlist, caller=None): return ""


class UnloggedinCmdSet(CmdSet):
    """
    The `CharacterCmdSet` contains additional, unique or altered commands used
    by FF8MUD available at the unloggedin screen. It is included in:
    `commands/default_cmdset.CharacterCmdSet.at_cmdset_creation`
    """
    key = "unloggedincmdset"
    priority = 1

    def at_cmdset_creation(self):
        # Commands for unloggedin screen.
        self.add(CmdUnconnectedContinue())
        self.add(CmdUnconnectedNewGame())
        self.add(CmdUnconnectedQuit())
        self.add(CmdUnconnectedHelp())
        self.add(CmdUnconnectedLook())


class CmdUnconnectedContinue(COMMAND_DEFAULT_CLASS):
    """
    Default connect command.

    Usage (at login screen):
      continue username password
      continue "user name" "pass word"

    Use the 'new game' command to first create an account before logging in.

    If you have spaces in your name, enclose it in quotes.
    """
    key = "continue"
    aliases = ["cont", "con", "c", "connect", "conn"]
    locks = "cmd:all()"  # not really needed
    arg_regex = r"\s.*?|$"

    def func(self):
        """
        Uses the Django admin api. Note that unlogged-in commands
        have a unique position in that their func() receives
        a session object instead of a source_object like all
        other types of logged-in commands (this is because
        there is no object yet before the account has logged in)
        """
        session = self.caller
        address = session.address

        args = self.args
        # extract double quote parts
        parts = [part.strip() for part in re.split(r"\"", args) if part.strip()]
        if len(parts) == 1:
            # this was (hopefully) due to no double quotes being found, or a guest login
            parts = parts[0].split(None, 1)

            # Guest login
            if len(parts) == 1 and parts[0].lower() == "guest":
                # Get Guest typeclass
                Guest = class_from_module(settings.BASE_GUEST_TYPECLASS)

                account, errors = Guest.authenticate(ip=address)
                if account:
                    session.sessionhandler.login(session, account)
                    return
                else:
                    session.msg("|R%s|n" % "\n".join(errors))
                    return

        if len(parts) != 2:
            session.msg("\n\r Usage (without <>): continue <name> <password>")
            return

        # Get account class
        Account = class_from_module(settings.BASE_ACCOUNT_TYPECLASS)

        name, password = parts
        # Next line custom added. Chargen removes characters from initial password.
        # Let's make sure we do the same for logging in.
        password = re.sub(r"\s+", " ", password).strip()
        account, errors = Account.authenticate(
            username=name, password=password, ip=address, session=session
        )
        if account:
            session.sessionhandler.login(session, account)
        else:
            session.msg("|R%s|n" % "\n".join(errors))


class CmdUnconnectedNewGame(COMMAND_DEFAULT_CLASS):
    """
    Create a new player account with the PokeMud meu system.

    Usage (at login screen):
      new game

    This triggers a system of menus which sets up a player/character.

    """
    key = "new game"
    aliases = ["new", "n"]
    locks = "cmd:all()"
    arg_regex = r"\s.*?|$"

    def func(self):
        session = self.caller

        # Initiate Character creation menu
        EvMenu(session, "features.pre_login", startnode="name_node",
               cmdset_mergetype="Replace", cmdset_priority=1,
               node_formatter=clean_node, options_formatter=clean_options,
               cmd_on_exit=CMD_LOGINSTART)

def name_node(caller):
    text = ""
    text += ("Garden Recruiter says: Thank you for your interest! Please "
             "complete the following Application Form...")
    text += """
┌────────────────────────────────────────────────────────────────────────────┐
|       |                                                For office use only |
|   ╭ ╯|||╰ ╮                                             ┌─┬─┬─┬─┬─┬─┬─┬─┬─┐ |
|  /   |||    \                                           └─┴─┴─┴─┴─┴─┴─┴─┴─┘ |
| (    |||╭╮   )   APPLICATION FORM FOR SeeD STUDENT ADMISSION                |
|  \   ╰--/  /                                                               |
|   ╰ . _╭ /      All hard-working and confident youths are welcome.         |
|        ||/       Ambitious overachievers are also welcome.                  |
|        |        Applicants are admitted after passing a final interview.   |
├────────────────────────────────────────────────────────────────────────────┤
|  Section A: Your Personal Details                                          |
├────────────────────────────────────────────────────────────────────────────┤
|  FIRST NAME:                                                               |
"""
    options = {"key": "_default",
               "goto": "password_node"}
    return text, options

def password_node(session, raw_string):
    username = re.sub(r"\s+", " ", raw_string).strip()
    account = class_from_module(settings.BASE_ACCOUNT_TYPECLASS)
    
    # Validate that username meets requirements & unique
    valid, errors = account.validate_username(username)
    if not valid:
        text = "Garden Recruiter says: %s" % "\n".join(errors)
        options = {"key": "_default", "goto": "password_node"}
        return text, options

    # Check IP and/or name bans
    if account.is_banned(ip=session.address, username=username):
        text = "{rYou have been banned and cannot continue from here." \
                 "\nIf you feel this ban is in error, please email an admin.{x"
        session.msg(text)
        session.sessionhandler.disconnect(session, "Good bye! Disconnecting.")
        return
    
    # Save sutiable name for later
    session.ndb._menutree.username = username

    # Present next prompt
    buffer = "                              "
    username = username + buffer[len(username):]
    text = """
┌────────────────────────────────────────────────────────────────────────────┐
|       |                                                For office use only |
|   ╭ ╯|||╰ ╮                                             ┌─┬─┬─┬─┬─┬─┬─┬─┬─┐ |
|  /   |||    \                                           └─┴─┴─┴─┴─┴─┴─┴─┴─┘ |
| (    |||╭╮   )   APPLICATION FORM FOR SeeD STUDENT ADMISSION                |
|  \   ╰--/  /                                                               |
|   ╰ . _╭ /      All hard-working and confident youths are welcome.         |
|        ||/       Ambitious overachievers are also welcome.                  |
|        |        Applicants are admitted after passing a final interview.   |
├────────────────────────────────────────────────────────────────────────────┤
|  Section A: Your Personal Details                                          |
├────────────────────────────────────────────────────────────────────────────┤
|  FIRST NAME: {0} AGE: 18                        |
|  PASSWORD:                                                                 |
""".format(username)
    options = {"key": "_default",
               "goto": "password_confirm_node"}
    return text, options

def password_confirm_node(session, raw_string):
    
    # Validate paswword
    username = session.ndb._menutree.username
    password = re.sub(r"\s+", " ", raw_string).strip()
    account = class_from_module(settings.BASE_ACCOUNT_TYPECLASS)
    
    # Validate that password meets requirements
    valid, errors = account.validate_password(password)
    # if password == username:
    #     valid = False
    #     errors.extend(["The password is too similar to the username."])
    if not valid:
        text = "Garden Recruiter says: %s" % " ".join(errors)
        text += "\n Try Again!"
        options = {"key": "_default", "goto": "password_confirm_node"}
        return text, options

    session.ndb._menutree.password = password

    text = "Garden Recruiter says: Can I confirm your password?"
    options = {"key": "_default",
              "goto": "tutorial_node"}
    return text, options

def tutorial_node(session, raw_string):
    password = re.sub(r"\s+", " ", raw_string).strip()
    if not (password == session.ndb._menutree.password):
        text = "Garden Recruiter says: I don't think that was right. Try again!"
        options = {"key": "_default", "goto": "tutorial_node"}
        return text, options

    buffer = "                              "
    username = session.ndb._menutree.username
    username = username + buffer[len(username):]
    text = """
Garden Recruiter says: Thank you!
┌────────────────────────────────────────────────────────────────────────────┐
|       |                                                For office use only |
|   ╭ ╯|||╰ ╮                                             ┌─┬─┬─┬─┬─┬─┬─┬─┬─┐ |
|  /   |||    \                                           └─┴─┴─┴─┴─┴─┴─┴─┴─┘ |
| (    |||╭╮   )   APPLICATION FORM FOR SeeD STUDENT ADMISSION                |
|  \   ╰--/  /                                                               |
|   ╰ . _╭ /      All hard-working and confident youths are welcome.         |
|        ||/       Ambitious overachievers are also welcome.                  |
|        |        Applicants are admitted after passing a final interview.   |
├────────────────────────────────────────────────────────────────────────────┤
|  Section A: Your Personal Details                                          |
├────────────────────────────────────────────────────────────────────────────┤
|  FIRST NAME: {0} AGE: 18                        |
|  PASSWORD:   *********                                                     |
├────────────────────────────────────────────────────────────────────────────┤
|  Section B: Application Details                                            |
├────────────────────────────────────────────────────────────────────────────┤
|  PREFERRED GARDEN: Balamb Garden                                           |
|  (OPTIONAL) WHY DID YOU CHOOSE TO APPLY:                                   |
|                                                                            |
└────────────────────────────────────────────────────────────────────────────┘
Garden Recruiter says: Would you like to reflect on why you chose to apply? Yes or No? [This will start the tutorial]
""".format(username)
    options = {"key": "_default",
              "goto": "tutorial_start_node"}
    return text, options

def tutorial_start_node(session, raw_string):
    raw_string = re.sub(r"\s+", " ", raw_string).strip().lower()
    yes_options = ["yes", "y"]
    no_options = ["no", "n"]
    
    if raw_string not in yes_options and raw_string not in no_options:
        text = "Garden Recruiter says: Yes or No?"
        options = {"key": "_default", "goto": "tutorial_start_node"}
        return text, options

    # Skip Tutorial - go to Account & Character creation.
    if raw_string in no_options:
        username = session.ndb._menutree.username
        password = session.ndb._menutree.password
        address = session.address
        
        # Create the new account (character created by account.create()).
        account = class_from_module(settings.BASE_ACCOUNT_TYPECLASS)
        account, errors = account.create(username=username, 
                                         password=password, 
                                         ip=address, 
                                         session=session)
        if account:
            # Account successfully created. Initaite Log in.
            text = ("Garden Recruiter says: Thank you! Your application will "
                    "be processed shortly. Please explore the Garden and we "
                    "will call you for your final interview!")
            session.ndb._menutree.cmd_on_exit = lambda caller, menu: caller.execute_cmd("continue " + username + " " + password)
            return text, None

        else:
            # Return error messages.
            text = "|R%s|n" % "\n".join(errors)
            return text, None
        
    # Tutorial
    if raw_string in yes_options:
        text = "TUTORIAL NOT YET COMPLETE"
        options = {"key": "_default", "goto": "tutorial_start_node"}
        return text, options

def end_node(caller):
    text = ""
    return text, None

        
class CmdUnconnectedQuit(COMMAND_DEFAULT_CLASS):
    """
    quit when in unlogged-in state

    Usage:
      quit

    We maintain a different version of the quit command
    here for unconnected accounts for the sake of simplicity. The logged in
    version is a bit more complicated.
    """

    key = "quit"
    aliases = ["q", "qu"]
    locks = "cmd:all()"

    def func(self):
        """Simply close the connection."""
        session = self.caller
        session.sessionhandler.disconnect(session, "Good bye! Disconnecting.")


class CmdUnconnectedLook(COMMAND_DEFAULT_CLASS):
    """
    look when in unlogged-in state

    Usage:
      look

    This is an unconnected version of the look command for simplicity.

    This is called by the server and kicks everything in gear.
    All it does is display the connect screen.
    """

    key = CMD_LOGINSTART
    aliases = ["look", "l"]
    locks = "cmd:all()"

    def func(self):
        """Show the connect screen."""
        self.caller.msg(CONNECTION_SCREEN)


class CmdUnconnectedHelp(COMMAND_DEFAULT_CLASS):
    """
    get help when in unconnected-in state

    Usage:
      help

    This is an unconnected version of the help command,
    for simplicity. It shows a pane of info.
    """
    key = "help"
    aliases = ["h", "?"]
    locks = "cmd:all()"

    def func(self):
        """Shows help"""

        string = """
You are not yet logged into the game. Commands available at this point:

  |wcreate|n - create a new account
  |wconnect|n - connect with an existing account
  |wlook|n - re-show the connection screen
  |whelp|n - show this help
  |wencoding|n - change the text encoding to match your client
  |wscreenreader|n - make the server more suitable for use with screen readers
  |wquit|n - abort the connection

First create an account e.g. with |wcreate Anna c67jHL8p|n
Next you can connect to the game: |wconnect Anna c67jHL8p|n

You can use the |wlook|n command if you want to see the connect screen again.
"""
        self.caller.msg(string)
