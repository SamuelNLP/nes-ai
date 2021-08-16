"""
A NEAT run on Tetris using openai api in parallel
"""

import logging
import os
import pickle
import random
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from neats.genetic import Genetic, NetworkShape
from neats.mutation import Mutation
from neats.network import Network
from nes_py.wrappers import JoypadSpace

from nes_ai.input import MOVEMENT, Button, Joypad
from nes_ai.tetris.env import Tetris
from nes_ai.tetris.info import GamePhase

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# constants
BUTTONS_MAP = {0: Button.LEFT, 1: Button.RIGHT, 2: Button.A, 3: Button.DOWN}

RUNS_PER_INDIVIDUAL = 3
ITERATIONS = 100
NUMBER_INDIVIDUALS = 100

NETWORK_INPUTS = 74
NETWORK_OUTPUTS = 4

mutation_probability = {
    Mutation.LINK: 0.30,
    Mutation.NODE: 0.20,
    Mutation.BOOL: 0.05,
    Mutation.SHIFT_WEIGHT: 0.40,
    Mutation.RANDOM_WEIGHT: 0.05,
}


def not_in_play(tetris: Tetris, player: Joypad):
    """
    Deals with the game when not in play
    """
    if tetris.game_phase not in (GamePhase.PLAY, GamePhase.LEVEL_AND_HEIGHT):
        player.press((Button.START,), delay=5)
    elif tetris.game_phase == GamePhase.LEVEL_AND_HEIGHT:
        player.press((Button.DOWN,), delay=5)
        player.press((Button.RIGHT,), delay=5)
        player.press((Button.RIGHT,), delay=5)
        player.press((Button.RIGHT,), delay=5)
        player.press((Button.RIGHT,), delay=5)
        player.press((Button.START,), delay=5)


def tetris_run(individual: Network, tetris: Tetris, player: Joypad):
    """
    A tetris run
    """
    while True:
        tetris.render()

        if tetris.game_phase != GamePhase.PLAY:
            # deal with non play
            not_in_play(tetris, player)
            continue

        if not tetris.piece or not tetris.next_piece:
            continue

        if tetris.field.is_full:
            if tetris.stats.lines > 0:
                print(
                    f"fitness: {individual.fitness} -> "
                    f"score: {tetris.stats.score}, "
                    f"pieces: {tetris.stats.pieces}, "
                    f"lines: {tetris.stats.lines}"
                )

            # fitness
            return tetris.stats.pieces * 100 + tetris.stats.score * 6

        # play
        # features: holes and heights
        features = tetris.field.features(tetris.piece, tetris.next_piece)

        if features:
            button_result = BUTTONS_MAP[int(np.argmax(individual.evaluate(features)))]

            # print(input_, "-> ", button_result)
            player.press((button_result,))
        else:
            player.press((Button.NONE,))


def individual_run(individual: Network):
    """
    An individual run
    """
    random.seed(datetime.now())
    tetris = Tetris()
    player = Joypad(JoypadSpace(tetris, MOVEMENT))

    fitness = []

    for _ in range(RUNS_PER_INDIVIDUAL):
        fitness.append(tetris_run(individual, tetris, player))

        tetris.reset()
        player.press((Button.NONE,))

    individual.fitness = sum(fitness) / len(fitness)
    tetris.close()

    return individual


if __name__ == "__main__":
    # prepare folder to store results
    run = f"openai_itr={ITERATIONS}_ind={NUMBER_INDIVIDUALS}"
    date_ = str(datetime.now().replace(microsecond=0)).replace(" ", "_")
    folder = Path.cwd() / "runs" / f"{run}_{date_}"
    folder.mkdir(parents=True, exist_ok=True)

    network_shape = NetworkShape(n_inputs=NETWORK_INPUTS, n_outputs=NETWORK_OUTPUTS)

    # initialize genetic
    genetic = Genetic(
        number_individuals=NUMBER_INDIVIDUALS,
        network_shape=network_shape,
        mutation_probability=mutation_probability,
    )

    average_fitness_list = list()
    max_fitness_list = list()

    for index in range(ITERATIONS):
        population = genetic.population

        with Pool(os.cpu_count()) as pool:
            population = pool.map(individual_run, population)

        max_fitness = max(population).fitness
        max_fitness_list.append(max_fitness)

        average_fitness = np.mean([network.fitness for network in population])
        average_fitness_list.append(average_fitness)

        genetic.population = population

        with open(str(folder / f"iteration={index}.pickle"), "wb") as handle:
            pickle.dump(genetic, handle, protocol=pickle.HIGHEST_PROTOCOL)

        logger.info("#----------#")
        logger.info(f"Iteration: {index}")
        logger.info(f"max fitness: {max_fitness}")
        logger.info(f"average fitness: {average_fitness}")
        logger.info(f"species: {len(genetic.species)}")
        logger.info("#----------#\n")

        genetic = genetic.evolve()

    best_individual = max(genetic.population)
    best_individual.draw()

    plt.figure()
    plt.plot(average_fitness_list)
    plt.plot(max_fitness_list)

    plt.show()

    with open(str(folder / "best_tetris.pickle"), "wb") as handle:
        pickle.dump(best_individual, handle, protocol=pickle.HIGHEST_PROTOCOL)
