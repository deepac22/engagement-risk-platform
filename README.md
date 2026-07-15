# 🎯 Engagement Risk Intelligence Platform

> **AI-powered player risk monitoring and personalized engagement strategies for responsible gaming**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29%2B-red)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1%2B-orange)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-LLM-purple)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📸 Demo

<div align="center">
  <img src="images/dashboard_screenshot.png" alt="Dashboard Overview" width="800"/>
  <br>
  <em>Figure 1: Real-time risk monitoring dashboard with KPI metrics and risk distribution charts</em>
</div>

<br>

<div align="center">
  <img src="images/semantic_search_demo.gif" alt="Semantic Search Demo" width="800"/>
  <br>
  <em>Figure 2: AI-powered semantic search with natural language queries</em>
</div>

---

## 📖 Overview

The **Engagement Risk Intelligence Platform** is an end-to-end Generative AI web application designed to analyze player behavior, identify responsible gaming risks, and generate personalized engagement strategies. This project was built with the following goals:

- **Responsible Gaming**: Flag high-risk players based on spending patterns, visit frequency, and demographic factors
- **Generative AI**: Leverage LangChain and Groq to generate personalized intervention strategies
- **Full-Stack Development**: FastAPI backend + Streamlit frontend with real-time interactivity
- **Data Science**: US Census demographic data integration with synthetic player profiles
- **Business Impact**: Player retention and risk mitigation through actionable insights

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────────────────────┐
│ Data Pipeline │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ US Census API│───▶│ Data Generator│───▶│ CSV Store │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Vector Database (Chroma) │
│ Semantic Player Search │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ FastAPI Backend │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ REST API │ │ LangChain │ │ Groq LLM │ │
│ │ Endpoints │ │ Integration │ │ (Llama 3.3) │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Streamlit Frontend │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ Dashboard │ │ User Profile │ │ Semantic │ │
│ │ │ │ │ │ Search │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ Risk │ │ What-If │ │ Live Demo- │ │
│ │ Analytics │ │ Simulator │ │ graphics │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

---

## ✨ Features

### 📊 Dashboard
- **KPI Metrics**: Total users, average spend, average risk score, high-risk count
- **Risk Level Distribution**: Interactive pie chart
- **Risk Score Histogram**: Distribution of risk scores
- **High-Risk Users**: Data table with filterable columns

### 👤 User Profile
- **User Information**: Age, state, segment, join date
- **Risk Profile**: Risk level, risk score, total spend, visit frequency
- **Explainable AI**: Detailed risk factor breakdown with explanations
- **AI-Powered Recommendations**: Personalized intervention strategies

### 🔍 Search Users
- Keyword search by User ID, State, or Segment
- Real-time filtering and results display

### 🔎 Semantic Search (Vector DB)
- Natural language search (e.g., *"high-risk players in California"*)
- Automatic filter detection for risk level and segment
- Chroma vector database for similarity search
- Results with risk and segment distribution charts

### 📈 Risk Analytics
- **Spend vs Risk Score Scatter Plot**: Visual correlation analysis
- **State Risk Bar Chart**: Average risk score by state
- **Detailed User Data**: Full dataset with sorting and filtering

### 🌎 Live Demographics
- Real US Census demographic data
- **Median Income Chart**: Top 10 states by median income
- **State Demographic Table**: Full dataset with sorting

### 🔄 What-If Simulator
- **Interactive Sliders**: Age, total spend, visit frequency, median income
- **Real-time Risk Calculation**: Instant feedback on risk score changes
- **Explainable Risk Factors**: Clear breakdown of contributing factors

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| **Programming Language** | Python 3.10+ |
| **Backend Framework** | FastAPI |
| **Frontend Framework** | Streamlit |
| **LLM Orchestration** | LangChain |
| **LLM Provider** | Groq (Llama 3.3 70B) |
| **Vector Database** | Chroma |
| **Data Processing** | Pandas, NumPy |
| **Data Visualization** | Plotly |
| **External APIs** | US Census Bureau API |
| **Version Control** | Git, GitHub |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Git
- Groq API Key (free at [console.groq.com](https://console.groq.com/))
- US Census API Key (free at [api.census.gov](https://api.census.gov/data/key_signup.html))

---

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/deepac22/engagement-risk-platform.git
cd engagement-risk-platform
