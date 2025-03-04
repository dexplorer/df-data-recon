import logging
import os

import click
from dotenv import load_dotenv
from config.settings import ConfigParms as sc
from dr_app import dr_app_core as drc
from utils import logger as ufl


# Create command group
@click.group()
def cli():
    pass


@cli.command()
@click.option("--dataset_id", type=str, help="Source dataset id", required=True)
@click.option("--cycle_date", type=str, default="", help="Cycle date")
def apply_rules(dataset_id: str, cycle_date: str):
    """
    Apply data reconciliation rules for the dataset.
    """

    logging.info(
        "Start applying data reconciliation rules on the dataset %s", dataset_id
    )
    dr_check_results = drc.apply_dr_rules(dataset_id=dataset_id, cycle_date=cycle_date)

    logging.info("Data reconciliation check results for dataset %s", dataset_id)
    logging.info(dr_check_results)

    logging.info(
        "Finished applying data reconciliation rules on the dataset %s", dataset_id
    )


def main():
    # Load the environment variables from .env file
    load_dotenv()

    # Fail if env variable is not set
    sc.env = os.environ["ENV"]
    sc.app_root_dir = os.environ["APP_ROOT_DIR"]
    sc.load_config()

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    ufl.config_logger(log_file_path_name=f"{sc.log_file_path}/{script_name}.log")
    logging.info("Configs are set")
    logging.info(os.environ)
    logging.info(sc.config)
    logging.info(vars(sc))

    cli()


if __name__ == "__main__":
    main()
