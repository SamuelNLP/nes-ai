"""
Super Mario session
"""

import logging
import os
import pickle
import random
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from neats.genetic import Genetic, NetworkShape
from neats.genome import Activation
from neats.mutation import Mutation
from neats.network import Network
from neats.selection import TournamentSelection
from neats.session import Session
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
}

THRESHOLD_FRAME = 5
TIMEOUT = 100
BUTTON_THRESHOLD = 0
INITIAL_THRESHOLD = 100

RENDER = True

# neats constants
ITERATIONS = 1000
NUMBER_INDIVIDUALS = 300

NETWORK_INPUTS = 169
NETWORK_OUTPUTS = 5

MUTATION_PROBABILITY = {
    Mutation.LINK: 0.05,
    Mutation.NODE: 0.03,
    Mutation.BOOL: 0.30,
    Mutation.SHIFT_WEIGHT: 0.90,
    Mutation.RANDOM_WEIGHT: 0.05,
}

DISJOINT = 0.5
WEIGHT = 0.3

STAGNATION = 15

# change these 2 to improve an existing session
run = None
iteration = None


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
        button_result = neat_result_to_buttons(
            individual.evaluate(features), BUTTONS_MAP, BUTTON_THRESHOLD  # noqa
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


if __name__ == "__main__":
    if run and iteration:
        folder = Path.cwd() / "runs" / run  # noqa
        folder.mkdir(parents=True, exist_ok=True)
        older_run = folder / iteration

        with older_run.open("rb") as handle:
            genetic = pickle.load(handle)

        genetic = genetic.with_properties(mutation_probability=MUTATION_PROBABILITY)
    else:
        date_ = str(datetime.now().replace(microsecond=0)).replace(" ", "_")
        run = f"mario_n={NUMBER_INDIVIDUALS}_{date_}"

        network_shape = NetworkShape(n_inputs=NETWORK_INPUTS, n_outputs=NETWORK_OUTPUTS)
        genetic = Genetic(
            number_individuals=NUMBER_INDIVIDUALS,
            network_shape=network_shape,
            mutation_probability=MUTATION_PROBABILITY,
            stagnation=STAGNATION,
            output_activation=Activation.H_TAN,
            selection=TournamentSelection(k_choice=3),
        )

        folder = Path.cwd() / "runs" / run
        folder.mkdir(parents=True, exist_ok=True)

    session = Session(
        individual_run=individual_run,
        genetic=genetic,
        folder=folder,
        parallel_num=os.cpu_count() - 1,
    )

    average_fitness, max_fitness = session.start(
        iterations=ITERATIONS,
        evolve_properties={"disjoint": DISJOINT, "weight": WEIGHT},
    )

    best_individual = max(session.genetic.population)
    best_individual.draw()

    plt.figure()
    plt.plot(average_fitness)
    plt.plot(max_fitness)

    plt.show()

    with open(str(folder / "best_mario.pickle"), "wb") as handle:
        pickle.dump(best_individual, handle, protocol=pickle.HIGHEST_PROTOCOL)
