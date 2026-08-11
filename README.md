# CMPT 354 Mini Project - Library Database

## Setup
1. Clone this repo
2. Run: `sqlite3 library.db < sql/schema.sql`
3. Run: `sqlite3 library.db < sql/populate.sql`
4. Run: `python app/main.py`

## Structure
- `sql/schema.sql` — all table definitions, constraints, and triggers
- `sql/populate.sql` — sample data