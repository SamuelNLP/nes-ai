"""
Super Mario session
"""

import logging
import random
from datetime import datetime

from neats.genetic import Genetic, NetworkShape
from neats.network import Network
from nes_py.wrappers import JoypadSpace

from nes_ai.input import MOVEMENT, Button, Joypad, neat_result_to_buttons
from nes_ai.mario.env import SuperMario

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# constants
BUTTONS_MAP = {
    0: Button.LEFT,
    1: Button.RIGHT,
    2: Button.A,
    3: Button.B,
    4: Button.DOWN,
    5: Button.NONE,
}

THRESHOLD_FRAME = 5
TIMEOUT = 100
BUTTON_THRESHOLD = 0.5
INITIAL_THRESHOLD = 100

RENDER = False

# neats constants
NUMBER_INDIVIDUALS = 10

NETWORK_INPUTS = 169
NETWORK_OUTPUTS = 6


@profile  # noqa
def individual_run(individual: Network) -> Network:
    """
    An individual run
    """
    random.seed(datetime.now())
    mario = SuperMario()
    player = Joypad(JoypadSpace(mario, MOVEMENT))

    while mario.ram[0x0009] < INITIAL_THRESHOLD:
        player.press((Button.START,), delay=INITIAL_THRESHOLD)

    frame_count = 0
    fitness = 0
    timeout_ = TIMEOUT
    rightmost_mario = 0

    while True:
        if RENDER:
            mario.render()

        if mario.is_dying or (timeout_ < 0 and frame_count > TIMEOUT):
            individual.fitness = fitness

            mario.close()
            return individual

        # play
        features = mario.get_input_array()
        instances = individual.evaluate(features)
        button_result = neat_result_to_buttons(
            instances, BUTTONS_MAP, BUTTON_THRESHOLD  # noqa
        )

        x_mario, _ = mario.get_mario()

        if x_mario > rightmost_mario:
            timeout_ = TIMEOUT
            rightmost_mario = x_mario

        if button_result:
            player.press(button_result, delay=THRESHOLD_FRAME, replay=True)
        else:
            player.press((Button.NONE,), delay=0)

        # fitness
        fitness = int(x_mario - frame_count / 4)
        frame_count += 1
        timeout_ -= 1


@profile  # noqa
def main():
    network_shape = NetworkShape(n_inputs=NETWORK_INPUTS, n_outputs=NETWORK_OUTPUTS)
    genetic = Genetic(
        number_individuals=NUMBER_INDIVIDUALS, network_shape=network_shape
    )

    for index in range(1):
        population = [individual_run(x) for x in genetic.population]
        genetic.population = population

        logger.info("#----------#")
        logger.info(f"Iteration: {index}")
        logger.info("#----------#\n")

        genetic = genetic.evolve()


if __name__ == "__main__":
    main()
