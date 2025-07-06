# from dataclasses import dataclass
import logging

import pandas as pd


# @dataclass
class DRValidationResult:
    success: bool
    expected_value: int | float | list
    actual_value: int | float | list

    def __init__(
        self, success: bool, expected_value: int | float, actual_value: int | float
    ):
        self.success = success
        self.expected_value = expected_value
        self.actual_value = actual_value


class DRBatch:
    df_src: pd.DataFrame
    df_recon: pd.DataFrame
    dummy_column: str = "all"

    def __init__(self, df_src: pd.DataFrame, df_recon: pd.DataFrame):
        self.df_src = df_src
        self.df_recon = df_recon
        # Add a dummy column to source dataframe.
        # This will be used to group all rows as 1 group.

        self.df_src[self.dummy_column] = "all"

    def run_validation(self, expectation) -> DRValidationResult:

        # Invoke the recon function
        # expectation points to the recon function with relevant arguments
        expected_value, actual_value = expectation

        status = False
        if str(actual_value) == str(expected_value):
            status = True

        result = DRValidationResult(
            success=status, expected_value=expected_value, actual_value=actual_value
        )

        return result

    def count(self, column: str, group_by_column_names: list[str]):
        logging.info("Calculating the measure 'count'")
        ds = -1

        if isinstance(self.df_src, pd.DataFrame):
            if column in self.df_src.columns:
                if check_if_columns_in_df(
                    df=self.df_src, columns=group_by_column_names
                ):
                    ds = self.df_src.groupby(group_by_column_names)[column].count()
                else:
                    # Group by all records if the given column is not in the dataframe
                    # ds = self.df_src.groupby(lambda x: True)[column].count()
                    ds = self.df_src.groupby(self.dummy_column)[column].count()

        mask = (self.df_recon["measure"] == "count") & (
            self.df_recon["column"] == column
        )
        expected_value = {
            "group_by_column_values": self.df_recon[mask][
                "group_by_column_values"
            ].to_list(),
            "measure_value": self.df_recon[mask]["measure_value"]
            .apply(pd.to_numeric, errors="coerce")
            .to_list(),
        }
        actual_value = {
            "group_by_column_values": ds.index.to_list(),
            "measure_value": ds.fillna(0).tolist(),
        }

        return expected_value, actual_value

    def distinct(self, column: str, group_by_column_names: list[str]):
        logging.info("Calculating the measure 'distinct'")
        ds = -1

        if isinstance(self.df_src, pd.DataFrame):
            if column in self.df_src.columns:
                if check_if_columns_in_df(
                    df=self.df_src, columns=group_by_column_names
                ):
                    ds = self.df_src.groupby(group_by_column_names)[column].nunique(
                        dropna=False
                    )
                else:
                    # Group by all records if the given column is not in the dataframe
                    ds = self.df_src.groupby(self.dummy_column)[column].nunique(
                        dropna=False
                    )

        mask = (self.df_recon["measure"] == "distinct") & (
            self.df_recon["column"] == column
        )
        expected_value = {
            "group_by_column_values": self.df_recon[mask][
                "group_by_column_values"
            ].to_list(),
            "measure_value": self.df_recon[mask]["measure_value"]
            .apply(pd.to_numeric, errors="coerce")
            .to_list(),
        }
        actual_value = {
            "group_by_column_values": ds.index.to_list(),
            "measure_value": ds.fillna(0).tolist(),
        }

        return expected_value, actual_value

    def median(self, column: str):
        logging.info("Calculating the measure 'median'")
        median_value = -1

        if isinstance(self.df_src, pd.DataFrame):
            if column in self.df_src.columns:
                median_value = self.df_src.groupby(self.dummy_column)[column].median()

        mask = (self.df_recon["measure"] == "median") & (
            self.df_recon["column"] == column
        )
        expected_value = {
            "group_by_column_values": self.df_recon[mask][
                "group_by_column_values"
            ].to_list(),
            "measure_value": self.df_recon[mask]["measure_value"].to_list(),
        }
        actual_value = {
            "group_by_column_values": ["all"],
            "measure_value": median_value,
        }

        return expected_value, actual_value

    def count_median(self, column: str):
        logging.info("Calculating the measure 'count_median'")
        median_value = -1

        if isinstance(self.df_src, pd.DataFrame):
            if column in self.df_src.columns:
                # Get the counts of unique values
                count_series = self.df_src.groupby(self.dummy_column)[
                    column
                ].value_counts(sort=True, ascending=False, dropna=True)
                # print(type(count_series))
                # print(count_series)
                # print(count_series.index)
                median_value = count_series.index[len(count_series) // 2]
                # print(median_value)
                # print(type(median_value))

        mask = (self.df_recon["measure"] == "count_median") & (
            self.df_recon["column"] == column
        )
        expected_value = {
            "group_by_column_values": self.df_recon[mask][
                "group_by_column_values"
            ].to_list(),
            "measure_value": self.df_recon[mask]["measure_value"].to_list(),
        }
        actual_value = {
            "group_by_column_values": [median_value[0]],
            "measure_value": [median_value[1]],
        }

        return expected_value, actual_value

    def sum(self, column: str, group_by_column_names: list[str]):
        logging.info("Calculating the measure 'sum'")
        # ds = -1

        ds = pd.Series(dtype=float)
        if isinstance(self.df_src, pd.DataFrame):
            if column in self.df_src.columns:
                if check_if_columns_in_df(
                    df=self.df_src, columns=group_by_column_names
                ):
                    # ds = self.df_src.groupby(group_by_column_names)[column].sum()
                    ds = self.df_src.groupby(group_by_column_names)[column].apply(
                        lambda x: x.astype(float).sum()
                    )
                else:
                    # Group by all records if the given column is not in the dataframe
                    # ds = self.df_src[column].sum()
                    # ds = self.df_src[column].apply(lambda x : x.astype(float).sum())
                    # ds = self.df_src.groupby(lambda x: True)[column].apply(lambda x : x.astype(float).sum())
                    ds = self.df_src.groupby(self.dummy_column)[column].apply(
                        lambda x: x.astype(float).sum()
                    )
                # print(type(ds))
                # print(ds)

        mask = (self.df_recon["measure"] == "sum") & (self.df_recon["column"] == column)
        expected_value = {
            "group_by_column_values": self.df_recon[mask][
                "group_by_column_values"
            ].to_list(),
            "measure_value": self.df_recon[mask]["measure_value"]
            .apply(pd.to_numeric, errors="coerce")
            .to_list(),
        }
        actual_value = {
            "group_by_column_values": ds.index.to_list(),
            # "group_by_column_values": list(zip(dfg.index)),
            "measure_value": ds.fillna(0)
            .apply(pd.to_numeric, errors="coerce")
            .tolist(),
        }

        return expected_value, actual_value


def check_if_columns_in_df(df: pd.DataFrame, columns: list[str]) -> bool:
    """
    Check if the list of columns are in the dataframe.
    """
    if set(columns).issubset(set(df.columns)):
        return True
    else:
        return False
