# 🛒 Amazon Sales Data Analysis

An interactive data analysis dashboard built with **Python** and **Streamlit** that explores 1,000 Amazon order records — covering data quality checks, sales calculations, group summaries, visual charts, and business recommendations.

---

## 📂 Dataset

| Field | Details |
|-------|---------|
| **File** | `data analytics 1000 rows.csv` |
| **Rows** | 1,000 orders |
| **Columns** | 20 (user_id, product_id, category, brand, price, discount, final_price, rating, location, payment_method, delivery_status, and more) |
| **Source** | Local CSV — place in the same folder as `amazon_sales_analysis.py` |

---

## 📋 Project Description

This project takes a raw Amazon sales CSV file and turns it into useful business information through a 6-step analysis:

1. **Load Data** — Read and explore the CSV dataset
2. **Data Quality Check** — Find missing values, duplicates, and invalid entries
3. **Sales Calculation** — Compute `Sales = Quantity × Unit Price` for every order
4. **Group & Summarize** — Aggregate data by category, brand, location, payment method, delivery status, and device
5. **Visual Charts** — 10 interactive Plotly charts to compare results
6. **Business Insights** — 10 plain-language recommendations derived from the data

The Streamlit frontend is fully interactive — sidebar filters (Category, Location, Brand) update all tables and charts instantly.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.12** | Core programming language |
| **Streamlit 1.64** | Web-based interactive dashboard |
| **Pandas 3.0** | Data loading, cleaning, and analysis |
| **NumPy 2.5** | Numerical operations |
| **Plotly 7.1** | Interactive charts and visualisations |

---

## ⚙️ Setup & Run Instructions

### 1. Prerequisites

Make sure **Python 3.8 or later** is installed on your computer.  
Check by running:

```bash
python --version
```

### 2. Clone or Download the Project

Place all project files in the same folder:

```
📁 Project Folder
├── amazon_sales_analysis.py
├── data analytics 1000 rows.csv
├── requirements.txt
├── run.bat
└── README.md
```

### 3. Install Dependencies

Open a terminal in the project folder and run:

```bash
python -m pip install -r requirements.txt
```

### 4. Launch the App

**Option A — Command line:**

```bash
python -m streamlit run "amazon_sales_analysis.py"
```

**Option B — Double-click shortcut (Windows only):**

Double-click `run.bat` in File Explorer.

### 5. Open in Browser

The app opens automatically at:

```
http://localhost:8501
```

To stop the app, press `Ctrl + C` in the terminal.

---

## 📊 Key Features

- **6-tab dashboard** — Data Overview, Data Quality, Sales Summary, Group Analysis, Charts, Business Insights
- **Live sidebar filters** — Filter by Category, Location, and Brand; all views update instantly
- **Sales formula** — `Sales = Quantity × final_price` (1 unit per order row, price after discount)
- **10 interactive charts** — Bar, line, pie, and scatter charts powered by Plotly
- **Auto-generated insights** — Business recommendations are dynamically computed from the actual data
- **CSV upload support** — Upload any compatible CSV file via the sidebar to replace the default dataset

---

## 📁 Project Files

| File | Description |
|------|-------------|
| `amazon_sales_analysis.py` | Main Streamlit application |
| `data analytics 1000 rows.csv` | Dataset (1,000 Amazon orders) |
| `requirements.txt` | Python dependency list |
| `run.bat` | One-click Windows launcher |
| `YourName_ProjectReport.docx` | Full project documentation (Word) |
| `README.md` | This file |

---

## 📦 Requirements

```
streamlit==1.64.0
pandas==3.0.6
numpy==2.5.3
plotly==7.1.0
```

---

