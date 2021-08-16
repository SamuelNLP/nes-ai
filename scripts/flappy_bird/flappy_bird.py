"""
A NEAT run on flappy bird
"""

import logging
import pickle
import random
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from neats.genetic import Genetic, NetworkShape
from neats.mutation import Mutation, MutationType
from neats.selection import TopPercentageSelection
from ple import PLE
from ple.games.flappybird import FlappyBird

logger = logging.getLogger()

logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

RUNS_PER_INDIVIDUAL = 1
NUMBER_INDIVIDUALS = 500
REDIRECTION_TRIES = 100

NETWORK_INPUTS = 8
NETWORK_OUTPUTS = 1

WIDTH, HEIGHT = 288, 512
MAX_FITNESS = 50_000

MUTATION_PROBABILITY = {
    Mutation.LINK: 0.01,
    Mutation.NODE: 0.10,
    Mutation.BOOL: 0.05,
    Mutation.SHIFT_WEIGHT: 0.70,
    Mutation.RANDOM_WEIGHT: 0.02,
}

display = False
best_individual = None
redirect_search_rounds = 0

date_ = str(datetime.now().replace(microsecond=0)).replace(" ", "_")
run = f"flappy_n={NUMBER_INDIVIDUALS}_{date_}"
folder = Path.cwd() / "runs" / run
folder.mkdir(parents=True, exist_ok=True)

# prepare folder to store results
network_shape = NetworkShape(n_inputs=NETWORK_INPUTS, n_outputs=NETWORK_OUTPUTS)

# initialize genetic
genetic = Genetic(
    number_individuals=NUMBER_INDIVIDUALS,
    network_shape=network_shape,
    mutation_probability=MUTATION_PROBABILITY,
    stagnation=15,
    selection=TopPercentageSelection(0.4),
    mutation_type=MutationType.SINGLE,
)

average_fitness_list = list()
max_fitness_list = list()

play = PLE(
    FlappyBird(width=WIDTH, height=HEIGHT, pipe_gap=100), fps=30, display_screen=display
)
actions = play.getActionSet()
play.init()

index = 0

if display:
    plt.figure()

while genetic.max_fitness < MAX_FITNESS:
    population = genetic.population

    for individual in population:
        fitness = list()

        for _ in range(RUNS_PER_INDIVIDUAL):
            random.seed(datetime.now())
            play.frame_count = 0

            while True:
                if play.game_over():
                    fitness.append(play.getFrameNumber())

                    play.reset_game()
                    break

                state = play.getGameState()
                features = (
                    state["player_y"] / HEIGHT,
                    state["player_vel"] / 8,
                    state["next_pipe_dist_to_player"] / WIDTH,
                    state["next_pipe_top_y"] / HEIGHT,
                    state["next_pipe_bottom_y"] / HEIGHT,
                    state["next_next_pipe_dist_to_player"] / WIDTH,
                    state["next_next_pipe_top_y"] / HEIGHT,
                    state["next_next_pipe_bottom_y"] / HEIGHT,
                )

                button_result = int(np.round(individual.evaluate(features)))

                play.act(actions[button_result])

        individual.fitness = sum(fitness) / len(fitness)

    max_fitness = max(population).fitness
    max_fitness_list.append(max_fitness)

    average_fitness = np.mean([network.fitness for network in population])
    average_fitness_list.append(average_fitness)

    genetic.population = population

    logger.info("#----------#")
    logger.info(f"Iteration: {index}")
    logger.info(f"max fitness: {max_fitness}")
    logger.info(f"average fitness: {average_fitness}")
    logger.info(f"distance value: {np.round(genetic.distance_threshold, 2)}")
    logger.info(f"species: {len(genetic.species)}")
    logger.info("#----------#\n")

    if (
        len(max_fitness_list) > REDIRECTION_TRIES
        and max_fitness_list[-REDIRECTION_TRIES] >= max_fitness_list[-1]
        and redirect_search_rounds == REDIRECTION_TRIES
    ):
        redirect_search = True
        redirect_search_rounds = 0
    else:
        redirect_search = False
        redirect_search_rounds += 1

    if redirect_search:
        logger.info("[INFO] -> Redirecting search...")

    genetic = genetic.evolve(redirection=redirect_search)

    best_individual = max(genetic.population)

    with open(
        str(folder / f"iteration={index}_max={int(max_fitness)}.pickle"), "wb"
    ) as handle:
        pickle.dump(genetic, handle, protocol=pickle.HIGHEST_PROTOCOL)

    index += 1

    if display:
        plt.cla()
        plt.plot(average_fitness_list)
        plt.plot(max_fitness_list)
        plt.draw()
        plt.pause(0.001)

if best_individual:
    best_individual.draw()
