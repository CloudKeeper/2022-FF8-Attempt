"""

Add Game Rules:
Open	Enables the player to see which cards the opponent is using.
Same	When a card is placed touching two or more other cards (one or both of 
        them have to be the opposite color), and the touching sides of each 
        card is the same (8 touching 8 for example), then the other two cards 
        are flipped. Combo rule applies.
Same Wall	An extension of the Same rule. The edges of the board are counted 
        as A ranks for the purposes of the Same rule. Combo rule applies. If 
        the Same rule is not present in a region that has Same Wall, Same Wall
        will not appear in the list of rules when starting a game because it 
        can have no effect without Same but it will be carried with the player 
        to other regions, and can therefore still be spread.
Sudden Death	If the game ends in a draw, a sudden death occurs in which a 
        new game is started but the cards are distributed on the side of the 
        color they were on at the end of the game.
Random	Five cards are randomly chosen from the player's deck instead of the 
        player being able to choose five cards themselves.
Plus	Similar to the Same rule. When one card is placed touching two others 
        and the ranks touching the cards plus the opposing rank equal the same 
        sum, then both cards are captured. Combo rule applies.
Combo	Of the cards captured by the Same, Same Wall or Plus rule, if they are 
        adjacent to another card whose rank is lower, it is captured as well. 
        This is not a separate rule; any time Same or Plus is in effect, Combo 
        is in effect as well.
Elemental	In the elemental rule, one or more of the spaces are randomly 
        marked with an element. Some cards have elements in the upper-right 
        corner. Ruby Dragon, for example, is fire-elemental, and Quezacotl is 
        thunder-elemental. When an elemental card is placed on a corresponding 
        element, each rank goes up a point. When any card is placed on a 
        non-matching element, each rank goes down a point. This does not affect 
        the Same, Plus and Same Wall rules, where the cards' original ranks 
        apply.

Add Winning Rules:
One	1	Winner chooses one card from loser.
Difference (Diff)	2	Winner chooses one card per score difference (2, 4, or 5).
Direct	3	Players take cards that are their color at the end of the game.
All	4	Winner takes all.

"""
import random
import itertools
from django.conf import settings
from evennia import create_script
from evennia import CmdSet
from evennia.utils.utils import class_from_module
from evennia.utils import evform
from typeclasses.default_typeclasses import Character, Script

COMMAND_DEFAULT_CLASS = class_from_module(settings.COMMAND_DEFAULT_CLASS)


##############################################################################
#
# Triple Triad Card List
#
##############################################################################

##############################################################################
#
# Triple Triad Card Mixin and Handler
#
##############################################################################

##############################################################################
#
# Triple Triad Command
#
##############################################################################

