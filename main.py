import logging
import os
from typing import Optional

import urllib3
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

# from src.models.fun_model_training import fun_load_model
# from src.models.fun_pred_eval import fun_1vsRest_predict_proba
from typing import Dict, List, Optional
from realtime_data_drift.realtime_data_drift.data_drift import (
    getDriftMonitoringService,
    MonitoringService,
)
from starlette_exporter import PrometheusMiddleware, handle_metrics
import pandas as pd
import os.path
import yaml

logger = logging.getLogger()
logger.setLevel(logging.INFO)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()
app.add_middleware(
    PrometheusMiddleware,
    app_name="sample_fast_api",
    prefix="sample_fast_api",
)
app.add_route("/metrics", handle_metrics)


SERVICE: Optional[MonitoringService] = None


@app.on_event("startup")
async def startup_event():
    # pylint: disable=global-statement
    global SERVICE
    config_file_name = "data-drift-config.yaml"
    # try to find a config file, it should be generated via a data preparation script
    if not os.path.exists(config_file_name):
        exit(
            "Cannot find config file for the metrics service. Try to check README.md for setup instructions."
        )

    with open(config_file_name, "rb") as config_file:
        config = yaml.safe_load(config_file)

    SERVICE = getDriftMonitoringService(config)


@app.get("/healthz")
def healthz():
    return {}


class PersonData(BaseModel):
    person_id: str
    job_title: Optional[str]
    industry: Optional[str]
    occupation: Optional[str]
    age: Optional[int]


# Think of other 4xx responses that can happen
@app.post("/api/v1/predict")
async def predict_v1(
    data: PersonData,
    background_tasks: BackgroundTasks,
):
    print(data.dict())
    features = pd.DataFrame(data.dict(), index=[0])
    if SERVICE is None:
        print("service is not found")
    else:
        # drift will be computed when there is 30 rows of data as window size is 30
        background_tasks.add_task(SERVICE.iterate, features.drop("person_id", axis=1))

    response = {"dummy_response": "true"}

    return response
