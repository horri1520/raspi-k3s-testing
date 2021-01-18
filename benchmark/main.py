import glob
import os
import time

import tensorflow as tf
from flask import Flask, abort, request, send_file
from tensorflow.keras.datasets import mnist
from tensorflow.keras.layers import Dense, InputLayer
from tensorflow.keras.models import Sequential

app = Flask(__name__)

# YOUR_APP_URL = 'http://192.168.1.226/'
# YOUR_APP_URL = 'http://192.168.1.214/'


@app.route("/")
def index():
    return 'Regnio Raspberry Pi 4 cluster'


@app.route("/start_test")
def start_test():

    start_time = time.time()
    print(f'start at {start_time}')

    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    x_train = x_train.reshape(60000, 784)
    x_test = x_test.reshape(10000, 784)
    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255
    y_train = tf.keras.utils.to_categorical(y_train, 10)
    y_test = tf.keras.utils.to_categorical(y_test, 10)

    model = Sequential()
    model.add(InputLayer(input_shape=(784,)))
    model.add(Dense(10, activation='softmax'))
    model.compile(loss='categorical_crossentropy',
                  optimizer='rmsprop', metrics=['accuracy'])
    model.summary()

    epochs = 10
    batch_size = 128
    history = model.fit(x_train, y_train, batch_size=batch_size,
                        epochs=epochs, verbose=1, validation_data=(x_test, y_test))

    score = model.evaluate(x_test, y_test, verbose=1)

    end_time = time.time()
    print(f'end at {end_time}')

    time_consumption = end_time - start_time
    print(f'time: {time_consumption}s')
    return f'time consumption: {str(time_consumption)}s'


if __name__ == "__main__":
    port = 3000
    app.run(host="0.0.0.0", port=port)
