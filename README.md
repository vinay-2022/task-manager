TASK-MANAGER → README.md

## ⚙️ Setup Instructions

### 1. Clone the repository
git clone https://github.com/vinay-2022/task-manager.git
cd task-manager

### 2. Install dependencies
pip install -r requirements.txt

### 3. Create PostgreSQL database
CREATE DATABASE taskmanager;

### Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password TEXT NOT NULL
);

### Tasks Table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    description TEXT,
    priority VARCHAR(20),
    status VARCHAR(20),
    user_id INTEGER
);


### 4. Run the project
python app.py

## 🔗 Links
GitHub: https://github.com/vinay-2022/task-manager