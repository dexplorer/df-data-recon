from metadata import dataset as ds
from metadata import data_source as dsrc
from metadata import dr_expectation as de
from metadata import dataset_dr_rule as dr
from app_calendar import eff_date as ed
from utils import csv_io as ufc
from utils import spark_io as ufs
from utils import aws_s3_io as ufas
from config.settings import ConfigParms as sc
from dr_app.recon import validater as rb

import logging
import pandas as pd


def apply_dr_rules(dataset_id: str, cycle_date: str) -> list:
    # Simulate getting the cycle date from API
    # Run this from the parent app
    if not cycle_date:
        cycle_date = ed.get_cur_cycle_date()

    dataset = ds.get_dataset_from_json(dataset_id=dataset_id)

    # Simulate getting the data source metadata from API
    data_source = dsrc.get_data_source_from_json(data_source_id=dataset.data_source_id)

    # Simulate getting all data reconciliation rules from API
    logging.info("Get all data reconciliation rules")
    dr_rules = dr.get_all_dr_rules_from_json()

    # Get data reconciliation rules defined for the dataset
    logging.info("Get all data reconciliation rules associated with the dataset")
    dr_rules_for_dataset = dr.get_dr_rules_by_dataset_id(dataset.dataset_id, dr_rules)

    # Get current effective date
    cur_eff_date = ed.get_cur_eff_date(
        schedule_id=dataset.schedule_id, cycle_date=cycle_date
    )
    cur_eff_date_yyyymmdd = ed.fmt_date_str_as_yyyymmdd(cur_eff_date)

    src_data_records = []
    if dataset.dataset_type == ds.DatasetType.LOCAL_DELIM_FILE:
        # Read the source data file
        src_file_path = sc.resolve_app_path(
            dataset.resolve_file_path(
                date_str=cur_eff_date_yyyymmdd,
                data_source_user=data_source.data_source_user,
            )
        )
        logging.info("Reading the file %s", src_file_path)
        src_data_records = ufc.uf_read_delim_file_to_list_of_dict(
            file_path=src_file_path
        )

    elif dataset.dataset_type == ds.DatasetType.SPARK_TABLE:
        # Read the spark table
        qual_target_table_name = dataset.get_qualified_table_name()
        logging.info("Reading the spark table %s", qual_target_table_name)
        src_data_records = ufs.read_spark_table_into_list_of_dict(
            qual_target_table_name=qual_target_table_name,
            cur_eff_date=cur_eff_date,
            warehouse_path=sc.hive_warehouse_path,
        )

    elif dataset.dataset_type == ds.DatasetType.AWS_S3_DELIM_FILE:
        # Read the source data file
        src_file_uri = sc.resolve_app_path(
            dataset.resolve_file_uri(
                date_str=cur_eff_date_yyyymmdd,
                data_source_user=data_source.data_source_user,
            )
        )
        logging.info("Reading the file %s", src_file_uri)
        src_data_records = ufas.uf_read_delim_file_to_list_of_dict(
            s3_obj_uri=src_file_uri, s3_region=sc.s3_region
        )

    df_src = pd.DataFrame.from_records(src_data_records)

    src_recon_data_records = []
    if dataset.dataset_type == ds.DatasetType.LOCAL_DELIM_FILE:
        # Read the source recon data file
        src_recon_file_path = sc.resolve_app_path(
            dataset.resolve_recon_file_path(
                date_str=cur_eff_date_yyyymmdd,
                data_source_user=data_source.data_source_user,
            )
        )
        logging.info("Reading the file %s", src_recon_file_path)
        src_recon_data_records = ufc.uf_read_delim_file_to_list_of_dict(
            file_path=src_recon_file_path, delim=dataset.recon_file_delim
        )
    elif dataset.dataset_type == ds.DatasetType.AWS_S3_DELIM_FILE:
        # Read the source recon data file
        src_recon_file_uri = sc.resolve_app_path(
            dataset.resolve_recon_file_uri(
                date_str=cur_eff_date_yyyymmdd,
                data_source_user=data_source.data_source_user,
            )
        )
        logging.info("Reading the file %s", src_recon_file_uri)
        src_recon_data_records = ufas.uf_read_delim_file_to_list_of_dict(
            s3_obj_uri=src_recon_file_uri,
            s3_region=sc.s3_region,
            delim=dataset.recon_file_delim,
        )

    df_recon = pd.DataFrame.from_records(src_recon_data_records)

    batch = rb.DRBatch(df_src, df_recon)

    # Apply the data reconciliation rules on the dataset
    logging.info("Apply data reconciliation rules on the dataset")
    dr_check_results = []
    for dr_rule in dr_rules_for_dataset:
        dr_expectation = de.DRExpectation.from_json(exp_id=dr_rule.exp_id)

        # Assign the GE function name to a string
        func_name = dr_expectation.ge_method
        # Get the function defined in the DR batch object
        gen_func = getattr(batch, func_name)
        # Pass the keyword arguments to the function
        expectation = gen_func(**dr_rule.kwargs)

        if expectation:
            # Run the validation
            # Output the results object as dict
            validation_results = vars(batch.run_validation(expectation))

            dr_check_result = fmt_dr_check_result(
                rule_id=dr_rule.rule_id,
                exp_name=dr_expectation.exp_name,
                dr_check_output=validation_results,
            )
            dr_check_results.append(dr_check_result)

    return dr_check_results


def fmt_dr_check_result(rule_id, exp_name, dr_check_output) -> dict:
    if dr_check_output["success"]:
        dr_check_status = "Pass"
    else:
        dr_check_status = "Fail"
    dr_check_expected_value = dr_check_output["expected_value"]
    dr_check_actual_value = dr_check_output["actual_value"]

    dr_check_result = {
        "rule_id": rule_id,
        "result": dr_check_status,
        "expectation": exp_name,
        "expected": dr_check_expected_value,
        "actual": dr_check_actual_value,
    }

    return dr_check_result
