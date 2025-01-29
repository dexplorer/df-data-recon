# df-data-recon

### Install

- **Install via setuptools**:
  ```sh
    python setup.py install
  ```


### Usage Examples

- **Apply data reconciliation rules on a dataset via CLI**:
  ```sh
    dr_app apply-rules --dataset_id "2" --env "dev"
  ```

- **Apply data reconciliation rules on a dataset via API**:
  ##### Start the API server
  ```sh
    python dr_app/dr_app_api.py
  ```
  ##### Invoke the API endpoint
  ```sh
    https://<host name with port number>/apply-rules/{dataset_id}
    https://<host name with port number>/apply-rules/2
  ```
  ##### Invoke the API from Swagger Docs interface
  ```sh
    https://<host name with port number>/docs

    /apply-rules/{dataset_id}
    /apply-rules/2
  ```

### Sample Input

##### Dataset (acct_positions_20241226.csv)
```
effective_date,account_id,asset_id,asset_value
2024-12-26,ACC1,1,-35000
2024-12-26,ACC1,2,-15000
2024-12-26,ACC2,2,10000
2024-12-26,ACC4,1,-5000
2024-12-26,ACC5,1,-5000
2024-12-26,ACC6,1,-5000
2024-12-26,ACC7,1,-5000
2024-12-26,ACC8,1,-5000
2024-12-26,ACC9,1,-5000
```

##### Reconciliation Dataset (acct_positions_20241226.recon)
```
"effective_date"|"measure"|"column"|"group_by_column_names"|"group_by_column_values"|"measure_value"
2024-12-26|"count"|"account_id"|["all"]|["all"]|9
2024-12-26|"count_median"|["asset_id"]|["all"]|["all"]|1
2024-12-26|"sum"|"asset_value"|["asset_id"]|["1"]|-65000.0
2024-12-26|"sum"|"asset_value"|["asset_id"]|["2"]|-5000.0
2024-12-26|"distinct"|"account_id"|["asset_id"]|["1"]|7
2024-12-26|"distinct"|"account_id"|["asset_id"]|["2"]|2

```

### API Data (simulated)
These are metadata that would be captured via the data reconciliation application UI and stored in a database.

  ##### datasets 
```
{
    "datasets": [
      {
        "dataset_id": "2",
        "catalog_ind": true,
        "file_delim": ",",
        "file_path": "APP_ROOT_DIR/data/acct_positions_yyyymmdd.csv",
        "schedule_id": "2",
        "dq_rule_ids": [], 
        "model_parameters": {
          "features": [
            {
              "column": "account_id",
              "variable_type": "category",
              "variable_sub_type": "nominal",
              "encoding": "frequency"
            },
            {
              "column": "asset_id",
              "variable_type": "category",
              "variable_sub_type": "nominal",
              "encoding": "one hot"
            },
            {
              "column": "asset_value",
              "variable_type": "numeric",
              "variable_sub_type": "float",
              "encoding": "numeric"
            }
          ],
          "hist_data_snapshots": [
            {
              "snapshot": "t-1d"
            },
            {
              "snapshot": "lme"
            }
          ],
          "sample_size": 10000
        }, 
        "recon_file_delim": "|", 
        "recon_file_path": "APP_ROOT_DIR/data/acct_positions_yyyymmdd.recon" 
      }
    ]
  }
  ```

  ##### dr_expectations 
```
{
    "dr_expectations": [
      {
        "exp_id": "1",
        "exp_name": "ExpectColumnValuesCountToMatch",
        "ge_method": "count"
      },
      {
        "exp_id": "2",
        "exp_name": "ExpectColumnValueCountsMedianToMatch",
        "ge_method": "count_median"
      },
      {
        "exp_id": "3",
        "exp_name": "ExpectColumnValuesSumToMatch",
        "ge_method": "sum"
      },
      {
        "exp_id": "4",
        "exp_name": "ExpectColumnUniqueValuesCountToMatch",
        "ge_method": "distinct"
      }, 
      {
        "exp_id": "5",
        "exp_name": "ExpectColumnValuesMedianToMatch",
        "ge_method": "median"
      }
    ]
  }
```

  ##### dr_rules 
```
{
    "dr_rules": [
      {
        "rule_id": "1",
        "dataset_id": "2",
        "exp_id": "1",
        "rule_fail_action": "abort",
        "column": "account_id", 
        "group_by_columns": [
          "all"
        ] 
      },
      {
        "rule_id": "2",
        "dataset_id": "2",
        "exp_id": "2",
        "rule_fail_action": "abort",
        "column": "asset_id" 
      },
      {
        "rule_id": "3",
        "dataset_id": "2",
        "exp_id": "3",
        "rule_fail_action": "abort",
        "column": "asset_value", 
        "group_by_columns": [
          "asset_id"
        ] 
      },
      {
        "rule_id": "4",
        "dataset_id": "2",
        "exp_id": "4",
        "rule_fail_action": "abort",
        "column": "account_id", 
        "group_by_columns": [
          "account_id"
        ] 
      }
    ]
  }
    
```

### Sample Output 

```
Data reconciliation check results for dataset 2
[
  {'rule_id': '1', 'result': True}, 
  {'rule_id': '2', 'result': True}, 
  {'rule_id': '3', 'result': False}
]
```
