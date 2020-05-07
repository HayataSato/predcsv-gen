# -- Standard --
import io
import os
# -- 3rd Party --
from django import forms
from django.conf import settings
from django_select2 import forms as s2forms
import pandas as pd
# -- local --
# from .models import oo


class PredForm(forms.Form):
    """ The form to predict with model and csv.

    Errors:
        ValidationError: This error will occurr when the input-csv does not have csv extension.
    """
    def __init__(self, *args, **kwargs):
        super(PredForm, self).__init__(*args, **kwargs)
        # -- Define constructs --
        # CHOICES: Options for model-input.
        # VALID_EXTENSIONS: Allowed Input Extensions for file-input
        self.CHOICES = [
                ("XGBoost", "XGBoost"),
                ("RandomForest", "RandomForest"),
             ]
        self.VALID_EXTENSIONS = ['.csv']
        # -- Set field values --
        self.fields['model'].choices = self.CHOICES

    # ----------
    # Inputs
    # ----------
    model = forms.MultipleChoiceField(choices=[], widget=s2forms.Select2MultipleWidget({"multiple": True}), required=True)
    file = forms.FileField(required=True)

    # ----------
    # Methods
    # ----------
    def clean_file(self):
        """Check the file structure sent from the file-input form."""
        file_input = self.cleaned_data["file"]  # validated data
        extension = os.path.splitext(file_input.name)[1]  # 拡張子
        if not extension.lower() in self.VALID_EXTENSIONS:
            raise forms.ValidationError(
                message=f"Please upload the file with one of the following extensions-list. \n {self.VALID_EXTENSIONS}.")

    @staticmethod
    def save(file_input):
        """Save file-input to MEDIA_ROOT as "{input-file-mame}.csv".

        Args:
            file_input (UploadedFile(csv)): The UploadedFile object that is posted from the csv-input form.

        """
        # Open new csv file with witer & binary mode
        path_saved_csv = os.path.join(settings.MEDIA_ROOT, "csv/input", file_input.name)
        with open(path_saved_csv, 'wb') as f:
            for chunk in file_input.chunks():
                f.write(chunk)
        return path_saved_csv