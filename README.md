# Premises Data Processing Graph

A LangGraph-based automation for processing premises location data with Google Places API validation, SQL-based duplicate detection, and LLM-powered occupancy classification.

**Gauntlet AI Launch Labs - Graph Systems Assignment**

---

## Overview

This project implements a multi-step graph workflow that:
- Ingests CSV files with premises (business location) data
- Validates and standardizes addresses using Google Places API
- Detects duplicates using lat/long proximity + LLM semantic similarity scoring
- Classifies occupancy types based on business type and state regulations
- Outputs three CSVs: successful records, errors, and detected duplicates

---

## Setup

### Prerequisites

- Python 3.13+
- MySQL database (LIV backend running in Docker)
- Anthropic API key
- (Optional) Google Places API key

### Installation

1. Clone and navigate to the project
2. Install dependencies: `uv sync`
3. Configure `.env` with your API keys
4. Ensure LIV database is running: `docker compose up -d mysql`
5. Test connection: `.venv/bin/python test_db_connection.py`

---

## Usage

### Process a Single CSV

```bash
.venv/bin/python -m graph.orchestrator <path_to_csv>
```

### Run Golden Set Evaluation

```bash
.venv/bin/python golden_set/evaluator.py
```

---

## Architecture

**11 Nodes | 3 Branching Decisions | 1 Main Loop**

See `PLAN.md` for detailed architecture and design decisions.

---

## Assignment Requirements Met

✅ Multi-step workflow (11 nodes)
✅ 3 tools (Google Places API, SQL, LLM)
✅ Branching decisions (3)
✅ Loop (row iteration)
✅ Golden set (10 test cases)

---

**Ready to Face the Gauntlet!** 🚀
