#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("MartinPythonBot")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

ship_states = {}

""" <<<Game Loop>>> """

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    directions_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]
    position_choices = []  # actual coordinates

    for ship in me.get_ships():
        if ship.id not in ship_states:
            ship_states[ship.id] = "collecting"

        position_options = ship.position.get_surrounding_cardinals() + [ship.position]

        # {(0,1): (19: 38)}
        position_dictionary = {}

        # {(0,1): 543}
        halite_dictionary = {}

        logging.info(position_options)

        for n, direction in enumerate(directions_order):
            position_dictionary[direction] = position_options[n]

        for direction in position_dictionary:
            position = position_dictionary[direction]
            halite_amount = game_map[position].halite_amount
            logging.info(position_choices)
            if position_dictionary[direction] not in position_choices:
                halite_dictionary[direction] = halite_amount
            else:
                logging.info("Attempting to move into occupied position " + str(position_dictionary[direction]))

        if ship_states[ship.id] == "depositing":
            move = game_map.naive_navigate(ship, me.shipyard.position)
            position_choices.append(position_dictionary[move])
            command_queue.append(ship.move(move))
            if move == Direction.Still:
                ship_states[ship.id] = "collecting"
        elif ship_states[ship.id] == "collecting":
            directional_choice = max(halite_dictionary, key=halite_dictionary.get)
            logging.info("appending " + str(position_dictionary[directional_choice]))
            position_choices.append(position_dictionary[directional_choice])  # Where is the current ship heading?
            command_queue.append(ship.move(directional_choice))

            if ship.halite_amount > constants.MAX_HALITE / 3:
                ship_states[ship.id] = "depositing"

    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
