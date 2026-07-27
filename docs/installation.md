# Installation & Local Setup Guide

This document outlines the step-by-step instructions required to set up the Fake News Detection System development environment from scratch.

---

## 1. Prerequisites

Before installing, ensure that your development machine has the following tools pre-installed:

*   **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS (12+), or Windows (10/11 with WSL2).
*   **Python**: Version `3.10.x` or `3.11.x`.
*   **Node.js**: Version `18.x` or higher (includes `npm`).
*   **Docker & Docker Compose**: (Optional, but highly recommended for containerized testing).
*   **Git**: For version control.

---

## 2. Setting Up the Backend API

Follow these commands to configure the Python virtual environment and launch the FastAPI server locally.

### Step 2.1: Create Python Virtual Environment
Navigate to the backend directory and create a virtual environment:
```bash
cd backend
python -m venv venv
```

### Step 2.2: Activate Virtual Environment
*   **Linux/macOS**:
    ```bash
    source venv/bin/activate
    ```
*   **Windows (PowerShell)**:
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```

### Step 2.3: Install System & Python Dependencies
Install wheel utilities first, then fetch the backend package dependencies:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 2.4: Configure Environment Variables
Copy the root `.env.example` into a local `.env` inside the `backend/` directory:
```bash
cp ../.env.example .env
```
Ensure that the `DATABASE_URL` is pointing to SQLite:
```ini
DATABASE_URL=sqlite:///./fakenews.db
```

### Step 2.5: Run the Database Migrations & Start Server
Spin up the FastAPI server via Uvicorn:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
On startup, the server automatically reads schemas and populates the SQLite database file `fakenews.db` inside your backend root.

---

## 3. Setting Up the Machine Learning Module

To run predictions, the machine learning classifier and TF-IDF vectorizer must be trained and saved into the registry.

### Step 3.1: Run Model Training
Run the training module from the root directory to generate synthetic samples (if no raw data is present), fit classifiers, and output the best model candidate:
```bash
# Ensure you are at the project root folder
python -m model.train
```

### Step 3.2: Run Evaluation
Generate performance logs, classification metrics, and confusion matrix heatmap graphs:
```bash
python -m model.evaluate
```

This updates `reports/evaluation_metrics.json` and creates `reports/confusion_matrix.png`, which are then visible on the dashboard.

---

## 4. Setting Up the Frontend Dashboard

Deploy the web dashboard assets using the Vite development server.

### Step 4.1: Install Node Modules
Navigate to the frontend folder and install Vite:
```bash
cd frontend
npm install
```

### Step 4.2: Launch Local Dev Server
Launch Vite to mount index.html and assets:
```bash
npm run dev
```
The console will print out the local server address:
```text
  VITE v5.1.6  ready in 250 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

Vite proxies `/api/v1` calls to the FastAPI backend running on port `8000`. Open your browser and navigate to [http://localhost:5173](http://localhost:5173) to view the VeritasAI dashboard.
