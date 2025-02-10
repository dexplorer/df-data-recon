from metadata import dataset as ds
from metadata import dr_expectation as de
from metadata import dr_rule as dr
from app_calendar import eff_date as ed
from utils import csv_io as ufc
from utils import spark_io as ufs

from config.settings import ConfigParms as sc
from dr_app.recon import validater as rb

import logging
import pandas as pd

# import inspect
# from funcsigs import signature


def apply_dr_rules(dataset_id: str, cycle_date: str) -> list:
    # Simulate getting the cycle date from API
    # Run this from the parent app
    if not cycle_date:
        cycle_date = ed.get_cur_cycle_date()

    # Simulate getting the dataset metadata from API
    # logging.info("Get base dataset metadata")
    # dataset = ds.Dataset.from_json(dataset_id)

    # if dataset.kind == ds.DatasetKind.LOCAL_DELIM_FILE:
    #     dataset = ds.LocalDelimFileDataset.from_json(dataset_id)
    # elif dataset.kind == ds.DatasetKind.SPARK_TABLE:
    #     dataset = ds.SparkTableDataset.from_json(dataset_id)

    dataset = ds.get_dataset_from_json(dataset_id=dataset_id)

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
    if dataset.kind == ds.DatasetKind.LOCAL_DELIM_FILE:
        # Read the source data file
        src_file_path = sc.resolve_app_path(
            dataset.resolve_file_path(cur_eff_date_yyyymmdd)
        )
        logging.info("Reading the file %s", src_file_path)
        src_data_records = ufc.uf_read_delim_file_to_list_of_dict(
            file_path=src_file_path
        )

    elif dataset.kind == ds.DatasetKind.SPARK_TABLE:
        # Read the spark table
        qual_target_table_name = dataset.get_qualified_table_name()
        logging.info("Reading the spark table %s", qual_target_table_name)
        src_data_records = ufs.read_spark_table_into_list_of_dict(
            qual_target_table_name=qual_target_table_name,
            cur_eff_date=cur_eff_date,
            warehouse_path=sc.hive_warehouse_path,
        )

    df_src = pd.DataFrame.from_records(src_data_records)
    print(df_src.loc[:0])

    # Read the source recon data file
    src_recon_file_path = sc.resolve_app_path(
        dataset.resolve_recon_file_path(cur_eff_date_yyyymmdd)
    )
    logging.info("Reading the file %s", src_recon_file_path)
    src_recon_file_records = ufc.uf_read_delim_file_to_list_of_dict(
        file_path=src_recon_file_path, delim=dataset.recon_file_delim
    )

    df_recon = pd.DataFrame.from_records(src_recon_file_records)
    print(df_recon.loc[:0])

    batch = rb.DRBatch(df_src, df_recon)

    # Apply the data reconciliation rules on the dataset
    logging.info("Apply data reconciliation rules on the dataset")
    dr_check_results = []
    for dr_rule in dr_rules_for_dataset:
        dr_expectation = de.DRExpectation.from_json(exp_id=dr_rule.exp_id)

        # Assign the GE function name to a string
        gen_func_str = f"gen_func = batch.{dr_expectation.ge_method}"
        # Get local variables
        _locals = locals()
        # Execute the function name assignment, this mutates the local namespace
        exec(gen_func_str, globals(), _locals)
        # Grab the newly defined function name from the local namespace dictionary and assign it to generic function variable
        gen_func = _locals["gen_func"]
        # print(gen_func)
        # print(f"{dr_rule.kwargs}")
        # Pass function specific keyword arguments to the generic function
        expectation = gen_func(**dr_rule.kwargs)
        # print(inspect.getfullargspec(expectation))
        # print(str(expectation))
        # print(str(signature(expectation)))

        if expectation:
            # Test the Expectation
            # Output the results object as dict
            validation_results = vars(batch.run_validation(expectation))

            # Evaluate the Validation Results:
            # print(validation_results)

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
