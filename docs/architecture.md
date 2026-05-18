# System Architecture

## Project: AI-Powered Global Job Market Intelligence Platform

## Overview
A full-stack analytics platform that ingests global job market data,
runs ETL pipelines, stores structured data in PostgreSQL, and serves
insights through a FastAPI backend and React dashboard.

## Data Flow
Raw Datasets → ETL Pipeline → PostgreSQL Warehouse → FastAPI → React UI

## Layers
1. **Data Sources**: Kaggle, LinkedIn, government labor stats, synthetic data
2. **ETL Pipeline**: Python (Pandas/Polars) extraction, cleaning, transformation
3. **Data Warehouse**: PostgreSQL with staging, core, analytics, and mart schemas
4. **Backend API**: FastAPI with SQLAlchemy ORM
5. **Forecasting**: Prophet (time series), XGBoost (ML predictions)
6. **Frontend**: React with Recharts and Chart.js visualizations
7. **AI Layer**: Groq/OpenAI chatbot for natural language queries

## Key Design Decisions
- Immutable raw data: source files are never modified
- Schema separation: staging → core → analytics progression
- Environment variables: no hardcoded credentials anywhere