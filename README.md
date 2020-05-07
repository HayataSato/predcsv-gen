[Predcsv-Generator](https://predcsv-gen.herokuapp.com/)
====

## 概要
* 言語：Python(3.8.0)
* フレームワーク：Django(3.0.5)
* プロジェクトディレクトリ：predcsv_gen
* アプリケーションディレクトリ：predictor
* デプロイ先: Heroku
    * プラグイン: PostgreSQL, Redis, heroku-config(for .env)
* 非同期処理: Redis(KVS), Celery(Worker)

<br>

## predcsvの生成の流れ
* [templates](https://github.com/HayataSato/predcsv-gen/tree/master/predictor/templates/predictor)
    * [フォーム](https://github.com/HayataSato/predcsv-gen/blob/master/predictor/forms.py) を表示してモデルとcsvファイルを受け取ってview(ハンドラ関数)に渡す．
    * RedisとCeleryで管理している非同期タスクの実行状態によって表示を分岐させている．

* views.py
    * フォームのバリデーションを実行．
        * モデルのトレーニングに使用したオリジナルの訓練データ(x_train.csv)が持つ列と，入力のcsvとの突合
        * 拡張子の確認
    * フォームのインプットを受け取って，非同期タスクを実行．

* [tasks.py](https://github.com/HayataSato/predcsv-gen/blob/master/predcsv_gen/tasks.py) 
    * 非同期で実行時間が掛かるバリデーションの一部から，前処理，予測までを実行する generator関数 を定義．
        * 前処理～予測については[pred_tools](https://github.com/HayataSato/predcsv-gen/tree/master/predictor/pred_tools) で定義したモデル毎のクラスを使用．

