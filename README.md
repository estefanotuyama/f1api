# 🏎️ F1 Stats API v0.1

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.110-green)


A FastAPI backend for exploring Formula 1 driver data, sessions, lap times, and results—using OpenF1 data.

-----

## 🚀 Features

  - ✅ Track F1 events by year and location
  - ✅ View session info (FP1, FP2, Qualifying, Race, etc.)
  - ✅ Explore driver participation and lap times
  - ✅ Clean, modular FastAPI backend using SQLModel
  - ✅ SQLite database, easily extendable to PostgreSQL

-----

## 📁 Project Structure

```sh
F1Project/
├── main.py           # FastAPI app entry point
├── database.py       # Engine + session setup
├── db_populate.py    # Script to populate DB from OpenF1
├── models/           # SQLModel ORM classes
├── api/              # API route definitions (WIP)
├── crud/             # DB access logic (WIP)
├── schemas/          # Pydantic models for request/response (WIP)
├── utils/            # Utility files like logging setup
├── f1.db             # SQLite database (ignored in Git)
└── .env              # Environment variables (ignored in Git)
```

-----

## 🛠️ Setup & Usage

### 1\. Clone the Repo

```bash
git clone git@github.com:estefanotuyama/f1api.git
cd f1api
```

### 2\. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
.\venv\Scripts\activate   # On Windows
```

### 3\. Install Dependencies

First, ensure you have a `requirements.txt` file. If not, you can create one:

```bash
pip freeze > requirements.txt
```

Then, install the dependencies:

```bash
pip install -r requirements.txt
```

### 4\. 🗄️ Populate the Database

The project pulls data from the OpenF1 API. To create the database tables and populate the 2024 season, run:

```bash
python db_populate.py
```

### 5\. 🧪 Run the API Server

Start the development server with:

```bash
uvicorn main:app --reload
```

Now, you can access the API documentation:

  - **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
  - **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

-----

## 📌 TODO

  - [ ] Add driver, session, and lap time API routes
  - [ ] Implement pagination and filtering for API endpoints
  - [ ] Write tests using `pytest`
  - [ ] Convert to PostgreSQL (optional)
  - [ ] Deploy to a cloud service (Render, Vercel, Fly.io)

-----

## 👨‍💻 Author

Built by **Estéfano Tuyama Gerassi**

-----

## ⚠️ License

This project is for educational purposes only. Data is sourced from the public [OpenF1 API](https://openf1.org/).