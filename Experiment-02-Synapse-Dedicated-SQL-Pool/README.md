# Experiment 2 – Azure Synapse Dedicated SQL Pool

## Aim

To create an Azure Synapse Dedicated SQL Pool and load structured data for analytical processing.

## Objective

* Create an Azure Synapse Analytics workspace.
* Create a Dedicated SQL Pool.
* Connect to the Dedicated SQL Pool using Synapse Studio.
* Create a relational table.
* Load structured data.
* Execute SQL queries.
* Analyze the loaded data.

## Architecture

```text
Azure Storage
      |
      v
Azure Synapse Analytics
      |
      v
Dedicated SQL Pool
      |
      v
SQL Tables
      |
      v
Analytical Queries
```

## Services Used

* Azure Synapse Analytics
* Synapse Dedicated SQL Pool
* Azure Storage
* Synapse Studio
* SQL

## Procedure

### Step 1 – Create Synapse Workspace

1. Open Azure Portal.
2. Search for Azure Synapse Analytics.
3. Create a Synapse workspace.
4. Configure the required subscription and resource group.
5. Configure the ADLS Gen2 storage account.
6. Complete the deployment.

### Step 2 – Create Dedicated SQL Pool

1. Open Synapse Studio.
2. Select **Manage**.
3. Select **SQL pools**.
4. Click **New**.
5. Enter the SQL Pool name.
6. Select the required performance level.
7. Create the Dedicated SQL Pool.

### Step 3 – Connect to the SQL Pool

1. Open **Develop**.
2. Create a new SQL Script.
3. Select the Dedicated SQL Pool.
4. Verify the connection.

### Step 4 – Create a Table

Example:

```sql
CREATE TABLE Employee
(
    EmployeeID INT,
    EmployeeName VARCHAR(100),
    Department VARCHAR(100),
    Salary INT
)
WITH
(
    DISTRIBUTION = ROUND_ROBIN,
    HEAP
);
```

### Step 5 – Load Data

Load the structured data into the table using an appropriate Synapse loading method such as `COPY INTO`.

Example:

```sql
COPY INTO Employee
FROM 'https://<storage-account>.blob.core.windows.net/<container>/employee.csv'
WITH
(
    FILE_TYPE = 'CSV',
    FIELDTERMINATOR = ',',
    FIRSTROW = 2
);
```

### Step 6 – Verify the Data

```sql
SELECT *
FROM Employee;
```

### Step 7 – Analyze the Data

```sql
SELECT
    Department,
    COUNT(*) AS EmployeeCount,
    AVG(Salary) AS AverageSalary
FROM Employee
GROUP BY Department;
```

## Result

The Azure Synapse Dedicated SQL Pool was successfully created and structured data was loaded into a relational table for analytical processing.

## Key Learning

This experiment demonstrates the use of a Dedicated SQL Pool as a cloud data warehouse for structured data storage and analytical workloads.
