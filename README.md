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
The source dataset for this project is the "HMEQ_dataset", which can be found [here](https://www.kaggle.com/datasets/ajay1735/hmeq-data).

## Technologies Used
- Python (Numpy,Pandas, Matplotlib,...)
- Sklearn (Build Model)
- ReactJS (Frontend)
- Flask (Backend)

## Getting Started
To explore and replicate the project, follow these steps:
1. Clone this repository to your local machine.
2. Setup the evn for the project (python, matplotlib, pandas, sklearn, ReactJS/Html/Css, Flask)
3. Follow the instructions in the respective folders for each project phase (EDA, Pre-processing, Build Model, Deploy) to set up and execute the code.

## EDA Phase
The steps of EDA: 
- Summary (shape, describe,)
- Check null, Outliner
- Distribution
- Data trend
- Correlation and Skewness


![EDA](https://github.com/thinh661/Credit_Score_Webapp/blob/master/image/eda.png)
    
And specifically about the source code in [here](https://github.com/thinh661/Credit_Score_Webapp/blob/master/EDA_hmeq.ipynb).

## Pre-processing Phase
The steps of Pre-processing:
- Handling missing data
- Handling outliner
- Handling imbalance data (Can't do it)
- Normalization (Scaling)
- Reduction
    - PCA
    - Feature Selection
    - Feature Selection + PCA
- Test datasets with various models to find the best stable dataset.


![preprocessing](https://github.com/thinh661/Credit_Score_Webapp/blob/master/image/preprocessing.png)

Specifically about the source code in [here](https://github.com/thinh661/Credit_Score_Webapp/blob/master/Preprocessing_hmeq.ipynb).


## Model Phase
Build models with 4 main machine learning algorithms:
- Random Forest
- Decision Tree
- SVM
- KNN

and tunning them for best validataion.


![model_build](https://github.com/thinh661/Credit_Score_Webapp/blob/master/image/model_acc.png)

Specifically about the source code in this file and 4 models are saved in [here](https://github.com/thinh661/Credit_Score_Webapp/blob/master/build_model.ipynb).

## Deploy Phase
* In this phase, I'll build the Web Application for end users:
    * The frontend is built using the ReactJS framework.
    * GUI:
        ![GUI](https://github.com/thinh661/Credit_Score_Webapp/blob/master/image/GUI.png)
    * The backend is built using the Flask framework by writing RESTful APIs.
    * To test the api working properly, use the postman
        ![Postman](https://github.com/thinh661/Credit_Score_Webapp/blob/master/image/postman_test.png)

## Report

---

