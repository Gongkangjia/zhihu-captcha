import os
import logging

import numpy as np
import tensorflow as tf

from data import *
from model import check_points_dir

__all__ = ["predict_captcha", "captcha_logger"]


def _init_captcha_logger():
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.INFO)

    if len(logger.handlers) > 0:
        logger.handlers.clear()

    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), CAPTCHA_FILE_NAME)
    fh = logging.FileHandler(log_file, encoding="utf8")
    sh = logging.StreamHandler()
    fmt = logging.Formatter("%(message)s")
    fh.setFormatter(fmt)
    sh.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(sh)

    return logger


captcha_logger = _init_captcha_logger()

tf.reset_default_graph()
sess = tf.Session()
tf.train.import_meta_graph(os.path.join(check_points_dir(), "captcha_model-42000.meta"))
tf.train.Saver().restore(sess, tf.train.latest_checkpoint(check_points_dir()))
graph = tf.get_default_graph()

X = graph.get_tensor_by_name("input/input_x:0")
Y = graph.get_tensor_by_name("input/input_y:0")
keep_prob = graph.get_tensor_by_name("keep_prob/keep_prob:0")
logits = graph.get_tensor_by_name("final_output/logits:0")
predict = tf.argmax(tf.reshape(logits, [-1, CAPTCHA_LEN, CHAR_SET_LEN]), 2)


def predict_captcha(image):
    image = img2array(image)
    max_idx = sess.run(predict, feed_dict={X: [image], keep_prob: 1.0})
    char_idx = max_idx[0].tolist()
    vector = np.zeros(CAPTCHA_LEN * CHAR_SET_LEN)
    i = 0
    for idx in char_idx:
        vector[i * CHAR_SET_LEN + idx] = 1
        i += 1
    return vector2text(vector)


def test_accuracy():
    hits = 0
    for i in range(100):
        text, image = next_text_and_image()
        predict_text = predict_captcha(image)
        hit = False
        if text == predict_text:
            hit = True
            hits += 1
        print("Correct:", text, "Predict:", predict_text, "hit:", hit)

    print("Test 100 captchas. Accuracy:", hits / 100)


if __name__ == '__main__':
    test_accuracy()
