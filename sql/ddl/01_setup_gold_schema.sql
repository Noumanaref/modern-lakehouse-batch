-- create database and schema containers

create database if not exists LAKEHOUSE_DB;
create schema if not exists LAKEHOUSE_DB.GOLD;

-- Set the session context

use database LAKEHOUSE_DB;
use schema GOLD;
use role accountadmin;

-- Define incoming data's file format inside the schema (parquet)

create or replace file format parquet_format
    type = parquet
    compression = snappy;

-- Create the External Stage for Stock Prices

create or replace stage silver_prices_stage
    storage_integration = s3_lakehouse_integration
    url = "s3://modern-lakehouse-processed/silver/stock_prices/"
    file_format = parquet_format;

-- Create the External Stage for company profile

create or replace stage silver_profile_stage
    storage_integration = s3_lakehouse_integration
    url = "s3://modern-lakehouse-processed/silver/company_profiles/"
    file_format = parquet_format;