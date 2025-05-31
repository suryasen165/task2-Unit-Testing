# 🚀 FastAPI CSV Upload with PostgreSQL on Kubernetes

A beginner-friendly FastAPI app that lets you upload CSV files, perform CRUD operations, and run inside a Kubernetes cluster with PostgreSQL.

---

## ✅ Features

* 📤 Upload CSV and save to PostgreSQL
* 🔍 Full Create, Read, Update, Delete (CRUD) support
* 🧪 81 Test Cases (3 per function)
* 🐳 Docker support for easy containerization
* ☘️ Deployable on Kubernetes via Minikube + Helm
* 🛠️ Health check and debug endpoints
* ⚙️ CI/CD ready with automated testing pipeline

---

## 🧰 Tech Stack

* **Backend**: FastAPI + SQLAlchemy
* **Database**: PostgreSQL (via Helm chart)
* **Orchestration**: Kubernetes (Minikube)
* **Containerization**: Docker
* **Testing**: Pytest

---

## 📦 Quick Start

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd fastapi-csv-postgres-k8s
```

### 2. Start Minikube & Deploy PostgreSQL

```bash
minikube start --driver=docker

helm repo add bitnami https://charts.bitnami.com/bitnami
helm install my-postgres bitnami/postgresql \
  --set auth.postgresPassword=password \
  --set auth.database=fastapi_db \
  --set primary.persistence.enabled=false
```

### 3. Port Forward PostgreSQL

```bash
kubectl port-forward svc/my-postgres-postgresql 5432:5432
```

### 4. Install Python Dependencies

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 🚀 Run the App

### Option 1: Python

```bash
python test_main.py   # run all tests
python main.py        # start the server
```

### Option 2: Docker

```bash
docker build -t fastapi_app .
docker run -p 8000:8000 fastapi_app
```

### Option 3: CI/CD Pipeline

```bash
python pipeline.py
```

---

## 📚 API Endpoints

| Method | Endpoint         | Purpose             |
| ------ | ---------------- | ------------------- |
| POST   | `/upload/`       | Upload CSV file     |
| GET    | `/records/`      | Get all records     |
| GET    | `/records/{id}`  | Get a single record |
| PUT    | `/records/{id}`  | Update a record     |
| DELETE | `/records/{id}`  | Delete a record     |
| GET    | `/health`        | App health status   |
| GET    | `/debug/columns` | Show DB columns     |

📘 Docs available at: `http://localhost:8000/docs`

---

## 📁 Project Structure

```
.
├── main.py            # FastAPI app
├── database.py        # DB connection and queries
├── utils.py           # CSV helpers
├── test_main.py       # 81 test cases
├── pipeline.py        # Test + build automation
├── Dockerfile
├── requirements.txt
├── k8s-deployment.yaml
└── sample.csv
```

---

## 🧪 Testing

* Run all tests:

  ```bash
  python test_main.py
  ```
* Test types:

  * DB Ops: 18 tests
  * Utils: 3 tests
  * API: 60 tests

---

## ☘️ Kubernetes Deployment

```bash
minikube image load fastapi_app
kubectl apply -f k8s-deployment.yaml
minikube service fastapi-service
```

---

## 🛠️ Config

| Variable       | Default                                                    |
| -------------- | ---------------------------------------------------------- |
| `DATABASE_URL` | `postgresql://postgres:password@localhost:5432/fastapi_db` |
| `PORT`         | `8000`                                                     |

---

## 📌 Notes

* Make sure port-forwarding is running
* Run `pipeline.py` to verify build & tests
* Demo endpoints with Swagger: `http://localhost:8000/docs`

---

## 📄 License

MIT License
