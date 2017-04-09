# from flat_game import catmouse
import catmouse
import numpy as np
import random
import csv
from nn import neural_net, neural_net2, LossHistory, LossHistory2
import os.path
import timeit
from keras.callbacks import TensorBoard

NUM_INPUT = 6
GAMMA = 0.9  # Forgetting.
TUNING = False  # If False, just use arbitrary, pre-selected params.


def train_net(model1, model2, params):

    filename = params_to_filename(params)

    observe = 1000  # Number of frames to observe before training.
    epsilon = 1
    train_frames = 500000  # Number of frames to play.
    batchSize = params['batchSize']
    buffer = params['buffer']

    # Just stuff used below.
    # max_cat_distance = 0
    # cat_distance = 0
    t = 0
    # data_collect = []
    replay = []  # stores tuples of (S, A, R, S').
    replay2 = []


    loss_log = []
    loss_log2 = []

    # Create a new game instance.
    game_state = catmouse.GameState()

    # Get initial state by doing nothing and getting the state.
    _, _, state, state2 = game_state.frame_step(4, 4)

    # Let's time it.
    # start_time = timeit.default_timer()

    # Run the frames.
    while t < train_frames:

        t += 1
        # cat_distance += 1

        # Choose an action.
        if random.random() < epsilon or t < observe:
            action = np.random.randint(0, 3)  # random
            action2 = np.random.randint(0, 3)
        else:
            # Get Q values for each action.
            state = state.reshape(1, NUM_INPUT)  # reshape
            state2 = state2.reshape(1, NUM_INPUT)

            qval = model.predict(state, batch_size=1)
            qval2 = model2.predict(state2, batch_size=1)

            action = (np.argmax(qval))  # best
            action2 = (np.argmax(qval2))

        # Take action, observe new state and get our treat.
        reward, reward2, new_state, new_state2 = game_state.frame_step(action, action2)

        # Experience replay storage.
        replay.append((state, action, reward, new_state))
        replay2.append((state2, action2, reward2, new_state2))

        # If we're done observing, start training.
        if t > observe:

            # If we've stored enough in our buffer, pop the oldest.
            if len(replay) > buffer:
                replay.pop(0)

            if len(replay2) > buffer:
                replay2.pop(0)

            # Randomly sample our experience replay memory
            minibatch = random.sample(replay, batchSize)
            minibatch2 = random.sample(replay2, batchSize)
            # Get training values.
            X_train, y_train = process_minibatch(minibatch, model)
            X_train2, y_train2 = process_minibatch(minibatch2, model2)


            # Train the model on this batch.,
            #Tensorboard
            # tbCallBack = TensorBoard(log_dir='./Graph', histogram_freq=0)

            history = LossHistory()
            history2 = LossHistory2()


            model.fit(
                X_train, y_train, batch_size=batchSize,
                nb_epoch=1, verbose=0, callbacks=[history]
            )
            loss_log.append(history.losses)


            model2.fit(
                X_train2, y_train2, batch_size=batchSize,
                nb_epoch=1, verbose=0, callbacks=[history2]
            )
            loss_log2.append(history2.losses2)


        # Update the starting state with S'.
        state = new_state
        state2 = new_state2

        # Decrement epsilon over time.
        if epsilon > 0.1 and t > observe:
            epsilon -= (1 / train_frames)

        # We died, so update stuff.
        # if reward == -500:
        #     # Log the cat's distance at this T.
        #     data_collect.append([t, cat_distance])

        #     # Update max.
        #     if cat_distance > max_cat_distance:
        #         max_cat_distance = cat_distance

        #     # Time it.
        #     tot_time = timeit.default_timer() - start_time
        #     fps = cat_distance / tot_time

        #     # Output some stuff so we can watch.
        #     print("Max: %d at %d\tepsilon %f\t(%d)\t%f fps" %
        #           (max_cat_distance, t, epsilon, cat_distance, fps))

        #     # Reset.
        #     cat_distance = 0
        #     start_time = timeit.default_timer()

        # Save the model every 25,000 frames.
        if t % 13000 == 0:
            model.save_weights('saved-models/' + filename + '-' +
                               str(t) + '.h5',
                               overwrite=True)
            print("Saving model %s - %d" % (filename, t))

            model2.save_weights('saved-models2/' + filename + '-' +
                               str(t) + '.h5',
                               overwrite=True)
            print("Saving model2 %s - %d" % (filename, t))

    # Log results after we're done all frames.
            log_results(filename, loss_log, loss_log2)



