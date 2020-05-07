# -- Celery --
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time
# -- Standard --
import io
import os
import re
# -- 3rd Party --
from django.conf import settings
from django.core.exceptions import ValidationError
import pandas as pd
# -- local --
from predictor.forms import PredForm
from predictor.pred_tools.XGBoost.XGB_prediction import XgbPred
from predictor.pred_tools.utils.encrypt_data import open_encrypt_data


class CeleryTaskError(Exception):
    """An Error Exception that is occured by CeleryTask"""
    def __init__(self, message):
        self.message = f"Error occerd in Celery Task \n{message}"


@shared_task
def generator(path_saved_csv):
    """

    Args
        path_saved_csv (str): An absolute path saved csv that is inputed from the form on index.html.

    Returns:
        path_file_output (str): An absolute path of pred-csv(Named "pred_{original inputed file name}.csv").

    Errors:
        CeleryTaskError: Error to recognize an Exception in a scheduled task.
        ValidationError: This error will occurr when the input-csv is unsuitable as input.
    """
    # validation
    try:
        input_df = pd.read_csv(io.StringIO(open(path_saved_csv, "rb").read().decode("utf-8")), delimiter=",")
    except Exception as e:
        raise CeleryTaskError('type: ' + str(type(e)) + "\n" + "message: " + str(e))
    if set(input_df.columns) != set(open_encrypt_data("train_x_min.csv.encrypted").columns):
        unnecessary = set(input_df.columns) - set(open_encrypt_data("train_x_min.csv.encrypted").columns)
        necessary = set(open_encrypt_data("train_x_min.csv.encrypted").columns) - set(input_df.columns)
        raise ValidationError(
            message=f"Validation Error\nPlease upload the file that has same column as the original data . \n Unnecessary Cols： {unnecessary} \n Necessary Cols： {necessary}..")
    name_file_input = os.path.basename(path_saved_csv)
    try:
        # Prediction
        xgb = XgbPred(data_name=name_file_input, model_name="XGBoost_0505_baseline.pickle")
        Y_pred_df = xgb.prediction()
        # Create output csv
        path_file_output = os.path.join(settings.CSV_DIR, "output",
                                        "pred_" + os.path.splitext(name_file_input)[0] + ".csv")
        Y_pred_df.to_csv(path_or_buf=path_file_output)
        # Output (Relative-path of output csv)
        return path_file_output

    except Exception as e:
        raise CeleryTaskError('type: ' + str(type(e)) + "\n" + "message: " + str(e))

