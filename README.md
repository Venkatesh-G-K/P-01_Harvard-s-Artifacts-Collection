# 🏛️ Harvard Artifacts Collection: ETL, SQL Analytics & Streamlit Dashboard

## 📌 Project Overview

This project builds an **end-to-end ETL pipeline** using the Harvard Art Museums Public API.  
It collects artifact data, transforms JSON data into structured tables, stores it in SQL, and provides an interactive **Streamlit dashboard** for querying and exploring museum artifacts.

The system enables users to dynamically fetch artifacts, store them into a relational database, and run SQL queries to analyze cultural and historical collections.

---

## 🎯 Objectives

- Fetch artifact data from Harvard Art Museums API
- Transform nested JSON into structured datasets
- Store cleaned data into SQL tables
- Run SQL analytics queries
- Visualize and explore data using Streamlit

---

## 🛠️ Technologies Used

- Python
- Streamlit
- SQL (MySQL / TiDB Cloud)
- Pandas
- Requests (API Integration)
- SQLAlchemy
- GitHub

---

## 📂 Project Workflow

### Step 1 — API Data Collection
- Connected to Harvard Art Museums API
- Used pagination to collect **2500+ records**
- Filtered data based on classification

---

### Step 2 — Data Transformation
Converted JSON into:

- artifact_metadata
- artifact_media
- artifact_colors

Handled:

- Missing values
- Nested color structures
- Data cleaning

---

### Step 3 — Database Storage

Stored data into **3 SQL Tables**:

#### 🗄️ artifact_metadata

Stores general artifact details:

- id
- title
- culture
- period
- century
- medium
- dimensions
- description
- department
- classification
- accessionyear
- accessionmethod

---

#### 🖼️ artifact_media

Stores media information:

- objectid
- imagecount
- mediacount
- colorcount
- rank
- datebegin
- dateend

---

#### 🎨 artifact_colors

Stores color details:

- objectid
- color
- spectrum
- hue
- percent
- css3

---

### Step 4 — SQL Analysis

Implemented SQL queries such as:

- Unique cultures
- Artifacts per department
- Top colors used
- Artifacts with multiple images
- Media statistics
- Join-based queries

---

### Step 5 — Streamlit Dashboard

Built an interactive UI to:

- Select classification
- Collect artifact data
- Store data into SQL
- Run SQL queries
- Display results dynamically

---

## 📊 Sample Queries

```sql
SELECT DISTINCT culture
FROM artifact_metadata;