def log_results(filename, loss_log, loss_log2):
    # Save the results to a file so we can graph it later.
    # with open('results/sonar-frames/learn_data-' + filename + '.csv', 'w') as data_dump:
    #     wr = csv.writer(data_dump)
    #     wr.writerows(data_collect)

    with open('results/sonar-frames/loss_data-' + filename + '.csv', 'w') as lf:
        wr = csv.writer(lf)
        for loss_item in loss_log:
            wr.writerow(loss_item)

    with open('results/sonar-frames/loss_data2-' + filename + '.csv', 'w') as lf2:
        wr = csv.writer(lf2)        
        for loss_item2 in loss_log2:
            wr.writerow(loss_item2)


def process_minibatch(minibatch, model):
    """This does the heavy lifting, aka, the training. It's super jacked."""
    X_train = []  # state
    y_train = []  # Q
    # Loop through our batch and create arrays for X and y
    # so that we can fit our model at every step.
    for memory in minibatch:
        # Get stored values.
        old_state_m, action_m, reward_m, new_state_m = memory

        old_state_m = old_state_m.reshape(1, NUM_INPUT)
        new_state_m = new_state_m.reshape(1, NUM_INPUT)

        # print old_state_m,new_state_m

        # Get prediction on old state.
        old_qval = model.predict(old_state_m, batch_size=1)
        # Get prediction on new state.
        newQ = model.predict(new_state_m, batch_size=1)
        # Get our best move. I think?
        maxQ = np.max(newQ)
        y = np.zeros((1, 5))  # three actions
        y[:] = old_qval[:]
        # Check for terminal state.
        if reward_m != 500 or reward_m != -500:  # non-terminal state
            update = (reward_m + (GAMMA * maxQ))
        else:  # terminal state
            update = reward_m
        # Update the value for the action we took.
        y[0][action_m] = update
        X_train.append(old_state_m.reshape(NUM_INPUT,))
        y_train.append(y.reshape(5,))

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    return X_train, y_train


def params_to_filename(params):
    return str(params['nn'][0]) + '-' + str(params['nn'][1]) + '-' + \
        str(params['batchSize']) + '-' + str(params['buffer'])


def launch_learn(params):
    filename = params_to_filename(params)
    print("Trying %s" % filename)
    # Make sure we haven't run this one.
    if not os.path.isfile('results/sonar-frames/loss_data-' + filename + '.csv'):
        # Create file so we don't double test when we run multiple
        # instances of the script at the same time.
        open('results/sonar-frames/loss_data-' + filename + '.csv', 'a').close()

    elif not os.path.isfile('results/sonar-frames/loss_data2-' + filename + '.csv'):

        open('results/sonar-frames/loss_data2-' + filename + '.csv', 'a').close()

        print("Starting test.")
        # Train.
        model = neural_net(NUM_INPUT, params['nn'])
        model2 = neural_net2(NUM_INPUT, params['nn'])
        train_net(model, model2, params)
    else:
        print("Already tested.")


if __name__ == "__main__":
    if TUNING:
        param_list = []
        nn_params = [[164, 150], [256, 256],
                     [512, 512], [1000, 1000]]
        batchSizes = [40, 100, 400]
        buffers = [10000, 50000]

        for nn_param in nn_params:
            for batchSize in batchSizes:
                for buffer in buffers:
                    params = {
                        "batchSize": batchSize,
                        "buffer": buffer,
                        "nn": nn_param
                    }
                    param_list.append(params)

        for param_set in param_list:
            launch_learn(param_set)

    else:
        nn_param = [164, 150]
        params = {
            "batchSize": 100,
            "buffer": 200,
            "nn": nn_param
        }
        model = neural_net(NUM_INPUT, nn_param)
        model2 = neural_net(NUM_INPUT, nn_param)
        train_net(model, model2, params)
