# FraudGraph Sentinel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Neo4j Aura Free-ready fraud investigation graph agent project from the synthetic financial fraud dataset.

**Architecture:** A Python package streams the large CSV, keeps all fraud rows plus a bounded non-fraud sample, estimates graph size before export, writes Neo4j import CSVs and Cypher, and documents Aura Agent tools. The local code is testable without Aura credentials; loading into Aura is a separate CLI step using environment variables.

**Tech Stack:** Python 3, stdlib CSV/dataclasses/argparse, optional `neo4j` Python driver for Aura loading, pytest for tests, Neo4j AuraDB Free, Aura Agent with Cypher Templates, Text2Cypher, and optional Similarity Search.

---

### Task 1: Test Suite Skeleton

**Files:**
- Create: `tests/test_sampling.py`
- Create: `tests/test_cypher_export.py`
- Create: `tests/test_agent_tools.py`

- [x] **Step 1: Write failing tests for sampler, exporter, and tool specs**
- [x] **Step 2: Run tests to verify import failures**

### Task 2: Core Fraud Graph Package

**Files:**
- Create: `src/fraudgraph_sentinel/__init__.py`
- Create: `src/fraudgraph_sentinel/model.py`
- Create: `src/fraudgraph_sentinel/sampling.py`
- Create: `src/fraudgraph_sentinel/graph_stats.py`

- [ ] **Step 1: Implement transaction dataclass and CSV row parsing**
- [ ] **Step 2: Implement deterministic sampling that keeps every fraud row**
- [ ] **Step 3: Implement Aura Free graph-size estimator**
- [ ] **Step 4: Run focused tests**

### Task 3: Cypher Export And Aura Agent Tools

**Files:**
- Create: `src/fraudgraph_sentinel/cypher_export.py`
- Create: `src/fraudgraph_sentinel/agent_tools.py`
- Create: `src/fraudgraph_sentinel/cli.py`

- [ ] **Step 1: Export node/relationship CSVs for Neo4j import**
- [ ] **Step 2: Generate idempotent constraints and LOAD CSV Cypher**
- [ ] **Step 3: Generate Aura Agent Cypher Template specs**
- [ ] **Step 4: Run focused tests**

### Task 4: Documentation And Submission Package

**Files:**
- Create: `README.md`
- Create: `.env.example`
- Create: `docs/agent_submission.md`

- [ ] **Step 1: Document low-cost Aura Free setup**
- [ ] **Step 2: Document import and agent configuration**
- [ ] **Step 3: Draft challenge submission content**

### Task 5: Real Dataset Output Generation

**Files:**
- Generate: `outputs/fraudgraph_sentinel/*`

- [ ] **Step 1: Run CLI against `datasets/cyber_security_fraud_phishing/Synthetic_Financial_datasets_log.csv`**
- [ ] **Step 2: Verify generated row counts stay under conservative Aura Free limits**
- [ ] **Step 3: Run full tests**
