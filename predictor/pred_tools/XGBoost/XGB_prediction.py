# -- Standard --
import os
import pickle
# -- 3rd Party --
from django.conf import settings
import numpy as np
import pandas as pd
# -- local --
from predictor.pred_tools.utils.encrypt_data import open_encrypt_data
# None


# Define Class
class XgbPred:
    """The class creates a preprocessed DataFrame from the form input and predicts it.

    Attributes:
            X_input        (DataFrame): The data we try to prediction that is selected by "data_name" argument.(Droped "お仕事No." column)
            oshigoto_no  (Series[int]): The unique id column of input data.
            model       (XGBRegressor): The XGB-model for prediction that is selected by "model_name" argument.

    """
    def __init__(self, data_name, model_name):
        """Constructor
        Args:
            data_name  (str): The file name of the input csv data.
            model_name (str): The file name of a XGB-model that is saved with pickle.
        """
        self.X_input = pd.read_csv(os.path.join(settings.CSV_DIR, "input", data_name))
        self.oshigoto_no = self.X_input["お仕事No."]
        self.X_input.drop(columns="お仕事No.", axis=1, inplace=True)
        self.model = pickle.load(open(os.path.join(settings.MODEL_DIR, "XGBoost", model_name), "rb"))

    # Define Methods
    def prep(self):
        """This function does pre-processing input data.

        Returns:
            DataFrame: It returned the preprocessed data as X_prep.

        """
        # ----------------------
        #         前処理
        # ----------------------
        # 値がすべて "NULL"(ユニークな値が0種) または "単一の値"(ユニークな値が1種) の列をDrop
        X_prep = self.X_input.drop(columns=open_encrypt_data("uninformed_column.csv.encrypted")["Unnamed: 0"], axis=1)
        # One-Hot Encoding
        # 対象の列を取得
        df_todo = open_encrypt_data("XGB_Todo.csv.encrypted")
        cols_to_onehot = df_todo.query(" Detail == \"One-Hot Encoding(NULLあり)\"")["column"]
        # One-Hot Encoding
        X_prep = pd.get_dummies(data=X_prep, dummy_na=True, columns=cols_to_onehot)
        # 保留or削除 対象の列を取得
        cols_on_hold = df_todo.query(" Todo == \"保留\"")["column"]
        cols_exclude = df_todo.query(" Todo == \"削除\"")["column"]
        # Drop
        X_prep.drop(columns=cols_on_hold, axis=1, inplace=True)
        X_prep.drop(columns=cols_exclude, axis=1, inplace=True)
        # modelの訓練に使用したデータに存在する列だけを残し，無ければ追加
        X_train = open_encrypt_data("X_XGB.csv.encrypted")

        drop_cols = set(X_prep.columns) - set(X_train.columns)
        add_cols = set(X_train.columns) - set(X_prep.columns)
        X_prep.drop(columns=drop_cols, inplace=True)
        for col in add_cols:
            X_prep[col] = None
        # ----------------------
        #       return
        # ----------------------
        return X_prep

    def prediction(self):
        """This function makes a prediction with the returned array by prep function.

        Returns:
            DataFrame: It has two columns, "お仕事No."(unique id) and "応募数 合計"(predict value).

        """
        # ----------------------
        #         予測
        # ----------------------
        X_prep = self.prep()
        X_prep_array = np.array(X_prep)
        # 予測
        Y_pred = self.model.predict(X_prep_array)
        # ----------------------
        #       return
        # ----------------------
        # 出力用DFの作成
        return pd.DataFrame(data={"お仕事No.": self.oshigoto_no, "応募数 合計": Y_pred})