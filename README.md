# 🏠 Ireland Rent Tracker

> **Live Dashboard:** [ireland-rent-tracker.streamlit.app](https://ireland-rent-tracker.streamlit.app)

An end-to-end data engineering project tracking rental prices across all 26 Irish counties from 2008 to 2024. Built with the modern data stack used by data engineering teams across Ireland.

---

## 📊 Key Insights From The Data

| Metric | Value |
|--------|-------|
| National average rent 2024 | €1,497/month |
| National average rent 2008 | €973/month |
| Total increase since 2008 | 53.8% |
| Most expensive area | Dublin 14 — €2,656/month |
| Market bottom | €777 in 2011 |
| Areas with falling rents | 50 locations |

---

## 🏗️ Architecture
```
RTB/CSO API (Irish Government Data)
        ↓
Python Scraper (ETL Pipeline)
        ↓
AWS S3 (Data Lake)
        ↓
Amazon Redshift Serverless (Data Warehouse)
        ↓
dbt (Data Transformation)
        ↓
Apache Airflow (Orchestration)
        ↓
Streamlit Dashboard (Visualisation)
        ↓
Docker (Containerisation)
        ↓
Terraform (Infrastructure as Code)
        ↓
GitHub Actions (CI/CD)
```

---

## 🛠️ Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Language | Python 3.12 | Core language |
| Data Source | RTB / CSO Ireland | Official government rent data |
| Data Lake | AWS S3 | Raw file storage |
| Warehouse | Amazon Redshift Serverless | Analytics database |
| Transform | dbt | SQL transformation layer |
| Orchestration | Apache Airflow | Daily pipeline scheduling |
| Dashboard | Streamlit + Plotly | Interactive visualisation |
| Container | Docker | Packaging and deployment |
| IaC | Terraform | AWS infrastructure as code |
| CI/CD | GitHub Actions | Automated testing and deployment |
| Version Control | Git + GitHub | Code management |

---

## 📁 Project Structure
```
ireland-rent-tracker/
│
├── scraper/
│   └── rtb_scraper.py          # ETL pipeline — CSO API → S3
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── sources.yml
│   │   │   └── stg_rents.sql   # Clean raw data
│   │   └── marts/
│   │       ├── rent_by_county.sql
│   │       ├── rent_by_bedrooms.sql
│   │       ├── national_trends.sql
│   │       └── falling_rents.sql
│   └── dbt_project.yml
│
├── airflow/
│   └── dags/
│       └── rent_pipeline.py    # Daily orchestration DAG
│
├── dashboard/
│   └── app.py                  # Streamlit dashboard
│
├── infrastructure/
│   ├── main.tf                 # Terraform provider config
│   ├── s3.tf                   # S3 data lake
│   ├── redshift.tf             # Redshift serverless
│   ├── security.tf             # IAM roles and security groups
│   └── variables.tf            # Input variables
│
├── sql/
│   ├── create_tables.py        # Creates Redshift schemas
│   └── load_data.py            # S3 → Redshift COPY command
│
├── tests/
│   └── test_scraper.py         # Unit tests
│
├── .github/
│   └── workflows/
│       ├── ci.yml              # Code quality checks
│       └── deploy.yml          # Auto deployment
│
├── .streamlit/
│   └── config.toml             # Streamlit theme config
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dashboard.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- AWS Account
- Docker

### Installation
```bash
# Clone the repo
git clone https://github.com/nameisrohit/ireland-rent-tracker.git
cd ireland-rent-tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-dashboard.txt

# Configure AWS
aws configure

# Create .env file
cp .env.example .env
# Fill in your Redshift credentials

# Run the scraper
python3 scraper/rtb_scraper.py

# Run the dashboard
streamlit run dashboard/app.py
```

---

## 📈 Dashboard Features

- **National Trends** — rent from 2008 to 2024 with financial crisis annotation
- **County Comparison** — ranked bar chart across all 26 counties
- **Bedroom Analysis** — one bed vs two bed vs three bed vs four plus bed
- **Falling Rents** — areas where rent has decreased year on year

---

## 🗄️ Data Source

- **Source:** RTB Average Monthly Rent Report — Central Statistics Office Ireland
- **Coverage:** All 26 Irish counties, 438 unique areas
- **Period:** 2008 to 2024
- **Rows:** 109,558 clean records
- **Licence:** Creative Commons Attribution 4.0

---

## ☁️ Infrastructure

All AWS infrastructure is provisioned using Terraform:
```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

Resources created:
- S3 bucket with versioning enabled
- Redshift Serverless namespace and workgroup
- IAM role for Redshift S3 access
- Security group with port 5439 open

---

## 🔄 CI/CD

Every push to main triggers:
1. **CI** — flake8 code quality checks + pytest unit tests
2. **CD** — validates all files exist + confirms Streamlit Cloud deployment

---

## 👤 Author

**Rohit**
- GitHub: [@nameisrohit](https://github.com/nameisrohit)
- LinkedIn: [linkedin.com/in/rohit-s-yadav](https://linkedin.com/in/rohit-s-yadav)
- Portfolio: [rohityadav.ie](https://rohityadav.ie)
- Live Project: [ireland-rent-tracker.streamlit.app](https://ireland-rent-tracker.streamlit.app)

---

## 📄 Licence

MIT