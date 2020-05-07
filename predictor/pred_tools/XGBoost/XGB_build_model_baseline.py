# -- Standard --
import csv
import os
import pickle
# -- 3rd Party --
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import xgboost as xgb
# -- local --
# None


# ----------------------
#  CSVの読み込み ＆ 俯瞰
# ----------------------
# 読み込み

X_train = pd.read_csv(os.path.join(settings.CSV_DIR, "train_test/train_x.csv"))
Y_train = pd.read_csv(os.path.join(settings.CSV_DIR, "train_test/train_y.csv"))
X_test = pd.read_csv(os.path.join(settings.CSV_DIR, "train_test/test_x.csv"))
# 重複データの削除
X_train = X_train.drop_duplicates(subset="お仕事No.", ignore_index=False, keep="first").reset_index(drop=True)
Y_train = Y_train.drop_duplicates(subset="お仕事No.", ignore_index=False, keep="first").reset_index(drop=True)
# 俯瞰
print("X_train: ", X_train.shape, "\nY_train: ", Y_train.shape, "\nX_test : ", X_test.shape, sep="")
print(X_train.columns)
print(Y_train.columns)


# ----------------------
#      前処理の準備
# ----------------------
# -- 説明変数DFをtrain testで結合 --
# 結合
X = pd.merge(X_train.assign(type="train"), X_test.assign(type="test"), how="outer")
# trainデータにおいて, 値がすべて "NULL"(ユニークな値が0種) または "単一の値"(ユニークな値が1種) の列をDrop
X.drop(columns=pd.DataFrame(X_train.nunique(), columns=["n"]).query("n==1 | n==0").index, axis=1, inplace=True)

# 確認
print(X.shape)


# ----------------------
#         前処理
# ----------------------
# One-Hot Encoding
# 対象の列を取得
df_todo = pd.read_csv(filepath_or_buffer=os.path.join(settings.CSV_DIR, "for_pred/XGB_Todo.csv"))
cols_to_onehot = df_todo.query(" Detail == \"One-Hot Encoding(NULLあり)\"")["column"]
# One-Hot したい列の，unique値の数を確認
X[cols_to_onehot].nunique()
# One-Hot Encoding
X = pd.get_dummies(data=X, dummy_na=True, columns=cols_to_onehot)
print(X.shape)
# 保留or削除 対象の列を取得
cols_on_hold = df_todo.query(" Todo == \"保留\"")["column"]
cols_exclude = df_todo.query(" Todo == \"削除\"")["column"]
# Drop
X.drop(columns=cols_on_hold, axis=1, inplace=True)
X.drop(columns=cols_exclude, axis=1, inplace=True)
print(X.shape)


# ----------------------
#     モデリングの準備
# ----------------------
# 除外対象の列を取得
cols_exclude_to_modeling = df_todo.query(" Todo == \"モデリングの際には除く\"")["column"]
# 後で使用するDF作成
df_type_oshigotonumber = X[cols_exclude_to_modeling]
# Drop
X.drop(columns=cols_exclude_to_modeling, axis=1, inplace=True)
print(X.shape)
X.to_csv(path_or_buf=os.path.join(settings.CSV_DIR, "for_pred/X_XGB.csv"), index=False)
# train & test のarray作成
# モデリング用
X_train_ary, X_valid_ary, Y_train_ary, Y_valid_ary = train_test_split(np.array( X.iloc[df_type_oshigotonumber.query("type == \"train\"").index] ),
                                                                      np.array(Y_train.drop("お仕事No.", axis=1)),
                                                                      test_size=0.2,
                                                                      random_state=0
                                                                      )
# 提出用
X_test_ary = np.array( X.iloc[df_type_oshigotonumber.query("type == \"test\"").index] )


# ----------------------
#       モデリング
# ----------------------
# 学習
model = xgb.XGBRegressor(objective="reg:squarederror")
model.fit(X_train_ary, Y_train_ary)
# 予測
Y_pred = model.predict(X_valid_ary)
rmse = np.sqrt(mean_squared_error(Y_valid_ary, Y_pred))
print(rmse)
# 提出用データの予測
result = pd.DataFrame(data={"お仕事No.": X_test["お仕事No."],
                      "応募数 合計": model.predict(X_test_ary)})

# モデルの出力
pickle.dump(model, open(os.path.join(settings.MODEL_DIR, "XGBoost/XGBoost_0505_baseline.pickle"), 'wb'))