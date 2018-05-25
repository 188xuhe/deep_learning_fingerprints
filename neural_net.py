import tensorflow as tf

class NeuralNet(object):

    def __init__(self, height, width, channels, batchgen):

        self.batchgen = batchgen

        self.graph = tf.Graph()

        self.session = tf.Session()  # config=tf.ConfigProto(log_device_placement=True)

        self.x = tf.placeholder(dtype=tf.float32, shape=[None, height, width, channels], name='input')
        self.x = tf.map_fn(lambda img: tf.image.per_image_standardization(img), self.x)

        self.dropout_rate = tf.placeholder(tf.float32)

        self.x_a, self.x_b = tf.split(self.x, [1, 1], axis=2)

        with tf.variable_scope('scope'):
            self.output_a = self.CNN(self.input_a, self.keep_prob)

        with tf.variable_scope('scope', reuse=True):
            self.output_b = self.CNN(self.input_b, self.keep_prob)

        self.concat = tf.concat([self.output_a, self.output_b], axis=1)

        self.fc1 = tf.layers.dense(inputs=self.concat,
                                   units=128,
                                   activation=tf.nn.relu,
                                   kernel_initializer=tf.keras.initializers.he_normal())

        self.fc2 = tf.layers.dense(inputs=self.fc1,
                                   units=128,
                                   activation=tf.nn.relu,
                                   kernel_initializer=tf.keras.initializers.he_normal())

        self.output = tf.dense(inputs=self.fc2,
                               units=1)

        self.output = tf.sigmoid(self.output)

        self.labels = tf.placeholder(dtype=tf.float32, shape=[None, 1])
        self.loss = tf.losses.log_loss(self.labels, self.output)
        self.optimizer = tf.train.AdamOptimizer()
        self.train_step = self.optimizer.minimize(self.loss)

        self.init_op = tf.global_variables_initializer()
        self.session.run(self.init_op)
        self.saver = tf.train.Saver(max_to_keep=None,
                                    name='checkpoint_saver')

    def Conv2D(self, x, filters, kernel_size, stride, padding='same'):
        return tf.layers.conv2d(inputs=x,
                                filters=filters,
                                kernel_size=kernel_size,
                                strides=stride,
                                activation=tf.nn.relu,
                                kernel_initializer=tf.keras.initializers.he_normal(),
                                kernel_regularizer=tf.keras.regularizers.l2(l=0.01),
                                activity_regularizer=tf.keras.regularizers.l2(l=0.01),
                                padding=padding)

    def CNN(self, x):

        x = self.Conv2D(x, 8, 3, 1)
        x = tf.layers.max_pooling2d(x, 2, 2)

        x = self.Conv2D(x, 8, 3, 1)
        x = tf.layers.max_pooling2d(x, 2, 2)

        x = self.Conv2D(x, 8, 3, 1)
        x = tf.layers.max_pooling2d(x, 2, 2)

        x = self.Conv2D(x, 8, 3, 1)
        x = tf.layers.max_pooling2d(x, 2, 2)

        return x

    def train(self, num_steps, batch_size, dropout_rate, lr, decay, checkpoint='models/neural_net'):

        loss_list = []
        val_loss_list = []

        for step in range(num_steps):

            x_batch, y_batch, boundary_batch = self.batchgen.generate_batch(batch_size)

            feed_dict = {
                self.x: x_batch,
                self.label: y_batch,
                self.dropout_rate: dropout_rate,
                self.lr: lr
            }

            loss_, _ = self.session.run([self.loss, self.train_step], feed_dict=feed_dict)
            lr *= decay

            if step % 100 == 0:
                x_batch, y_batch, boundaries_batch = self.batchgen.generate_val_data()
                feed_dict = {
                    self.x: x_batch,
                    self.label: y_batch,
                    self.dropout_rate: 0
                }
                val_loss = self.session.run([self.loss], feed_dict=feed_dict)
                val_loss_list.append(val_loss)
                loss_list.append(loss_)
                print('step: {}'.format(step))
                print('train loss: {}'.format(loss_))
                print('val loss: {}'.format(val_loss))
                print('lr: {}'.format(lr))
                print('')

            if (step + 1) % 1000 == 0 or step == num_steps - 1:
                self.saver.save(self.session, checkpoint + str(step) + '.ckpt')
                print('Saved to {}'.format(checkpoint + str(step) + '.ckpt'))

        return loss_list, val_loss_list



