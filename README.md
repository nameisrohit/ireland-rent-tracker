# 🏠 Ireland Rent Tracker

An end-to-end data engineering project tracking rental prices across all 26 Irish counties.

## 🏗️ Architecture
```
RTB/CSO API (Irish Government Data)
        ↓
Python Scraper (requests, pandas)
        ↓
AWS S3 (Data Lake)
        ↓
Amazon Redshift (Data Warehouse)
        ↓
dbt (Data Transformation)
        ↓
Apache Airflow (Orchestration)
        ↓
Streamlit Dashboard (Visualisation)
        ↓
Docker + GitHub Actions (CI/CD)
```

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| Language | Python 3.12 |
| Data Source | RTB/CSO Ireland Open Data |
| Data Lake | AWS S3 |
| Data Warehouse | Amazon Redshift Serverless |
| Transformation | dbt |
| Orchestration | Apache Airflow |
| Dashboard | Streamlit + Plotly |
| Infrastructure | Terraform |
| Containers | Docker |
| CI/CD | GitHub Actions |

## 📊 Data

- **Source**: RTB Average Monthly Rent Report (CSO Ireland)
- **Coverage**: All 26 Irish counties, 438 unique areas
- **Period**: 2008 to 2024
- **Rows**: 109,558 clean records
- **Updated**: Daily via Airflow pipeline

## 🗂️ Project Structure
```
ireland-rent-tracker/
│
├── scraper/
│   └── rtb_scraper.py        # ETL pipeline — CSO API → S3
│
├── dbt/
│   ├── models/
│   │   ├── staging/          # Clean raw data
│   │   └── marts/            # Business logic
│   └── dbt_project.yml
│
├── airflow/
│   └── dags/
│       └── rent_pipeline.py  # Daily orchestration
│
├── dashboard/
│   └── app.py                # Streamlit dashboard
│
├── infrastructure/
│   └── main.tf               # Terraform IaC
│
├── .github/
│   └── workflows/
│       └── deploy.yml        # CI/CD pipeline
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

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
pip install -r requirements.txt

# Configure AWS
aws configure

# Run the scraper
python3 scraper/rtb_scraper.py
```

## 📈 Dashboard Features

- Rent trends by county (2008–2024)
- Price per bedroom breakdown
- Year-on-year change by area
- Counties where rent is falling
- National vs county comparison

## 👤 Author

**Rohit**
- GitHub: [@nameisrohit](https://github.com/nameisrohit)
- LinkedIn: [[Rohit Yadav](https://www.linkedin.com/in/rohit-s-yadav/)]

## 📄 Licence

MIT
