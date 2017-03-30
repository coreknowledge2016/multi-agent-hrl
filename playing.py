"""
Once a model is learned, use this to play it.
"""

import carmunk
import numpy as np
from nn import neural_net, neural_net2

NUM_SENSORS = 6


def play(model, model2):

    # car_distance = 0
    game_state = carmunk.GameState()

    # Do nothing to get initial.
    _, _, state, state2 = game_state.frame_step(2, 2)

    state = state.reshape(1, NUM_SENSORS)
    state2 = state2.reshape(1, NUM_SENSORS)
    # Move.
    while True:
        # car_distance += 1

        # Choose action.
        action = (np.argmax(model.predict(state, batch_size=10)))

        action2 = (np.argmax(model2.predict(state2, batch_size=10)))

        # Take action.
        _, _, state, state2 = game_state.frame_step(action, action2)

        state = state.reshape(1, NUM_SENSORS)
        state2 = state2.reshape(1, NUM_SENSORS)

        # Tell us something.
        # if car_distance % 1000 == 0:
        #     print("Current distance: %d frames." % car_distance)


if __name__ == "__main__":
    saved_model = 'saved-models/164-150-100-200-170000.h5'
    saved_model2 = 'saved-models2/0310-6-164-150-100-200-300000.h5'
    model = neural_net(NUM_SENSORS, [164, 150], saved_model)
    model2 = neural_net2(NUM_SENSORS, [164, 150], saved_model2)
    play(model, model2)
