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
