# import csv
# from matplotlib import pyplot as plt
# listFeature = ['i' for i in range(75)]
# # feature_dict = {i:label for i,label in zip(
# #             range(4),
# #               ('sepal length in cm',
# #               'sepal width in cm',
# #               'petal length in cm',
# #               'petal width in cm', ))}
#
# feature_dict = {i:label for i,label in zip(
#             range(75), tuple(listFeature) )}
#
# import pandas as pd
#
# df = pd.io.parsers.read_csv(
#     #filepath_or_buffer='https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data',
#     filepath_or_buffer='/home/sayong/carData/train_data.csv',
#     header=None,
#     sep=',',
#     )
# df.columns = [l for i,l in sorted(feature_dict.items())] + ['class label']
# df.dropna(how="all", inplace=True) # to drop the empty line at file-end
#
# df.tail()
#
# df_test = pd.io.parsers.read_csv(
#     #filepath_or_buffer='https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data',
#     filepath_or_buffer='/home/sayong/carData/dataset_test/set_3/test_data_3.csv',
#     header=None,
#     sep=',',
#     )
# df_test.columns = [l for i,l in sorted(feature_dict.items())] + ['class label']
# df_test.dropna(how="all", inplace=True) # to drop the empty line at file-end
#
# df_test.tail()
#
# from sklearn.preprocessing import LabelEncoder
#
# X = df[[i for i in range(75)]].values
# y = df['class label'].values
#
# x_test = df_test[[i for i in range(75)]].values
# y_test = df_test['class label'].values
#
# enc = LabelEncoder()
# label_encoder = enc.fit(y)
# y = label_encoder.transform(y) + 1
# label_encoder = enc.fit(y_test)
# y_test = label_encoder.transform(y_test) + 1
#
#
# label_dict = {1: 'Truck', 2: 'Car', 3:'Bike'}
#
# from sklearn import preprocessing
# #preprocessing.scale(X, axis=0, with_mean=True, with_std=True, copy=False)
# #preprocessing.scale(x_test, axis=0, with_mean=True, with_std=True, copy=False)
#
#
# import numpy as np
#
# #import ipdb;ipdb.set_trace()
# from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
# from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis as QLDA
# sklearn_lda = LDA()
# X_lda_sklearn = sklearn_lda.fit(X,y)
# X_lda_test = sklearn_lda.predict(x_test)
#
# print np.mean(y_test == X_lda_test)
# from pandas_confusion import ConfusionMatrix
# cm = ConfusionMatrix(y_test, X_lda_test)
# cmData = cm.to_array('a')
# class_acc = [cmData[0][0], cmData[1][1], cmData[2][2]]


from sklearn.preprocessing import LabelEncoder
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as scikit_LDA
import numpy as np
import pandas as pd
from pandas_confusion import ConfusionMatrix
from sklearn.externals import joblib

class LDA:
    def __init__(self, num_feature, num_class ):
        self.num_feature = num_feature
        self.num_class = num_class
        self.listFeature = ['i' for i in range(self.num_feature)]
        self.feature_dict = {i:label for i, label in zip(
                    range(self.num_feature), tuple(self.listFeature))}
        self.lda = None
        self.training_data = None
        self.training_answer = None
        self.testing_data = None
        self.testing_answer = None

    def predict(self, data):
        np_data = np.array(data, dtype=np.float32)
        answer = self.lda.predict(np.array([np_data]))
        return answer[0]

    def training(self):
        self.lda = scikit_LDA()
        X_lda_sklearn = self.lda.fit(self.training_data,self.training_answer)

    def save_model(self, path):
        joblib.dump(self.lda, path+'main_app/media/model.pkl')

    def load_model(self, path):
        self.lda = joblib.load(path+'main_app/media/model.pkl')

    def file_input(self, data_file, type_set="train"):
        df = pd.io.parsers.read_csv(
            filepath_or_buffer=data_file,
            header=None,
            sep=',',
            )
        df.columns = [l for i, l in sorted(self.feature_dict.items())] + ['class label']
        df.dropna(how="all", inplace=True) # to drop the empty line at file-end
        df.tail()
        data = df[[i for i in range(self.num_feature)]].values

        answer = df['class label'].values
        answerList = [[0]*3 for x in range(len(answer))]
        for x in range(len(answerList)):
            answerList[x][int(answer[x])] = 1
        if type_set == "train":
            self.training_data = np.array(data.tolist(), dtype=np.float32)
            self.training_answer = np.array(answer)
        elif type_set == "test":
            self.testing_data = np.array(data.tolist(), dtype=np.float32)
            self.testing_answer = np.array(answer)

    def get_train_data(self):
        return self.training_data, self.training_answer

    def get_test_data(self):
        return self.testing_data, self.testing_answer
