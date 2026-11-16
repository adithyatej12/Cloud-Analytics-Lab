# Experiment 3 – Query and Analyze Structured and Unstructured Data from ADLS using Azure Synapse

## Aim

To query and analyze structured and unstructured data stored in Azure Data Lake Storage Gen2 using Azure Synapse Analytics.

## Objective

* Configure Azure Data Lake Storage Gen2.
* Store datasets in ADLS Gen2.
* Connect ADLS Gen2 with Azure Synapse.
* Configure a linked service.
* Use Synapse Serverless SQL.
* Query CSV data directly from ADLS.
* Analyze the retrieved data using SQL.

## Architecture

```text
Azure Data Lake Storage Gen2
             |
             v
      Azure Synapse
             |
             v
     Serverless SQL Pool
             |
             v
        OPENROWSET()
             |
             v
       Query Results
```

## Services Used

* Azure Data Lake Storage Gen2
* Azure Synapse Analytics
* Synapse Serverless SQL
* Azure Data Factory
* SQL

## Procedure

### Step 1 – Configure ADLS Gen2

1. Open the Azure Storage Account.
2. Verify that Hierarchical Namespace is enabled.
3. Create the required containers.
4. Create a `raw` container.
5. Upload the CSV dataset.

Example:

```text
raw/
└── Adithya_tej.csv
```

### Step 2 – Configure Azure Data Factory

1. Open Azure Data Factory Studio.
2. Select **Manage**.
3. Open **Linked services**.
4. Select **New**.
5. Select **Azure Data Lake Storage Gen2**.
6. Enter the linked service name:

```text
ls_adithya
```

7. Select the Azure subscription.
8. Select the storage account:

```text
caljainstorage1
```

9. Test the connection.
10. Verify:

```text
Connection successful
```

11. Create the linked service.

### Step 3 – Open Synapse Studio

1. Open the Synapse workspace.
2. Launch Synapse Studio.
3. Open the **Data** section.
4. Select **Linked**.
5. Locate the ADLS Gen2 storage account.
6. Navigate to the `raw` container.
7. Verify the CSV file.

### Step 4 – Create SQL Script

1. Open **Develop**.
2. Select **SQL Script**.
3. Connect to the **Built-in** serverless SQL endpoint.
4. Enter the query.

### Step 5 – Query CSV Data

```sql
SELECT TOP 100 *
FROM OPENROWSET(
    BULK 'https://caljainstorage1.dfs.core.windows.net/raw/Adithya_tej.csv',
    FORMAT = 'CSV',
    PARSER_VERSION = '2.0'
) AS [result];
```

### Step 6 – Analyze the Dataset

The dataset contains fields such as:

```text
PassengerId
Survived
Pclass
Name
Sex
Age
SibSp
```

Example analytical query:

```sql
SELECT
    Sex,
    COUNT(*) AS PassengerCount
FROM OPENROWSET(
    BULK 'https://caljainstorage1.dfs.core.windows.net/raw/Adithya_tej.csv',
    FORMAT = 'CSV',
    PARSER_VERSION = '2.0'
) AS [result]
GROUP BY Sex;
```

Another example:

```sql
SELECT
    Pclass,
    COUNT(*) AS TotalPassengers
FROM OPENROWSET(
    BULK 'https://caljainstorage1.dfs.core.windows.net/raw/Adithya_tej.csv',
    FORMAT = 'CSV',
    PARSER_VERSION = '2.0'
) AS [result]
GROUP BY Pclass;
```

## Troubleshooting

During the experiment, an initial file access error was encountered while querying the CSV file.

The following were verified:

* Storage account name
* Container name
* File name
* File path
* Linked service
* Access permissions

After correcting/verifying the configuration, the SQL query executed successfully and returned the dataset.

## Result

The CSV dataset stored in Azure Data Lake Storage Gen2 was successfully queried and analyzed using Azure Synapse Serverless SQL.

## Key Learning

This experiment demonstrates how Synapse Serverless SQL can query data directly from a data lake without first loading the files into a traditional relational database.

It provides practical experience with cloud data lakes, serverless analytics, SQL querying, storage integration, and data engineering workflows.
