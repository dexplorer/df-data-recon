from dr_app import settings as sc
from dr_app import dr_app_core as drc
import logging

from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
async def root():
    """
    Default route
    """

    return {"message": "Data Quality Validation App"}


@app.get("/apply-rules/{dataset_id}")
async def apply_rules(dataset_id: str, env: str = "dev"):
    """
    Apply data reconciliation rules for the dataset.
    """

    cfg = sc.load_config(env)
    sc.set_config(cfg)

    logging.info("Configs are set")

    logging.info(
        "Start applying data reconciliation rules on the dataset %s", dataset_id
    )
    dr_check_results = drc.apply_dr_rules(dataset_id=dataset_id)

    logging.info(
        "Finished applying data reconciliation rules on the dataset %s", dataset_id
    )

    return {"results": dr_check_results}


if __name__ == "__main__":
    uvicorn.run(
        app,
        port=8080,
        host="0.0.0.0",
        log_config=f"{sc.APP_ROOT_DIR}/cfg/api_log.ini",
    )
