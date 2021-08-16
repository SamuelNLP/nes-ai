"""
A NEAT run on flappy bird
"""

import random
from datetime import datetime

import neat  # noqa
import numpy as np
from ple import PLE
from ple.games.flappybird import FlappyBird

WIDTH, HEIGHT = 288, 512


def eval_genomes(genomes, config_):

    play = PLE(
        FlappyBird(width=WIDTH, height=HEIGHT, pipe_gap=100),
        fps=30,
        display_screen=False,
    )
    actions = play.getActionSet()
    play.init()

    for genome_id, genome in genomes:
        fitness = []
        net = neat.nn.FeedForwardNetwork.create(genome, config_)

        for _ in range(5):
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
                    state["next_pipe_dist_to_player"] / WIDTH,
                    state["next_pipe_top_y"] / HEIGHT,
                    state["next_pipe_bottom_y"] / HEIGHT,
                )

                button_result = int(np.round(net.activate(features)))

                play.act(actions[button_result])

        genome.fitness = np.mean(fitness)


# Load configuration.
config = neat.Config(
    neat.DefaultGenome,
    neat.DefaultReproduction,
    neat.DefaultSpeciesSet,
    neat.DefaultStagnation,
    "flappy_bird_config_feedforward",
)

# Create the population, which is the top-level object for a NEAT run.
p = neat.Population(config)

# Add a stdout reporter to show progress in the terminal.
p.add_reporter(neat.StdOutReporter(False))

# Run until a solution is found.
winner = p.run(eval_genomes)

# Display the winning genome.
print("\nBest genome:\n{!s}".format(winner))

# Show output of the most fit genome against training data.
print("\nOutput:")
winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
