# Evidently Drift Detection For Models Deployed As An API  

To build the package please run  
```
python3 setup.py sdist bdist_wheel
```

## Using it in a FAST API service  

Initialise the monitoring service by running the following script in app startup  

```
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
```

It needs a config file an example of which is shown in fast-api-app/data-drift-config.yaml

```
from fastapi import FastAPI, BackgroundTasks
@app.post("/api/v1/predict")
async def predict_v1(
    data: POSTData,
    background_tasks: BackgroundTasks,
):
features = retrieveFeaturesFromRequest(data.dict())
background_tasks.add_task(SERVICE.iterate, features)
...
#other stuff like model.predict, return response etc
```

To run the app please setup virtual env and run the following

```
uvicorn main:app
```

You can see the metrics by accessing http://127.0.0.1:8000/metrics  

They should appear once you have triggered enough requests to meet the minimum window size

The grafana dashboard is available under dashboards