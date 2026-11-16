# Experiment 1 – Azure Data Factory: On-Premises SQL to Azure Blob Storage

## Aim

To create an Azure Data Factory pipeline to ingest data from an on-premises SQL Server database into Azure Blob Storage.

## Objective

* Connect an on-premises SQL Server database with Azure Data Factory.
* Configure a Self-hosted Integration Runtime.
* Create source and destination linked services.
* Create datasets for the source and destination.
* Create a Copy Data pipeline.
* Transfer data from SQL Server to Azure Blob Storage.
* Monitor and verify the pipeline execution.

## Architecture

```text
On-Premises SQL Server
          |
          | Self-hosted Integration Runtime
          v
   Azure Data Factory
          |
          | Copy Activity
          v
   Azure Blob Storage
```

## Services Used

* Azure Data Factory
* SQL Server
* Self-hosted Integration Runtime
* Azure Blob Storage

## Procedure

### Step 1 – Prepare the On-Premises SQL Database

1. Create or use an existing SQL Server database.
2. Create the required tables.
3. Insert sample records.
4. Verify the data using SQL queries.

### Step 2 – Create Azure Data Factory

1. Open Azure Portal.
2. Search for Azure Data Factory.
3. Create a Data Factory resource.
4. Open Data Factory Studio.

### Step 3 – Configure Self-hosted Integration Runtime

1. Open **Manage** in Data Factory.
2. Select **Integration Runtimes**.
3. Select **New**.
4. Choose **Self-hosted**.
5. Install the Integration Runtime on the machine that can access the SQL Server.
6. Register the Integration Runtime.
7. Verify that its status is running.

### Step 4 – Create SQL Server Linked Service

1. Open **Manage → Linked services**.
2. Select **New**.
3. Select SQL Server.
4. Configure the SQL Server connection.
5. Select the Self-hosted Integration Runtime.
6. Test the connection.
7. Create the linked service.

### Step 5 – Create Azure Blob Storage Linked Service

1. Create a new linked service.
2. Select Azure Blob Storage.
3. Select the required storage account.
4. Configure authentication.
5. Test the connection.
6. Create the linked service.

### Step 6 – Create Datasets

Create:

* SQL Server source dataset
* Azure Blob Storage destination dataset

### Step 7 – Create Copy Data Pipeline

1. Open **Author**.
2. Create a new pipeline.
3. Add a **Copy Data** activity.
4. Select SQL Server as the source.
5. Select Azure Blob Storage as the sink.
6. Configure the required mapping.
7. Validate the pipeline.

### Step 8 – Run the Pipeline

1. Select **Debug** or **Trigger now**.
2. Open **Monitor**.
3. Check the pipeline execution.
4. Verify that the Copy Activity completed successfully.
5. Open the Blob Storage container.
6. Verify that the transferred data is available.

## Result

The data was successfully extracted from the on-premises SQL Server database and ingested into Azure Blob Storage using an Azure Data Factory Copy Data pipeline.

## Key Learning

This experiment demonstrates how Azure Data Factory can be used to build an ETL/data ingestion pipeline between an on-premises data source and cloud storage using a Self-hosted Integration Runtime.
