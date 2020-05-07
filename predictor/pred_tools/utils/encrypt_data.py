# -- Standard --
import io
import os
# -- 3rd Party --
import cryptography
from cryptography.fernet import Fernet
from django.conf import settings
from dotenv import load_dotenv
import pandas as pd
# -- local --
# None


# -------------------------------------------------------------------------------------------
# 前処理時に除きたい，情報を持たない列を暗号化して保存
# (trainデータにおいて, 値がすべて "NULL"(ユニークな値が0種) または "単一の値"(ユニークな値が1種) の列)
# -------------------------------------------------------------------------------------------
# os.environ["DJANGO_SETTINGS_MODULE"] = "predcsv_gen.settings.local"
# X_train = pd.DataFrame(pd.read_csv(os.path.join(settings.CSV_DIR, "train_test/train_x.csv")))
# pd.DataFrame(X_train.nunique(), columns=["n"]).query("n==1 | n==0").to_csv(os.path.join(settings.CSV_DIR, "for_pred/uninformed_column.csv"), index=False)


# ----------------------
# df_todoの暗号化を行う関数
# ----------------------
# "model_Todo.csv"の名前で保存してあるTodo.csvを暗号化する
# XGB_Todo.csvは列毎の操作(削除やダミー変数化など)を記載したデータ
def create_encrypt_data(todo_csv_name):
    os.environ["DJANGO_SETTINGS_MODULE"] = "predcsv_gen.settings.local"
    with open(os.path.join(settings.CSV_DIR, "for_pred/", todo_csv_name), 'rb') as f:
        data_original = f.read()
    key = Fernet.generate_key()
    fernet = Fernet(key)
    data_encrypted = fernet.encrypt(data_original)
    with open(os.path.join(os.path.dirname(settings.BASE_DIR), "predictor/pred_tools/data_encrypted/", f'{todo_csv_name}.encrypted'), 'wb') as f:
        f.write(data_encrypted)
    with open(".env", 'r') as f:
        env = f.read()
    target_env = f"{os.path.splitext(todo_csv_name)[0].upper()}_KEY"
    if target_env in env:
        os.system(f'sed -i -e "s/{target_env} = .*/{target_env} = {key.decode()}/" .env')
    else:
        os.system(f'echo {target_env} = {key.decode()} >> .env')


# ----------------------
# df_todoの復号化を行う関数
# ----------------------
def open_encrypt_data(todo_csv_encrypted_name):
    target_env = f"{os.path.splitext(os.path.splitext(todo_csv_encrypted_name)[0])[0].upper()}_KEY"
    # ローカルで環境変数が更新されないときだけ実行
    if settings.DEBUG:
        if target_env in os.environ:
            os.environ.pop(target_env)
        load_dotenv('.env')
    key = os.environ.get(target_env)
    with open(os.path.join(os.path.dirname(settings.BASE_DIR), "predictor/pred_tools/data_encrypted/", todo_csv_encrypted_name), 'rb') as f:
        data_encrypted = f.read()
    fernet = Fernet(key)
    data_original = fernet.decrypt(data_encrypted)
    return pd.read_csv(io.StringIO(data_original.decode()))


# XGB_Todo
# create_encrypt_data("XGB_Todo.csv")
# open_encrypt_data("XGB_Todo.csv.encrypted")

# uninformed column
# create_encrypt_data("uninformed_column.csv")
# open_encrypt_data("uninformed_column.csv.encrypted")["Unnamed: 0"]

# X_XGB
# create_encrypt_data("X_XGB.csv")
# open_encrypt_data("X_XGB.csv.encrypted")

# train_x
# create_encrypt_data("train_x.csv")
# open_encrypt_data("train_x.csv.encrypted")

# train_x_min
# create_encrypt_data("train_x_min.csv")
# open_encrypt_data("train_x_min.csv.encrypted")
