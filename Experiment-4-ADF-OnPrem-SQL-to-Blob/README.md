# Experiment 4: Azure Data Factory – On-Premises SQL Server to Azure Blob Storage

## Aim

To create an Azure Data Factory pipeline to extract student data from an on-premises SQL Server database and load it into Azure Blob Storage using a Copy Data activity.

---

## Objective

- To configure Azure Data Factory for data ingestion.
- To connect an on-premises SQL Server as the source.
- To configure Azure Blob Storage as the destination.
- To create source and sink datasets.
- To configure and execute a Copy Data pipeline.
- To verify the successful transfer of data from SQL Server to Blob Storage.

---

## Azure Services and Tools Used

- Azure Data Factory
- Azure Blob Storage / ADLS Gen2
- On-Premises SQL Server
- Self-Hosted Integration Runtime
- Azure Portal
- SQL Server Management Studio / SQL Server

---

## Architecture

```text
On-Premises SQL Server
        |
        |  Self-Hosted Integration Runtime
        |
        v
Azure Data Factory
        |
        |  Copy Data Activity
        |
        v
Azure Blob Storage / ADLS Gen2
        |
        v
Student CSV Data