#
# import tensorflow as tf
# import numpy as np
# import pandas as pd
# from sklearn import preprocessing
# from pandas_confusion import ConfusionMatrix
#
# class neural_net:
#
#     def __init__(self, num_feature, num_class ):
#         self.num_feature = num_feature
#         self.num_class = num_class
#         self.listFeature = ['i' for i in range(75)]
#         self.feature_dict = {i:label for i, label in zip(
#                     range(75), tuple(self.listFeature))}
#         self.neural_struct = None
#         self.weight_in = None
#         self.weight_out = None
#         self.data_placeholder = tf.placeholder("float", [None, self.num_feature])
#         self.answer_placeholder = tf.placeholder("float", [None, self.num_class])
#         self.train_op = None
#         self.predict_op = None
#         self.training_data = None
#         self.training_answer = None
#         self.testing_data = None
#         self.testing_answer = None
#         self.sess = tf.Session()
#
#     def init_weights(self,shape):
#         return tf.Variable(tf.random_normal(shape, stddev=0.01))
#
#     def model(self, X, w_h, w_o):
#         h = tf.nn.sigmoid(tf.matmul(X, w_h)) # this is a basic mlp, think 2 stacked logistic regressions
#         return tf.matmul(h, w_o) # note that we dont take the softmax at the end because our cost fn does that for us
#
#     def create_struct(self, num_neural):
#         self.weight_in = self.init_weights([self.num_feature, num_neural])
#         self.weight_out = self.init_weights([num_neural, self.num_class])
#         self.neural_struct = self.model(self.data_placeholder, self.weight_in, self.weight_out)
#         cross = tf.nn.softmax_cross_entropy_with_logits(self.neural_struct, self.answer_placeholder)
#         cost = tf.reduce_mean(cross)
#         self.train_op = tf.train.AdamOptimizer(0.001).minimize(cost)
#         self.predict_op = tf.argmax(self.neural_struct, 1)
#
#     def training(self, epoch):
#         self.sess = tf.Session()
#         init = tf.initialize_all_variables()
#         self.sess.run(init)
#         for i in range(epoch):
#             for start, end in zip(range(0, len(self.training_data), 128), range(128, len(self.training_data), 128)):
#                 self.sess.run(self.train_op, feed_dict={self.data_placeholder: self.training_data[start:end],
#                                                         self.answer_placeholder: self.training_answer[start:end]})
#             print i, np.mean(np.argmax(self.training_answer, axis=1) ==
#                              self.sess.run(self.predict_op, feed_dict={self.data_placeholder: self.training_data,
#                                                                        self.answer_placeholder: self.training_answer}))
#             # print i, np.mean(np.argmax(self.testing_answer, axis=1) ==
#             #                  self.sess.run(self.predict_op, feed_dict={self.data_placeholder: self.testing_data,
#             #                                                            self.answer_placeholder: self.testing_answer}))
#
#     def file_input(self, data_file, type_set="train"):
#         df = pd.io.parsers.read_csv(
#             filepath_or_buffer=data_file,
#             header=None,
#             sep=',',
#             )
#         df.columns = [l for i, l in sorted(self.feature_dict.items())] + ['class label']
#         df.dropna(how="all", inplace=True) # to drop the empty line at file-end
#         df.tail()
#         data = df[[i for i in range(self.num_feature)]].values
#
#         answer = df['class label'].values
#         answerList = [[0]*3 for x in range(len(answer))]
#         for x in range(len(answerList)):
#             answerList[x][int(answer[x])] = 1
#         if type_set == "train":
#             self.training_data = np.array(data.tolist(), dtype=np.float32)
#             self.training_answer = np.array(answerList)
#         elif type_set == "test":
#             self.testing_data = np.array(data.tolist(), dtype=np.float32)
#             self.testing_answer = np.array(answerList)
#
#     def data_input(self, data, answer, type_set="train"):
#         answer_list = [[0]*3 for x in range(len(answer))]
#         for x in range(len(answer_list)):
#             answer_list[x][int(answer[x])] = 1
#         if type_set == "train":
#             self.training_data = np.array(data, dtype=np.float32)
#             self.training_data = preprocessing.scale(self.training_data, axis=0, with_mean=True, with_std=True, copy=False)
#             self.training_answer = np.array(answer_list)
#         elif type_set == "test":
#             self.testing_data = np.array(data, dtype=np.float32)
#             self.testing_data = preprocessing.scale(self.testing_data, axis=0, with_mean=True, with_std=True, copy=False)
#             self.testing_answer = np.array(answer_list)
#
#     def accuracy_info(self):
#         answerListB = self.testing_answer.tolist()
#         answerList = [answer.index(1) for answer in answerListB]
#         cm = ConfusionMatrix(answerList,
#                              self.sess.run(self.predict_op,
#                                            feed_dict={self.data_placeholder: self.testing_data,
#                                                       self.answer_placeholder: self.testing_answer}))
#         cmData = cm.to_array('a')
#         acc = [cmData[0][0], cmData[1][1], cmData[2][2]]
#         print cm
#         print acc
#
#     def predict(self, data):
#         np_data = np.array(data, dtype=np.float32)
#         answer = self.sess.run(self.predict_op, feed_dict={self.data_placeholder: np.array([np_data])})
#         return answer[0]
#
#     def get_train_data(self):
#         return self.training_data, self.training_answer
#
#     def get_test_data(self):
#         return self.testing_data, self.testing_answer
#
#     def save_model(self, path):
#         saver = tf.train.Saver()
#         saver.save(self.sess, path+'main_app/media/model.ckpt')
#
#     def load_model(self, path):
#         saver = tf.train.Saver()
#         saver.restore(self.sess, path+'main_app/media/model.ckpt')
