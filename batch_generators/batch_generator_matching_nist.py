from tqdm import tqdm
from scipy.misc import imread, imresize
import numpy as np
from glob import glob

class BatchGenerator_Matching_NIST:

    def __init__(self, path=None, height=512, width=512):

        self.path = path
        self.height, self.width, = height, width
        self.images, self.ids = self.parse_data()
        self.sample_ids = list(set([x[1:] for x in self.ids]))

        self.sample_ids_train = self.sample_ids[:1600]
        self.sample_ids_val = self.sample_ids[1600:]

    def parse_data(self):

        file_list = glob(self.path + '/*' + '/*')

        ids = list(set([x[:-4].split('/')[-1] for x in file_list]))
        if 'Thumb' in ids:
            ids.remove('Thumb')

        images = []

        for id in tqdm(ids):
            image_path = [x for x in file_list if x.find(id) > -1 and x.endswith('png')][0]
            img = imread(image_path)
            if self.height != 512 or self.width != 512:
                img = imresize(img, [self.height, self.width])
            img = img.reshape([self.height, self.width, 1])
            img = img / 255
            images.append(img)

        return images, ids


    def generate_triplet_batch(self, batch_size, candidate_ids):

        batch = []

        for _ in range(batch_size):

            anchor_id = np.random.choice(candidate_ids)
            anchor_index = self.ids.index('f' + anchor_id)
            pos_index = self.ids.index('s' + anchor_id)
            if np.random.rand() < .5:
                anchor_index, pos_index = pos_index, anchor_index

            candidate_ids_neg = [x for x in candidate_ids if x != anchor_id]
            neg_id = np.random.choice(candidate_ids_neg)
            if np.random.rand() < .5:
                neg_index = self.ids.index('f' + neg_id)
            else:
                neg_index = self.ids.index('s' + neg_id)

            anchor_img, pos_img, neg_img = self.images[anchor_index], self.images[pos_index], self.images[neg_index]

            triplet = np.concatenate([anchor_img, pos_img, neg_img], axis=2)
            batch.append(triplet)

        return np.array(batch)


    def generate_duo_batch_with_labels(self, batch_size, candidate_ids):

        x_batch = []
        y_batch = []

        for _ in range(batch_size):

            anchor_id = np.random.choice(candidate_ids)
            anchor_index = self.ids.index('f' + anchor_id)
            partner_index = self.ids.index('s' + anchor_id)

            # pos case
            if np.random.rand() < .5:
                if np.random.rand() < .5:
                    anchor_index, partner_index = partner_index, anchor_index
                label = 1

            # neg case
            else:
                candidate_ids_neg = [x for x in candidate_ids if x != anchor_id]
                neg_id = np.random.choice(candidate_ids_neg)
                if np.random.rand() < .5:
                    partner_index = self.ids.index('f' + neg_id)
                else:
                    partner_index = self.ids.index('s' + neg_id)
                label = 0

            anchor_img = self.images[anchor_index]
            partner_img = self.images[partner_index]

            duo = np.concatenate([anchor_img, partner_img, partner_img], axis=2)

            x_batch.append(duo)
            y_batch.append(label)

        return np.array(x_batch), np.array(y_batch).reshape(batch_size, 1)

    def generate_train_triplets(self, batch_size):

        return self.generate_triplet_batch(batch_size, self.sample_ids_train)

    def generate_val_triplets(self, batch_size):

        return self.generate_triplet_batch(batch_size, self.sample_ids_val)

    def generate_train_duos(self, batch_size):

        return self.generate_duo_batch_with_labels(batch_size, self.sample_ids_train)

    def generate_val_duos(self, batch_size):

        return self.generate_duo_batch_with_labels(batch_size, self.sample_ids_val)
#
# H=400
# W=275
# bg = BatchGenerator_Matching_NIST(path='/home/sander/data/deep_learning_fingerprints/sd04/png_txt', height=H, width=W)
#
# batch = bg.generate_val_triplets(32)
#
# import matplotlib.pyplot as plt
# batch.shape
#
# anchor=batch[0, :, :, 0].reshape(H, W)
# # pos=batch[0, :, :, 1].reshape(H, W)
# # neg=batch[0, :, :, 2].reshape(H, W)
# # show = np.concatenate([anchor, pos, neg], axis=0)
# # plt.imshow(show, cmap='gray')
#
#
# np.mean(anchor)
# plt.imshow(anchor, cmap='gray')
# plt.show()
#
#
# def augment(images):
#
#     noise = tf.random_normal(shape=tf.shape(images), mean=0.0, stddev=0.1,
#                              dtype=tf.float32)
#     images = tf.add(images, noise)
#
#     images = tf.map_fn(lambda img: tf.image.random_brightness(img, max_delta=1.), images)
#     images = tf.map_fn(lambda img: tf.image.random_contrast(img, lower=0, upper=1), images)
#
#     return images
#
# import tensorflow as tf
# tf.enable_eager_execution()
# anchor = augment(anchor.reshape(1, H,W,1))
#
# anchor = np.array(anchor).reshape(H, W)
#
# np.mean(anchor)
#
# plt.imshow(anchor, cmap='gray')
# plt.show()