class CmdTripleTriad(COMMAND_DEFAULT_CLASS):
    """
    
    """
    key = "tripletriad"
    aliases = ["tt"]
    help_category = "General"
    rhs_split = ("=", "to") # Prefer = delimiter, but allow " to " usage.

    def func(self):
        caller = self.caller
        participants = [caller]
        
        # ---------------------------------------------------------------------
        # OUT OF GAME COMMANDS
        # ---------------------------------------------------------------------
        
        # ---------------------------------------------------------------------
        # Initiate Triple Triad game command.
        # Assumed Input: tt <target>
        # ---------------------------------------------------------------------
        
        # If caller is not already in a game, assume invitation to start game.
        if not caller.ndb.game_handler:
            
            # If no arguments, inform Caller they need a target.
            if not self.args:
                    caller.msg("Play with whom?")
                    return
            
            participant = caller.search(self.args)
        
            # If Participant could not be located, inform Caller.
            if not participant:
                caller.msg(self.args + " could not be located.")
                return
            
            # If Particpant isn't a character, inform Caller.
            if not isinstance(participant, Character):
                caller.msg(self.args + " is not able to play a game.")
                return
            
            # If Participant is already playing a game, inform Caller.
            if participant.ndb.game_handler:
                caller.msg(self.args + " is already playing a game.")
                return
            
            # If Participant is themselves, inform Caller.
            if participant in participants:
                caller.msg("You cannot play by yourself.")
                return
    
            participants.append(participant)
            
            # TODO: COLLECT CARDS? THIS IS A MOCK SET UP
            def rand_card():
                """ 
                """
                temp_card = {"name": "Geezard", "element": None, "type": "Monster"}
                temp_card["up"] = random.randrange(1, 10)
                temp_card["right"] = random.randrange(1, 10)
                temp_card["down"] = random.randrange(1, 10)
                temp_card["left"] = random.randrange(1, 10)
                return temp_card

            participants = {participant:[rand_card(),rand_card(),rand_card(),rand_card(),rand_card()] for participant in participants}
            
            # Create list and initialise the game.
            handler = create_script(TripleTriadHandler)
            handler.initialise_game_information(participants, "game")
            return

        # ---------------------------------------------------------------------
        # IN-GAME COMMANDS
        # ---------------------------------------------------------------------
        game = caller.ndb.game_handler        

        # ---------------------------------------------------------------------
        # Forfeit game command
        # Assumed Input: tt forfeit
        # ---------------------------------------------------------------------

        if self.args in ("forfeit", "give up", "concede", "quit"):
            game.forfeit(caller)
            return
            
        # ---------------------------------------------------------------------
        # Take Turn command
        # Assumed Input: tt 2 to A3
        # ---------------------------------------------------------------------

        # Only Current Player can take turn. If not current Player, inform Caller.
        current_player = game.current_player()
        if not caller == current_player:
            caller.msg("It is not your turn. Please wait for your Opponent.")
            return
        
        # CHECK TARGET CARD
        target_card = self.lhs
        current_hand = game.db.participants[current_player]
        
        # If target card is not numeral 1-5, inform Caller.
        if not target_card in ("1", "2", "3", "4", "5"):
            caller.msg(target_card + " is not a valid card in your hand. Usage: 'tt [card in hand - 1 to 5] to [board position - A1 to C3]'")
            return
        
        target_card = int(target_card) - 1
        
        # If target card is no longer in hand, inform Caller.
        if not current_hand[target_card]:
            caller.msg("Target card " + str(target_card) + " is not in your hand. Pick another.")
            return
        
        # Target Card should be valid.
    
        # CHECK BOARD POSITION
        target_position = self.rhs.lower()
        gameboard = game.db.gameboard
        
        # If target position not a board position, inform Caller.
        if not target_position in ("a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2", "c3"):
            caller.msg(target_position + " is not a valid board position. Usage: 'tt [card in hand - 1 to 5] to [board position - A1 to C3]'")
            return
        
        # If target position is occupied, inform Caller.
        if gameboard[target_position][0]:
            caller.msg("Target position " + str(target_card) + " is already occupied. Pick another.")
            return

        # target position should be valid

        # LODGE ACTION
        game.current_player_action(target_card, target_position)

##############################################################################
#
# Triple Triad Script
#
##############################################################################


