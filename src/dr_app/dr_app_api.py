import os
import argparse
import logging

from config.settings import ConfigParms as sc
from config import settings as scg
from dr_app import dr_app_core as drc
from utils import logger as ufl

from fastapi import FastAPI
import uvicorn

#
APP_ROOT_DIR = "/workspaces/df-data-recon"

app = FastAPI()


@app.get("/")
async def root():
    """
    Default route

    Args:
        none

    Returns:
        A default message.
    """

    return {"message": "Data Reconciliation Validation App"}


@app.get("/apply-rules/")
async def apply_rules(dataset_id: str, cycle_date: str = ""):
    """
    Apply data reconciliation rules for the dataset.


    Args:
        dataset_id: Id of the dataset.
        cycle_date: Cycle date

    Returns:
        Results from the data reconciliation checks.
    """

    logging.info(
        "Start applying data reconciliation rules on the dataset %s", dataset_id
    )
    dr_check_results = drc.apply_dr_rules(dataset_id=dataset_id, cycle_date=cycle_date)
    logging.info(
        "Finished applying data reconciliation rules on the dataset %s", dataset_id
    )

    return {"results": dr_check_results}


def main():
    parser = argparse.ArgumentParser(description="Data Reconciliation Application")
    parser.add_argument(
        "-e", "--env", help="Environment", const="dev", nargs="?", default="dev"
    )

    # Get the arguments
    args = vars(parser.parse_args())
    logging.info(args)
    env = args["env"]

    scg.APP_ROOT_DIR = APP_ROOT_DIR
    sc.load_config(env=env)

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    ufl.config_logger(log_file_path_name=f"{sc.log_file_path}/{script_name}.log")
    logging.info("Configs are set")

    logging.info("Starting the API service")

    uvicorn.run(
        app,
        port=8080,
        host="0.0.0.0",
        log_config=f"{sc.cfg_file_path}/api_log.ini",
    )


if __name__ == "__main__":
    main()
