from metadata import dataset as ds
from metadata import dr_expectation as de
from metadata import dr_rule as dr

from dr_app import settings as sc

import logging


def apply_dr_rules(dataset_id) -> list:

    # Simulate getting the dataset metadata from API
    logging.info("Get dataset metadata")
    dataset = ds.LocalDelimFileDataset.from_json(dataset_id)

    # Simulate getting all DQ rules from API
    logging.info("Get all DQ rules")
    dr_rules = dr.get_all_dr_rules_from_json()

    # Get DQ rules defined for the dataset
    logging.info("Get all DQ rules associated with the dataset")
    dr_rules_for_dataset = dr.get_dr_rules_by_dataset_id(dataset.dataset_id, dr_rules)

    # Define the GE context
    context = gx.get_context()

    # Use the `pandas_default` Data Source to retrieve a Batch of sample Data from a data file:
    src_file_path = sc.resolve_app_path(dataset.file_path)
    batch = context.data_sources.pandas_default.read_csv(src_file_path)

    # Apply the DQ rules on the dataset
    logging.info("Apply DQ rules on the dataset")
    dr_check_results = []
    for dr_rule in dr_rules_for_dataset:
        dr_expectation = de.DQExpectation.from_json(exp_id=dr_rule.exp_id)

        # Assign the GE function name to a string
        gen_func_str = f"gen_func = gx.expectations.{dr_expectation.exp_name}"
        # Get local variables
        _locals = locals()
        # Execute the function name assignment, this mutates the local namespace
        exec(gen_func_str, globals(), _locals)
        # Grab the newly defined function name from the local namespace dictionary and assign it to generic function variable
        gen_func = _locals["gen_func"]
        # Pass function specific keyword arguments to the generic function
        expectation = gen_func(**dr_rule.kwargs)

        if expectation:
            # Test the Expectation:
            validation_results = batch.validate(expectation)

            # Evaluate the Validation Results:
            # print(validation_results)

            dr_check_result = fmt_dr_check_result(
                rule_id=dr_rule.rule_id, dr_check_output=validation_results
            )
            dr_check_results.append(dr_check_result)

    return dr_check_results


def fmt_dr_check_result(rule_id, dr_check_output) -> dict:
    dr_check_status = dr_check_output["success"]

    if dr_check_status:
        dr_check_result = {"rule_id": rule_id, "result": dr_check_status}
    else:
        dr_check_result = {"rule_id": rule_id, "result": False}

    return dr_check_result
