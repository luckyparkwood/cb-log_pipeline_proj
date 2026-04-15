# cb-log_pipeline_proj
Overview

This project is a lightweight log processing pipeline that simulates a simplified observability system.

It ingests log events through an API, buffers them in a queue, processes them asynchronously, stores them for analysis, and generates alerts based on recent behavior. A log generator produces continuous traffic, and a CLI report provides real-time visibility into both system health and pipeline performance.

The goal was to model production-style patterns such as decoupled ingestion, asynchronous processing, time-windowed aggregation, rule-based alerting, and pipeline self-observability.

---

What the system does

At a high level, the system:

- accepts log events from simulated services
- validates and enriches incoming data
- buffers logs in Redis to decouple ingestion from processing
- processes logs asynchronously via a worker
- stores logs and alerts in SQLite
- computes metrics over recent time windows (e.g., last 60 seconds)
- triggers alerts when thresholds are exceeded (error rate, latency)
- tracks pipeline health (queue depth, processing lag, throughput)
- provides a CLI report showing current system state and pipeline performance

---

Architecture

Data flows through the system as follows:

Generator → API → Redis → Worker → SQLite → Rules → Alerts → Report

In addition, the worker continuously records pipeline health metrics:

Worker → pipeline_metrics (SQLite) → Report

Each component has a single responsibility and communicates through well-defined boundaries.

---

Components

API (app/api.py)

- FastAPI service with a POST /logs endpoint
- Validates incoming events using a Pydantic schema
- Adds ingestion metadata
- Pushes events into Redis

Purpose:  
Handles ingestion and enforces a consistent log format while keeping request handling lightweight.

---

Schema (app/schemas.py)

- Defines the structure of a log event

Purpose:  
Ensures incoming data is validated and consistent before entering the pipeline.

---

Queue (app/redis_client.py)

- Uses Redis lists for buffering
- Producers push logs (LPUSH)
- Worker consumes logs (BRPOP)
- Exposes queue depth (LLEN)

Purpose:  
Decouples ingestion from processing, allowing the system to absorb bursts of traffic without blocking the API.

---

Worker (app/worker.py)

- Continuously consumes logs from Redis
- Persists logs to SQLite
- Evaluates alerting rules
- Stores triggered alerts
- Records pipeline metrics for each processed event

Metrics recorded:

- queue depth
- processing lag (event time vs processing time)
- total logs processed

Purpose:  
Performs asynchronous processing and isolates downstream work from the ingestion layer, while also instrumenting the pipeline itself.

---

Database (app/db.py)

- Initializes SQLite schema
- Provides a connection helper
- Stores logs, alerts, and pipeline metrics

Tables:

- logs
- alerts
- pipeline_metrics

Purpose:  
Provides persistent storage and enables aggregation queries for alerting, reporting, and pipeline monitoring.

---

Rules Engine (app/rules.py)

- Computes metrics over a recent time window (last 60 seconds)
- Calculates:
    - log count
    - error rate
    - average latency
- Triggers alerts when thresholds are exceeded

Current rules:

- High error rate (> 20%)
- High average latency (> 500 ms)

Purpose:  
Transforms raw log data into meaningful signals and detects abnormal behavior.

---

Log Generator (app/generator.py)

- Simulates multiple services emitting logs
- Introduces random error spikes and latency spikes

Purpose:  
Provides continuous, realistic input for testing and demonstrating the pipeline.

---

Reporting CLI (app/report.py)

- Displays:
    - total logs and alerts
    - per-service metrics (last 60 seconds)
    - recent alerts
    - pipeline health metrics

Pipeline health includes:

- current queue depth
- latest processing lag
- average processing lag (recent samples)
- logs processed by worker
- approximate processing rate (logs/sec)

Purpose:  
Provides real-time visibility into both system behavior and pipeline performance, making it easy to observe trends, detect bottlenecks, and validate system health.

---

Key design ideas

- Decoupling: API and processing are separated via Redis
- Asynchronous processing: worker consumes logs independently of ingestion
- Time-windowed aggregation: metrics computed over recent data
- Rule-based alerting: simple thresholds trigger alerts
- Pipeline self-observability: the system tracks its own performance metrics
- Separation of concerns: each component has a focused responsibility

---

Summary

This project demonstrates how to build a small-scale observability pipeline using production-style patterns. It shows how logs can be ingested, processed asynchronously, analyzed in near real time, surfaced as actionable alerts, and monitored through pipeline-level metrics such as queue depth, processing lag, and throughput.