# Participation Pipeline

Pipeline for Participation Proyect.

The pipeline is based on set tools that form different actions on the data. The actions are part of a data pipeline that defines the workflow of the project. Each action is carried out by a different component or module and is executed sequentially.We present a modular toolkit for processing Big Linked Data,encouraging scalability and reusabilit. 
It integrates existing open-source tools with others built specifically for the toolkit. The main modules are orchestration, data ingestion, pre-processing, analysis, storage, and visualization, which are described below. 

- The Data Ingestion module involves obtaining data from the structured and unstructured data sources and transforming these data into linked data formats, using scraping techniques and APIs, respec-
tively. The use of linked data enables reusability of ingestion modules as well as interoperability and provides a uniform schema for processing data. 
The ingestion is implemented using GSICrawler (Sánchez-Rada et al.,2018), the module responsible for retrieving data.

- The Processing and Analysis module  collects the different analysis tasks that enrich the incoming data, such as psychology analysis and moral value estimation. The analysis is based on the NIF recommen-
dation, which has been extended for multimodal data sources. Each analysis task has been modeled as a plugin of Senpy.
In this way, analysis modules can be easily reused.

- The Storage module is responsible for storing data in a nonSQL database. 
We have selected ElasticSearch (Gormley & Tong, 2015), since it provides scalability, text search as well as a RESTful server based on a Query DSL language. 
For our purposes, JSON-LD (Sporny et al., 2014) is used, with the aim of preserving linked data expressivity in a format compatible with the Elasticsearch ecosystem.

- The Visualization module  enables building dashboards as well as executing semantic queries. Visualization is based on Kibana (Gupta, 2015), on top of which an array of components have been configured to enable faceted search. In addition, the Apache Fuseki (Jena, 2014) interface is exploited to allow users to perform SPARQL Protocol and RFD Query Language (SPARQL) queries, thus enabling complex searches. Fuseki is provisioned by the data pipeline.

![Alt text](./assets/pipeline.png?raw=true "Pipeline")

# Usage

The simplest option is to build the pipeline locally with docker compose:

`$ docker-compose up --build`

# Pipeline and dashboard integration demo

http://participation.gsi.upm.es
