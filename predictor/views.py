# -- Standard --
import csv
import re
import os
# -- 3rd Party --
from celery.result import AsyncResult
from django_celery_results.models import TaskResult
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render
# -- local --
from predcsv_gen.tasks import generator, CeleryTaskError
from predictor.forms import PredForm


def index(request):
    """The Handler function to render index.html
        Divide rendering top-page following the status of celery task.
    """
    # POST
    if "prediction" in request.POST:
        form = PredForm(request.POST, request.FILES)
        model = request.POST.getlist("model")
        name_file_input = request.FILES["file"].name
        if form.is_valid():
            # CSVの保存 ("settings.CSV_DIR/input")
            path_saved_csv = form.save(file_input=request.FILES["file"])
            # 非同期タスクの実行開始
            task_id = generator.delay(path_saved_csv)
            task_status = {"state": "PENDING"}  # AsyncResult(task_id)は行わずに1ターン目は強制でリロード画面に回す
            message = "PROCESSING"
            # task_statusに応じて画面表示と自動リロードの可否を分岐
            #                   &
            # result.messageで<h5>タグの非同期タスクのステータスを表示
            return render(request, "predictor/index.html",
                          {"form": PredForm(), "task_status": task_status, "task_id": task_id,
                           "results": {"message": message, "model": model, "file": name_file_input, }})
        else:
            # ERROR at validation (unknown exception or model)
            return render(request, "predictor/index.html",
                          {"form": PredForm(), "error_message": form.errors,
                           "results": {"message": "ERROR", "model": model, "file": name_file_input, }})

    if "reload" in request.POST:
        task_id = request.POST.get("task_id")
        model = request.POST.getlist("model")
        name_file_input = request.POST.get("file")
        task_status = AsyncResult(task_id)
        message = "PROCESSING"
        task_result = ""
        try:
            task_result = task_status.get(timeout=1)
            message = "SUCCESS"  # task_status.getのエラーを見越してmessage更新はgetの後に記述
        except (ValidationError, CeleryTaskError) as e:
            task_result = e.message
            message = "ERROR"
        finally:
            return render(request, "predictor/index.html", {
                "form": PredForm(), "task_status": task_status,
                "results": {"message": message, "model": model, "file": name_file_input, "task_result": task_result}
            })

    if "download" in request.POST:
        path_file_output = request.POST["path_file_output"]
        with open(path_file_output, 'rb') as f:
            response = HttpResponse(f.read(), content_type="text/csv")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(path_file_output)
            return response

    # GET
    return render(request, "predictor/index.html", {
        "form": PredForm(),
        "results": {"message": "WAITING"},
    })

