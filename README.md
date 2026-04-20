# 📒 Financial Book App

A personal finance tracking web application built around rule-based, 
automatic budget allocation — designed for irregular, multi-source income.

> Built by [Boniface Kibet](https://github.com/YOUR_GITHUB_USERNAME) as both 
> a personal finance tool and a Data Engineering portfolio project.

---

## 🧠 The Problem

Most finance apps assume you have one income source and a fixed monthly salary. 
They don't handle irregular income well, and their budget rules are rigid.

This app was born from a personal spreadsheet that tracked multiple income types 
(salary, side hustles, upkeep, investments) and automatically split each one into 
budget categories using different rules per income type.

The goal: turn that spreadsheet into a proper, extensible web application — 
starting as a personal tool, with plans to open it to other users in 2027.

---

## ✨ Key Features

- **Multi-source income logging** — supports 7 income categories, each with subtypes
- **Rule-based auto-allocation** — income is automatically split into budget buckets 
  based on configurable rules per income category
- **Smart deduction ordering** — certain deductions (e.g. Tithe, Fare) are processed 
  before percentage splits, in a defined sequence
- **Fare top-up logic** — transport budget is topped up to a target amount monthly, 
  not blindly allocated
- **Full audit trail** — every allocation is linked to the exact rule version that 
  produced it (Slowly Changing Dimension Type 2)
- **Rule history** — budget rules are versioned, so changing a rule never 
  corrupts historical data
- **Debt tracking** — named loans and personal payment obligations
- **Transaction ledger** — full record of money moving in and out of each bucket

---

## 🗂️ Income Categories

| # | Category | Examples |
|---|---|---|
| 1 | Earned Income | Salary, Freelancing, Commissions, Bonuses |
| 2 | Passive Income | Rental income, Dividends, Royalties |
| 3 | Business Income | Revenue from active business operations |
| 4 | Investment Income | Interest, Capital gains |
| 5 | Transfer Income | Upkeep, Gifts, Scholarships, Government support |
| 6 | Residual Income | Subscriptions, Affiliate marketing, Content monetization |
| 7 | Other | Anything that doesn't fit above |

---

## 💰 Default Budget Rules

### Earned Income
| Step | Category | Rule |
|---|---|---|
| 1st (before splits) | Tithe | 10% of gross |
| 2nd (before splits) | Fare | Top up to KES 5,000 on 1st of month |
| Remainder | Food | 25% |
| Remainder | Housing | 15% |
| Remainder | Clothing | 10% |
| Remainder | Wants | 20% |
| Remainder | Investment/Savings | 20% |

### All Other Income (except Other)
| Category | Rule |
|---|---|
| Food | 25% |
| Housing | 15% |
| Clothing | 10% |
| Wants | 20% |
| Investment/Savings | 20% |
| Tithe | 10% |

### Other (Category 7)
| Category | Rule |
|---|---|
| Food | 25% |
| Housing | 15% |
| Clothing | 10% |
| Wants | 30% |
| Investment/Savings | 20% |
| Tithe | Not applied |

---

## 🏗️ Architecture
[ React Frontend ]
↕ REST API
[ FastAPI Backend ]  ←  Allocation engine + Rule processor
↕
[ SQLite → PostgreSQL ]  ←  Income, allocations, rules, transactions, debts
---

## 🗄️ Database Schema

| Table | Purpose |
|---|---|
| `income_entries` | Every income event logged by the user |
| `income_allocations` | Auto-generated budget splits per income entry |
| `budget_rules` | Versioned allocation rules (SCD Type 2) |
| `transactions` | Money moving in/out of each budget bucket |
| `debts` | Named loans and personal payment obligations |

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | React | Component-based, industry standard |
| Backend | FastAPI (Python) | Fast, clean, async-ready |
| ORM | SQLAlchemy | Pythonic database interaction |
| Database (dev) | SQLite | Zero-config, file-based |
| Database (prod) | PostgreSQL | Scalable, production-grade |
| Hosting | Railway / Render | Simple GitHub-connected deployment |

---

## 🚀 Getting Started (Local / Codespaces)

### Prerequisites
- Python 3.11+
- Node.js 18+ *(for frontend, coming soon)*

### Setup

```bash
# Clone the repo
git clone https://github.com/bonito-dev/financial-book-app.git
cd financial-book-app

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # then edit .env with your values

# Create database tables
python -m app.database.init_db

# Seed initial budget rules
python -m app.database.seed

# Start the development server (coming soon)
uvicorn app.main:app --reload
```

---

## 📍 Project Roadmap

### Phase 1 — Backend Foundation *(complete ✅)*
- [x] Project structure & environment setup
- [x] Database schema design
- [x] SQLAlchemy models (Income, Rules, Allocations, Transactions, Debts)
- [x] Budget rules seeded with SCD Type 2 versioning
- [x] Allocation engine (deductions + top-up + percentages)
- [x] Income logging API + allocation engine
- [x] Transactions API
- [x] Balances API (live calculated)
- [x] Debts API

### Phase 2 — Frontend
- [ ] React project setup
- [ ] Income logging form
- [ ] Budget dashboard (balances per category)
- [ ] Transaction ledger view
- [ ] Debt tracker

### Phase 3 — Intelligence & Reporting
- [ ] Monthly income trend charts
- [ ] Budget health indicators
- [ ] 52-Week Savings Challenge tracker
- [ ] Rule change history viewer

### Phase 4 — Multi-user (2027)
- [ ] User authentication (JWT)
- [ ] Per-user budget rule customisation
- [ ] PostgreSQL migration
- [ ] Production deployment

---

## 📚 What I'm Learning Through This Project

This project is being built as a hands-on learning journey through:

- **SQL & Relational Data Modelling** — schema design, primary/foreign keys, normalisation
- **Slowly Changing Dimensions (SCD Type 2)** — versioning data that changes over time
- **FastAPI** — building REST APIs with Python
- **SQLAlchemy ORM** — database interaction without raw SQL
- **React** — component-based frontend development
- **Git & GitHub** — version control and portfolio management
- **Data Engineering principles** — ETL thinking, pipeline design, audit trails

---

## 📄 License

This project is currently unlicensed — all rights reserved.
A licence will be added before the public launch in 2027.

---

*Last updated: April 2026*