class TripleTriadHandler(Script):
    """This implements the game handler."""

    #########################################################################
    # Create Game
    #########################################################################
    
    def at_script_creation(self):
        """
        Initialises Game Handler and idles waiting for Game to be Initialised.
        
        self.db.phase [str] - Used to determine what phase to initialise 
                              the game for: invitation / game.
        
        self.db.gameboard [dict of lists] - Keeps track of cards on gameboard. 
                Will be used like:
                gameboard = {
                    "A1": [card, player1],
                    "A2": [card, player2],
                    ...
        
        self.db.particpants [dict of lists] - Keeps track of players and 
                their current hands. Will be used like:
                participants = {player1: [card, None, card, card, card],
                                player2: [card, card, None, None, card]}
                            
        self.db.turn_order [list] - Keeps track of turn order. 
                Will be used like:
                turn_order = [player1, player2]
        """
        # Script attributes.
        self.key = "game_handler_%i" % random.randint(1, 1000)
        self.desc = "handles games"
        self.interval = 60 * 2  # two minute timeout
        self.start_delay = True # Started with initialise_game_information()
        
        # Game attributes
        self.db.phase = None
        self.db.gameboard = {
            "a1": [None, None],
            "a2": [None, None],
            "a3": [None, None],
            "b1": [None, None],
            "b2": [None, None],
            "b3": [None, None],
            "c1": [None, None],
            "c2": [None, None],
            "c3": [None, None]}
        self.db.participants = {}
        self.db.turn_order = []

    #########################################################################
    # Begin Game Lifecycle
    #########################################################################

    def initialise_game_information(self, participants, phase):
        """
        Triggered by external code to initialise game values before the game 
        starts. Then starts the game!
        """
        self.db.phase = phase
        self.db.participants = participants
        # Randomise first turn order
        turn_order = list(participants.keys())
        random.shuffle(turn_order)
        self.db.turn_order = turn_order

        self.at_start()
    
    def at_start(self):
        """
        This method is called: 
            1. When script first starts, 
            2. After Evennia reloads, 
            3. At the start of each new turn.
        It is assumed the script is stocked with the correct information.
        """
        # Set up the phase.
        if self.db.phase == "game" and self.db.participants:
            for participant in self.db.participants:
                # self.initiate_new_turn(participant)
                # TEST
                participant.ndb.game_handler = self
                participant.msg(self.display_gameboard(participant))
                # End Test
        
            # If AIs turn, trigger AI.
            if not self.current_player().has_account:
                self.random_ai_action()

    #########################################################################
    # Game Phase
    #########################################################################

    #########################
    # Iniatiate new Game Turn
    #########################

    # def initiate_new_turn(self, participant):
    #     """
    #     Run for each participant.
    #     Both players are presented the board. The player with the 'turn' is
    #     prompted and the game waits for their reponse.
    #     """
    #     participant.ndb.game_handler = self
    #     participant.msg(self.display_gameboard(participant))

    #########################
    # General Player Actions - available at any time
    #########################

    def forfeit(self, caller):
        """
        Called by a player making an action via the Triple Triad Command.
        Forfeits the match.
        """
        self.msg_all(caller.key + " has forfeitted the game")
        self.stop()

    #########################
    # Current Player Action
    #########################

    def current_player_action(self, card_position, board_position):
        """
        Called by a player making an action via the Triple Triad Command.
        Checks should already by made. We should assume the move is legal.
        """
        current_player = self.current_player()
        current_hand = self.db.participants[current_player]
        played_card = current_hand[card_position]
        gameboard = self.db.gameboard
        
        # Make the game data changes
        gameboard[board_position][0] = played_card
        gameboard[board_position][1] = current_player
        current_hand[card_position] = None
        
        # Calculate Consequences
        board_position_relationships = {
            "a1": {"a2": ["down", "up"], "b1": ["right", "left"]},
            "a2": {"a1": ["up", "down"], "a3": ["down", "up"], "b2": ["right", "left"]},
            "a3": {"a2": ["up", "down"], "b3": ["right", "left"]},
            "b1": {"b2": ["down", "up"], "a1": ["left", "right"], "c1": ["right", "left"]},
            "b2": {"b1": ["up", "down"], "b3": ["down", "up"], "a2": ["left", "right"], "c2": ["right", "left"]},
            "b3": {"b2": ["up", "down"], "a3": ["left", "right"], "c3": ["right", "left"]},
            "c1": {"c2": ["down", "up"], "b1": ["left", "right"]},
            "c2": {"c1": ["up", "down"], "c3": ["down", "up"], "b2": ["left", "right"]},
            "c3": {"c2": ["up", "down"], "b3": ["left", "right"]}}
        
        for position in board_position_relationships[board_position]:
            relationship = board_position_relationships[board_position][position]
            adjacent_card = gameboard[position][0]
            if adjacent_card and played_card[relationship[0]] > adjacent_card[relationship[1]]:
                gameboard[position][1] = current_player
            
        # End Turn
        self.ndb.turn_complete = True
        self.db.phase = "game"
        self.force_repeat()

    def random_ai_action(self):
        """
        Called by an AI making an action via the Triple Triad Command.
        Checks should already by made. We should assume the move is legal.
        """
        current_player = self.current_player()
        current_hand = self.db.participants[current_player]
        gameboard = self.db.gameboard
        
        # Randomly select a card from available card positions
        available_cards = [position for position in range(5) if current_hand[position] is not None]
        card_position = random.choice(available_cards)
        played_card = current_hand[card_position]
        
        # Randomly select a board position from available board positions
        available_positions = [position for position in gameboard.keys() if gameboard[position][0] is None]
        board_position = random.choice(available_positions)
        
        # Make the game data changes
        gameboard[board_position][0] = played_card
        gameboard[board_position][1] = current_player
        current_hand[card_position] = None
        
        # Calculate Consequences
        board_position_relationships = {
            "a1": {"a2": ["down", "up"], "b1": ["right", "left"]},
            "a2": {"a1": ["up", "down"], "a3": ["down", "up"], "b2": ["right", "left"]},
            "a3": {"a2": ["up", "down"], "b3": ["right", "left"]},
            "b1": {"b2": ["down", "up"], "a1": ["left", "right"], "c1": ["right", "left"]},
            "b2": {"b1": ["up", "down"], "b3": ["down", "up"], "a2": ["left", "right"], "c2": ["right", "left"]},
            "b3": {"b2": ["up", "down"], "a3": ["left", "right"], "c3": ["right", "left"]},
            "c1": {"c2": ["down", "up"], "b1": ["left", "right"]},
            "c2": {"c1": ["up", "down"], "c3": ["down", "up"], "b2": ["left", "right"]},
            "c3": {"c2": ["up", "down"], "b3": ["left", "right"]}}
        
        for position in board_position_relationships[board_position]:
            relationship = board_position_relationships[board_position][position]
            adjacent_card = gameboard[position][0]
            if adjacent_card and played_card[relationship[0]] > adjacent_card[relationship[1]]:
                gameboard[position][1] = current_player
        
        # End Turn
        self.ndb.turn_complete = True
        self.db.phase = "game"
        # Bypass force_repeat() because it doesn't like it being run during the
        # first at_start() run and the ai's move is a fraction of a second any
        # way so it doesn't matter that the turn timing is used for the next turn.
        self.at_repeat()

    #########################
    # Initiate end of Turn
    #########################

    def at_repeat(self):
        """
        This is called every self.interval seconds (turn timeout) or
        when force_repeat is called (when a player enters a command). We know 
        this by checking the existence of the `invitation_turn` or 
        `action_turn` NAttribute, set just before calling force_repeat.
        """
        if self.ndb.turn_complete:
            # Check win condition.
            self.action_resolution()
            
            # Set up turn order for next turn.
            order = self.db.turn_order
            order[0], order[1] = order[1], order[0]
            
            # Set up players for next turn.
            del self.ndb.turn_complete
            self.at_start()
            
        else:
            # turn timeout
            self.msg_all("Game has ended due to inaction.")
            self.stop()

    #########################
    # Check End of Game
    #########################

    def action_resolution(self):
        """
        Decides who the winner is.
        """
        gameboard = self.db.gameboard
        
        # Game ends when all gameboard positions are filled.
        if not [position for position in gameboard.keys() if gameboard[position][0] is None]:
            for participant in self.db.participants:
                participant.msg(self.display_gameboard(participant, title="GAME OVER"))
                if self.calculate_score(participant) > 5:
                    self.msg_all(participant.key + " has won the match.")
                if self.calculate_score(participant) == 5:
                    self.msg_all("The match was a tie.")
            self.stop()

    #########################
    # Finish Script
    #########################

    def at_stop(self):
        """
        Called just before the script is stopped/destroyed.
        
        Conducts cleanup on each player connected to handler.
        """
        for participant in self.db.participants:
            del participant.ndb.game_handler

    #########################
    # Utility Methods
    #########################

    def display_gameboard(self, participant, title = None):
        
        # Set Gameboard Appearance
        form = {"FORM": """
Your Cards                        xxxxKxxxx                        Their Cards
  xxxxx                       A       B       C                       xxxxx
1 xxAxx       Score       ┌───────┬───────┬───────┐       Score       xxFxx 6
  xxxxx         xUx       │*xxxxx │*xxxxx │*xxxxx │         xVx       xxxxx
    xxxxx               1 │ xxLxx │ xxMxx │ xxNxx │                 xxxxx
  2 xxBxx                 │ xxxxx │ xxxxx │ xxxxx │                 xxGxx 7
    xxxxx                 ├───────┼───────┼───────┤                 xxxxx
      xxxxx               │*xxxxx │*xxxxx │*xxxxx │               xxxxx
    3 xxCxx             2 │ xxOxx │ xxPxx │ xxQxx │               xxHxx 8 
      xxxxx               │ xxxxx │ xxxxx │ xxxxx │               xxxxx
        xxxxx             ├───────┼───────┼───────┤             xxxxx
      4 xxDxx             │*xxxxx │*xxxxx │*xxxxx │             xxIxx 9
        xxxxx           3 │ xxRxx │ xxSxx │ xxTxx │             xxxxx 
          xxxxx           │ xxxxx │ xxxxx │ xxxxx │           xxxxx 
        5 xxExx           └───────┴───────┴───────┘           xxJxx 10 
          xxxxx                                               xxxxx
"""}
        
        # Set Card Appearance
        def return_card_string(card):
            """ Turn {"name": "Geezard", "up": 5, "right": 5, "down": 5...}
                Into:
                      ┌ 1 ┐
                      |1 1|
                      └ 1 ┘
            """
            line1 = "┌ {} ┐".format(card["up"])
            line2 = "|{}{}{}|".format(card["left"], card["element"] if card["element"] else " ", card["right"])
            line3 = "└ {} ┘".format(card["down"])
            return line1 + "\n" + line2 + "\n" + line3
        
        # Set Information to be displayed on Gameboard
        cells = {}
        participants = self.db.participants
        turn_order = list(self.db.turn_order)
        gameboard = self.db.gameboard
        player = participant
        opponent = list(turn_order)
        opponent.remove(player)
        opponent = opponent[0]
        
        # Prepare Player's Hand
        keys = list("ABCDE")
        for card in participants[player]:
            if card:
                cells[keys.pop(0)] = return_card_string(card)
            else:
                # Handle blank space
                cells[keys.pop(0)] = " "*5 + "\n" + " "*5 + "\n" + " "*5
        
        # Prepare Opponent's Hand
        keys = list("FGHIJ")
        for card in participants[opponent]:
            if card:
                cells[keys.pop(0)] = return_card_string(card)
            else:
                # Handle blank space
                cells[keys.pop(0)] = " "*5 + "\n" + " "*5 + "\n" + " "*5
        
        # Prepare Turn Indicator
        if not title:
            if player == turn_order[0]:
                cells["K"] = "YOUR TURN"
            else:
                cells["K"] = "OPPS TURN"
        else:
            cells["K"] = title
        
        # Prepare GameBoard
        keys = list("LMNOPQRST")
        positions = ["a1", "b1", "c1", "a2", "b2", "c2", "a3", "b3", "c3"]
        for position in positions:
            if gameboard[position][0]:
                cells[keys.pop(0)] = return_card_string(gameboard[position][0])
            else:
                # Handle blank space
                cells[keys.pop(0)] = " "*5 + "\n" + " "*5 + "\n" + " "*5
        
        # Prepare Score
        cells["U"] = self.calculate_score(player)
        cells["V"] = self.calculate_score(opponent)
        
        form = str(evform.EvForm(form=form, cells=cells))
        
        # Switch out the card ownership symbols * with < or >
        positions = ["a1", "b1", "c1", "a2", "b2", "c2", "a3", "b3", "c3"]
        for position in positions:
            if gameboard[position][1]:
                if gameboard[position][1] == player:
                    form = form.replace("*", "<", 1)
                else:
                    form = form.replace("*", ">", 1)
            else:
                form = form.replace("*", " ", 1)
        return form

    def current_player(self):
        """
        Called just before the script is stopped/destroyed.
        Conducts cleanup on each trainer connected to handler.
        """
        return self.db.turn_order[0]

    def calculate_score(self, participant):
        """
        Called just before the script is stopped/destroyed.
        Conducts cleanup on each trainer connected to handler.
        """
        score = 0
        gameboard = self.db.gameboard
        current_hand = self.db.participants[participant]
        for card in current_hand:
            if card:
                score+= 1
        for position in gameboard:
            if gameboard[position][1] == participant:
                score+= 1
        return score

    def msg_all(self, message, exceptions=()):
        """
        Send message to all participants
        """
        for participant in self.db.participants:
            if participant not in exceptions:
                participant.msg(message)
