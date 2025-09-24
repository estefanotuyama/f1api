# 🏎️ F1 Stats API v0.6

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.110-green)


A FastAPI backend for exploring Formula 1 driver data, sessions, lap times, and results—using OpenF1 data.

-----

## 🚀 Features

  - ✅ Track F1 events by year and location
  - ✅ View session info (FP1, FP2, Qualifying, Race, etc.)
  - ✅ Explore driver participation and lap times
  - ✅ Clean, modular FastAPI backend using SQLModel
  - ✅ PostgreSQL database
  - ✅ Frontend in React

-----

## 📁 Structure

```sh
F1Project/
├── backend/
│   ├── main.py           # ✅ FastAPI app entry point
│   ├── models/           # SQLModel ORM classes
│   ├── api/              # API route definitions
│   ├── crud/             # DB access logic
│   ├── db/               # DB definitions and utilities (engine, sessions, populators)
│   ├── schemas/          # Pydantic models for request/response
│   ├── utils/            # Utility files
│   └── __init__.py
├── frontend/
│   ├── app/              # Exports frontend code
│   ├── public/           # Frontend static files
│   ├── src/              # Source code
├── static/               # static files (icons)
├── .env                  # Environment variables (ignored in Git)
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
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

```bash
pip install -r requirements.txt
```

### 4\. Configure the Database

This project uses PostgreSQL for the database. You will need to have PostgreSQL installed and running.

1.  **Install PostgreSQL**: You can download and install PostgreSQL from the official website: [https://www.postgresql.org/download/](https://www.postgresql.org/download/)

2.  **Create a Database and User**: Create a new database and a user with privileges to access it. You can do this using the `psql` command-line tool or a graphical tool like pgAdmin.

3.  **Create a `.env` file**: In the root of the project, create a file named `.env` and add the following line, replacing 'user' with your username, 'password' with your password (if set) and 'database' with your database name:

    ```
    DATABASE_URL="postgresql://user:password@host:port/database"
    ```

### 5\. 🗄️ Populate the Database

The project pulls data from the OpenF1 API. To create the database tables and populate them, run:

```bash
python -m backend.db.update_db
```

### 6\. 🧪 Run the API Server

From the root directory (with the venv active), start the development server with:

```bash
uvicorn backend.main:app --reload
```

Now, you can access the API documentation:

  - **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
  - **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 7\. Install Frontend dependencies and start frontend server

```bash
cd ./frontend
npm install
npm start
```

Now, you can access the application at http://localhost:3000

-----

## 📌 TODO

  - [x] Add driver, session, and lap time API routes (in progress)
  - [x] Write tests using `pytest`
  - [x] Add simple Front-End
  - [x] Add session stats feature
  - [x] Convert to PostgreSQL
  - [ ] Deploy to a cloud service

-----

## 👨‍💻 Author

Built by **Estéfano Tuyama Gerassi**

-----

## ⚠️ License

This project is for educational purposes only. Data is sourced from the public [OpenF1 API](https://openf1.org/).
