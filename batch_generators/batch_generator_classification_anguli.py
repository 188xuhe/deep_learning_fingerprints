import os
import pickle
from tqdm import tqdm
from scipy.misc import imread, imresize
import numpy as np
from glob import glob


class BatchGenerator_Classification_Anguli:


    def __init__(self, path='/home/sander/data/deep_learning_fingerprints/anguli/batch1', height=400, width=275):

        self.path = path
        self.height = height
        self.width = width

        self.image_ids, self.labels = self.parse_data(path)
        self.image_ids_train, self.labels_train = self.image_ids[:150000], self.labels[:150000]
        self.image_ids_val, self.labels_val = self.image_ids[150000:], self.labels[150000:]


    def parse_data(self, path):

        meta_path = path + 'Meta Info/fp_1/'
        images = glob(path + '/Impression_*/fp_1/*')
        meta_files = glob(path + '/Meta Info/fp_1/*')

        image_ids = list(set([int(x[:-4].split('/')[-1]) for x in images]))
        meta_ids = list([int(x[:-4].split('/')[-1]) for x in meta_files])
        image_ids.sort()
        meta_ids.sort()

        # counter = 0
        # for image_id in tqdm(image_ids):
        #     if image_id not in meta_ids:
        #         counter += 1
        # print(counter)

        if os.path.exists('labels.p'):
            labels = pickle.load(open('labels.p', 'rb'))
        else:
            labels = []
            for meta_id in tqdm(meta_ids):

                meta_file = meta_path + str(meta_id) + '.txt'

                with open(meta_file) as doc:
                    for line in doc.readlines():
                        # print(line)
                        if line.startswith('Type'):
                            label = line[7:].strip('\n')
                            labels.append(label)
            # Tokenize labels
            tokens = list(range(len(set(labels))))
            label_dict = {key: value for key, value in zip(sorted(set(labels)), tokens)}
            labels_tokenized = [label_dict[x] for x in labels]
            n_values = np.max(tokens) + 1
            labels_one_hot = np.eye(n_values)[labels_tokenized]

            pickle.dump(labels_one_hot, open('labels.p', 'wb'))

        return image_ids, labels


    def generate_batch(self, batch_size, image_ids, labels):

        x_batch = []
        y_batch = []

        for _ in range(batch_size):

            index = np.random.choice(range(len(image_ids)))
            if np.random.rand() < .5:
                image = imread(self.path+'Impression_1/'+str(image_ids[index])+'.jpg')
            else:
                image = imread(self.path+'Impression_2/' + str(image_ids[index]) + '.jpg')

            image = imresize(image, [self.height, self.width])
            x_batch.append(image)
            y_batch.append(labels[index])

        return np.array(x_batch).reshape(batch_size, self.imsize, self.imsize, 1), np.array(y_batch)


    def generate_train_batch(self, batch_size):

        return self.generate_batch(batch_size, self.image_ids_train, self.labels_train)


    def generate_val_batch(self, batch_size):

        return self.generate_batch(batch_size, self.image_ids_val, self.labels_val)

bg = BatchGenerator_Classification_Anguli()

x, y = bg.generate_train_batch(32)
x, y = bg.generate_val_batch(32)