"""
Once a model is learned, use this to play it.
"""

import carmunk
import numpy as np
from nn import neural_net

NUM_SENSORS = 6


def play(model):

    car_distance = 0
    game_state = carmunk.GameState()

    # Do nothing to get initial.
    _, state = game_state.frame_step(2,2)
    state = state.reshape(1,NUM_SENSORS)
    # Move.
    while True:
        car_distance += 1

        # Choose action.
        action = (np.argmax(model.predict(state, batch_size=10)))
    
        # action2 = (np.argmax(model.predict(state2, batch_size=10)))

        # Take action.
        _, state = game_state.frame_step(action, action2)
        state = state.reshape(1, NUM_SENSORS)

        # Tell us something.
        if car_distance % 1000 == 0:
            print("Current distance: %d frames." % car_distance)


if __name__ == "__main__":
    saved_model = 'saved-models/164-150-100-200-200000.h5'
    model = neural_net(NUM_SENSORS, [164, 150], saved_model)
    play(model)
