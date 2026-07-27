# VeritasAI - Fake News Detection System

VeritasAI is a production-ready, full-stack machine learning application designed to classify raw text articles and uploaded documents (.txt, .pdf, .docx) as **Real News** or **Fake News**. 

This system comprises a FastAPI backend with SQLite logging, a responsive single-page web dashboard built using Bootstrap 5 and Chart.js, and an offline machine learning pipeline (TF-IDF + Scikit-Learn Classifiers).

---

## 1. Directory Blueprint

```text
├── .env.example              # Blueprint configuration file
├── .gitignore                # Global git ignore rules
├── docker-compose.yml        # Multi-container local deployment orchestrator
├── README.md                 # Project Overview (This file)
├── requirements.txt          # Global packages requirements (development tools)
│
├── backend/                  # FastAPI Application Services
│   ├── app/                  # Application source package
│   │   ├── api/              # Endpoint modules (predict, model, history)
│   │   ├── core/             # Base configurations (databases, settings loaders)
│   │   ├── models/           # SQLAlchemy prediction history models
│   │   ├── schemas/          # Pydantic input/output validation schemas
│   │   ├── services/         # File parse services (txt, pdf, docx)
│   │   └── main.py           # FastAPI server bootstrapper
│   ├── Dockerfile            # Multi-stage production image container
│   ├── requirements.txt      # API package requirements
│   └── pyproject.toml        # Ruff, Black, and MyPy checking parameters
│
├── frontend/                 # Client Web Dashboard 
│   ├── index.html            # Main dashboard structural layouts
│   ├── style.css             # Glassmorphism variables, dark/light styles, animations
│   ├── app.js                # Routing control, chart canvas renderer, and native API fetch wrappers
│   ├── package.json          # Node server commands
│   └── vite.config.js        # Host and proxy port specifications
│
├── model/                    # Offline Machine Learning Pipeline
│   ├── artifacts/            # Model registries (.pkl binaries)
│   ├── dataset_loader.py     # Data stream split and generation fallback
│   ├── preprocessing.py      # Cleaner (lowering, cleaning, stopwords, WordNet lemmatizing)
│   ├── feature_extraction.py # TF-IDF feature maps vectorizer fit/transform
│   ├── train.py              # Compares Naive Bayes, SVM, RF, Logistic Regression; saves best model
│   ├── evaluate.py           # Evaluation report builder & confusion matrix generator
│   └── predict.py            # API-facing inference mapping (signed distance confidence scores)
│
├── data/                     # Local data splits (raw, processed)
├── uploads/                  # Temporary file upload cache
├── reports/                  # Evaluation JSON files and graphical confusion heatmaps
├── tests/                    # Testing suite (unit tests, endpoints validations)
└── docs/                     # Comprehensive documentation guides
```

---

## 2. Documentation Index

The complete documentation has been generated and structured within the `/docs` and `/tests` folders:

*   **[docs/installation.md](file:///C:/Users/gowth/.gemini/antigravity/scratch/fake-news-detection-system/docs/installation.md)**: Setup instructions for Python virtual environments, database migrations, model training runs, and Vite frontend servers.
*   **[docs/deployment.md](file:///C:/Users/gowth/.gemini/antigravity/scratch/fake-news-detection-system/docs/deployment.md)**: Deployment guidelines featuring Docker-Compose setups, bare-metal Linux VPS servers using Gunicorn + Nginx, and GitHub Actions CI/CD workflows.
*   **[docs/api_documentation.md](file:///C:/Users/gowth/.gemini/antigravity/scratch/fake-news-detection-system/docs/api_documentation.md)**: REST specifications for predict, upload, metrics, health, and history, complete with request/response schemas.
*   **[docs/project_report.md](file:///C:/Users/gowth/.gemini/antigravity/scratch/fake-news-detection-system/docs/project_report.md)**: Project implementation report covering data preprocessing, TF-IDF math formulas, engineering challenges (such as SVM probability approximations), and future scopes.
*   **[docs/testing.md](file:///C:/Users/gowth/.gemini/antigravity/scratch/fake-news-detection-system/docs/testing.md)**: Pytest instructions and unit test layouts.

---

## 3. Quick Start (Docker-Compose)

If you have Docker installed, you can spin up the entire application locally in one command:

1. Copy the environment variables template:
   ```bash
   cp .env.example .env
   ```
2. Build and run the containers:
   ```bash
   docker-compose up -d --build
   ```
3. Open [http://localhost:5173](http://localhost:5173) in your browser to access the VeritasAI dashboard.
