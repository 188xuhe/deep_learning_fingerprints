import numpy as np
import matplotlib.pyplot as plt
from batch_generators.batch_generator_classification_nist import BatchGenerator_Classification_NIST
from batch_generators.batch_generator_classification_anguli import BatchGenerator_Classification_Anguli
from neural_nets.neural_net_classification import NeuralNet_Classification

########################################
# Set globals
########################################

path = '/home/sander/data/deep_learning_fingerprints/sd04/png_txt'
HEIGHT = 400
WIDTH = 275
BATCH_SIZE = 32
NUM_STEPS = 1001
CATEGORIES = 5

bg_anguli = BatchGenerator_Classification_Anguli(height=HEIGHT, width=WIDTH)
bg_nist = BatchGenerator_Classification_NIST(height=HEIGHT, width=WIDTH)

nn = NeuralNet_Classification(HEIGHT, WIDTH, CATEGORIES)

loss, val_loss = nn.train(num_steps=NUM_STEPS,
                          batchgen=bg_anguli,
                          batch_size=BATCH_SIZE,
                          dropout_rate=0.5,
                          lr=.0001,
                          decay=1)


plt.plot(loss, color='b', alpha=.7)
plt.plot(val_loss, color='g', alpha=.7)
plt.show()


########################################
# Determine acc
########################################

samples = 0
correct = 0
for i in range(10):
    x, y = bg.generate_train_batch(32)
    for img, label in zip(x, y):
        samples += 1
        pred = nn.predict(img)
        if np.argmax(pred) == np.argmax(label):
            correct += 1

print('Train acc: {}'.format(correct/samples))

samples = 0
correct = 0
for i in range(10):
    x, y = bg.generate_val_batch(32)
    for img, label in zip(x, y):
        samples += 1
        pred = nn.predict(img)
        if np.argmax(pred) == np.argmax(label):
            correct += 1

print('Val acc: {}'.format(correct/samples))