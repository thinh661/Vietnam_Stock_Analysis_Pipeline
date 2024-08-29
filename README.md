# Vietnam-Stock-Analysis-Pipeline

![Logo](https://github.com/thinh661/Vietnam_Stock_Analysis_Pipeline/blob/master/image/logo.jpg)

## Table of Contents
- [Introduction](#introduction)
- [Project Phases](#project-phases)
- [Data Pipeline Architechture](#pipline)
- [Technologies Used](#technologies-used)
- [Crawl Data](#data-source)
- [Setup ENV for project](#setup-env)
- [Design Storage Architechture](#design-storage)
- [ETL](#etl)
- [Visualization](visualization)

## Introduction
Welcome to the Vietnam-Stock-Analysis-Pipeline Project. This is a step-by-step project for Data Engineer. I'll start from Design the pipline architechture, Crawl Data, Design the Storage,Settting the ENV, ETL and Visualzation. The domain of this project focuses on Finance. The data used is basic data from Vietnam stock exchange.

## Project Phases
1. **Data Pipeline Architechture**: First, I will design a data pipeline architecture to handle the input and output for the project.
3. **Technologies Used**: Next, I will discuss the tools I plan to use in the data pipeline and explain the reasons for choosing them.
2. **Crawl Data**: I will outline the data sources I plan to use and write documentation on how to obtain the data.
4. **Setup Env**: Install the necessary tools and environments to implement the project.
5. **Design Storage Architechture**: Proposing an architecture to store data that optimizes query performance and analysis
6. **ETL**: Extract - Transform - Load data into Storage.
7. **Visualization**: Build Dashboard for Analysis.
8. **Report**

## Data Pipeline Architechture
Below is the data pipeline architecture that I will use to transmit data to the visualization tool for securities data analysis.
![Data Pipeline](https://github.com/thinh661/Vietnam_Stock_Analysis_Pipeline/blob/master/image/pipeline_architecture.png)

Raw data will be collected from the API and saved to MinIO. Next, this raw data will be processed through ETL using Airflow and then saved back to MinIO. Trino will serve as the query engine to retrieve the data after ETL for analysis and visualization using Superset.


## Technologies Used
- Data Ingestion: Python and Airflow
- Data Storage: MinIO and Trino.
- Data Transformation: Airflow
- Data Visualization: Superset
- Enviroment: Docker 

For the first, i use the Python and Airflow to ingestion data because Python is ez for use and Airflow is open source. So MinIO-Trino is object storage and it has configuration and features similar to AWS S3. That will make my project change to easily integrate and deploy in the cloud environment. Superset is also open source and we can delve into the source code and make flexible adjustments according to the project's requirements. Additionally, it is free compared to commercial versions like Power BI or Tableau.


## Crawl Data
Data is used in this project is basic data from Vietnam stock exchange and I will collect it through API from two stock exchanges, TCBS and VCI provided by VNSTock3.

Specifically it will be instructed in the file `crawl_data.ipynb` in this repo.

## Setup Enviroment
I'll setup 3 service:
 - MinIO-Trino in docker
 - Airflow_lightweight in docker
 - Superset in docker

And they are in 3 corresponding folders in this project.

You can see the specific installation guide in the readme of each of these folders.


## Design Storage Architechture
Next, I will present how I have designed the securities data storage system to optimize both query performance and long-term data storage, while also supporting future system expansion.

![Storage Architechture](https://github.com/thinh661/Vietnam_Stock_Analysis_Pipeline/blob/master/image/minio_storage_architechtire.png)

1. I intend to split the storage into two zones: Raw Zone and Processed Zone. This approach will clearly separate data processing stages and facilitate easier maintenance and scalability.
2. The special aspect here is due to the data zoning issue in MinIO and filtering during the ETL process. Therefore, I decided to store the data in two separate buckets: one for daily price data and one for hourly price data. These two buckets will serve as the interface between the two data zone.


## ETL
After designing the storage system, I will perform the ETL process using Airflow to clean the data for analysis and visualization. Initially, the data will be collected and stored in the raw data area using the buckets I created during the storage design phase. Then, the daily and hourly stock price data from the raw data area will be extracted, cleaned, and stored back in MinIO.

Due to the data storage design, I will divide the data into master data and transaction data. The ETL process using Airflow will be illustrated with the following visualizations:

![ETL1](https://github.com/thinh661/Vietnam_Stock_Analysis_Pipeline/blob/master/image/ETL1.png)
![ETL2](https://github.com/thinh661/Vietnam_Stock_Analysis_Pipeline/blob/master/image/ETL2.png)
![ETL3](https://github.com/thinh661/Vietnam_Stock_Analysis_Pipeline/blob/master/image/ETL3.png)
![ETL4](https://github.com/thinh661/Vietnam_Stock_Analysis_Pipeline/blob/master/image/ETL4.png)

And the WebUI Airflow for DAGs:
![airflow_img](https://github.com/thinh661/Vietnam_Stock_Analysis_Pipeline/blob/master/image/airflow_webUI.png)

You can see and develop DAGs in folder dags in airflow_lightweight folder.

## Visualization

Finally, after cleaning the data, I will use Trino as the query engine to retrieve the data and feed it into Superset for building dashboards to analyze market trends.
![dashboard1](https://github.com/thinh661/Vietnam_Stock_Analysis_Pipeline/blob/master/image/dashboard_1.png)
![dashboard2](https://github.com/thinh661/Vietnam_Stock_Analysis_Pipeline/blob/master/image/dashboard_2.png)


Currently, my outputs include:
- Top-performing stocks by year.
- Top-performing stocks by month.
- Stable stocks by year.
- Comparison with the market at the same time.
- Price and volume charts by day and hour...

## Report
Due to personal copyright reasons, I have a detailed technical report of the project. If you would like to review it, please contact me via email at `thinh1.work@gmail.com`.

Thank you very much!
---

