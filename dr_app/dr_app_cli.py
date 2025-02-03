import logging
import os

import click
from dr_app import settings as sc
from dr_app import dr_app_core as drc
from utils import logger as ufl


@click.command()
# @click.argument('dataset_id', required=1)
@click.option(
    "--dataset_id", type=str, default="dev", help="Source dataset id", required=True
)
@click.option("--env", type=str, default="dev", help="Environment")
@click.option("--cycle_date", type=str, default="", help="Cycle date")
def apply_rules(dataset_id: str, env: str, cycle_date: str):
    """
    Apply data reconciliation rules for the dataset.
    """

    cfg = sc.load_config(env)
    sc.set_config(cfg)

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    ufl.config_logger(log_file_path_name=f"{sc.log_file_path}/{script_name}.log")
    logging.info("Configs are set")

    logging.info(
        "Start applying data reconciliation rules on the dataset %s", dataset_id
    )
    dr_check_results = drc.apply_dr_rules(dataset_id=dataset_id, cycle_date=cycle_date)

    logging.info(
        "Finished applying data reconciliation rules on the dataset %s", dataset_id
    )

    logging.info("Data reconciliation check results for dataset %s", dataset_id)
    logging.info(dr_check_results)

    return {"results": dr_check_results}


# Create command group
@click.group()
def cli():
    pass


# Add sub command to group
cli.add_command(apply_rules)


def main():
    cli()


if __name__ == "__main__":
    main()
