# df-data-recon

This application reconciles the source data with the reconciliation control measures received from the source. Reconciliation controls (columns, aggregates) can be configured.

Application can be invoked using CLI or REST API end points. This allows the app to be integrated into a larger data ingestion / distribution framework.

### Define the environment variables

Create a .env file with the following variables.

```
ENV=dev
APP_ROOT_DIR=/workspaces/df-data-recon
NAS_ROOT_DIR=/workspaces/nas
```

### Install

- **Install via Makefile and pip**:
  ```sh
    make install
  ```

### Usage Examples

- **Apply data reconciliation rules on a dataset via CLI**:
  ```sh
    dr-app-cli apply-rules --dataset_id "dataset_2"
  ```

- **Apply data reconciliation rules on a dataset via CLI with cycle date override**:
  ```sh
    dr-app-cli apply-rules --dataset_id "dataset_2" --cycle_date "2024-12-24"
  ```

- **Apply data reconciliation rules on a dataset via API**:
  ##### Start the API server
  ```sh
    dr-app-api
  ```
  ##### Invoke the API endpoint
  ```sh
    https://<host name with port number>/apply-rules/?dataset_id=<value>
    https://<host name with port number>/apply-rules/?dataset_id=<value>&cycle_date=<value>

    /apply-rules/?dataset_id=dataset_2
    /apply-rules/?dataset_id=dataset_2&cycle_date=2024-12-26
  ```
  ##### Invoke the API from Swagger Docs interface
  ```sh
    https://<host name with port number>/docs

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
2024-12-26|"count"|"account_id"|"all"|"all"|9
2024-12-26|"count_median"|"asset_id"|"all"|"all"|"2"
2024-12-26|"sum"|"asset_value"|"asset_id"|"1"|-65000.0
2024-12-26|"sum"|"asset_value"|"asset_id"|"2"|-5000.0
2024-12-26|"distinct"|"account_id"|"asset_id"|"1"|7
2024-12-26|"distinct"|"account_id"|"asset_id"|"2"|2

```

### API Data (simulated)
These are metadata that would be captured via the data reconciliation application UI and stored in a database.

  ##### datasets 
```
{
    "datasets": [
      {
        "dataset_id": "dataset_2",
        "dataset_kind": "local delim file",
        "catalog_ind": true,
        "file_delim": ",",
        "file_path": "APP_DATA_IN_DIR/acct_positions_yyyymmdd.csv",
        "schedule_id": "2",
        "recon_file_delim": "|", 
        "recon_file_path": "APP_DATA_IN_DIR/acct_positions_yyyymmdd.recon" 
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
        "group_by_column_names": [
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
        "group_by_column_names": [
          "asset_id"
        ] 
      },
      {
        "rule_id": "4",
        "dataset_id": "2",
        "exp_id": "4",
        "rule_fail_action": "abort",
        "column": "account_id", 
        "group_by_column_names": [
          "asset_id"
        ] 
      }
    ]
  }
    
```

### Sample Output 

```
Data reconciliation check results for dataset dataset_2

{
  "results": [
    {
      "rule_id": "1",
      "result": "Pass",
      "expectation": "ExpectColumnValuesCountToMatch",
      "expected": {
        "group_by_column_values": [
          "all"
        ],
        "measure_value": [
          9
        ]
      },
      "actual": {
        "group_by_column_values": [
          "all"
        ],
        "measure_value": [
          9
        ]
      }
    },
    {
      "rule_id": "2",
      "result": "Pass",
      "expectation": "ExpectColumnValueCountsMedianToMatch",
      "expected": {
        "group_by_column_values": [
          "all"
        ],
        "measure_value": [
          "2"
        ]
      },
      "actual": {
        "group_by_column_values": [
          "all"
        ],
        "measure_value": [
          "2"
        ]
      }
    },
    {
      "rule_id": "3",
      "result": "Pass",
      "expectation": "ExpectColumnValuesSumToMatch",
      "expected": {
        "group_by_column_values": [
          "1",
          "2"
        ],
        "measure_value": [
          -65000.0,
          -5000.0
        ]
      },
      "actual": {
        "group_by_column_values": [
          "1",
          "2"
        ],
        "measure_value": [
          -65000.0,
          -5000.0
        ]
      }
    },
    {
      "rule_id": "4",
      "result": "Pass",
      "expectation": "ExpectColumnUniqueValuesCountToMatch",
      "expected": {
        "group_by_column_values": [
          "1",
          "2"
        ],
        "measure_value": [
          7,
          2
        ]
      },
      "actual": {
        "group_by_column_values": [
          "1",
          "2"
        ],
        "measure_value": [
          7,
          2
        ]
      }
    }
  ]
}

```
