# Wordly API

REST API backend for vocabulary learning and dictionary management (client: Android app).

## 🛠️ Tech Stack
- **Framework:** FastAPI
- **ORM & Database:** SQLAlchemy 2.x, PostgreSQL (`psycopg2-binary`)
- **Auth:** JWT tokens / password hashing
- **Deployment:** Render - API, Neon - Database



## 🚀 Quick start


### Prerequisites
* Python 3.10+ installed

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Orestver/Wordly_API.git
   cd Wordly_API
   ```

2. **Create and activate a virtual environment:**
    - Windows:
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```
    - Linux / macOS:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    
4. **Setup .evn:**
    create .evn file in the root folder of the project and fill up the values for 
    - SECRET_KEY - key for encryption
    - DATABASE_URL - your database url

5. **Run the api localy:**
    ```bash
    uvicorn main:app --reload


## API Documentation
    after you run local server you can check interactive documentation using this url in browser:
    - Swagger UI: http://127.0.0.1:8000/docs
    - ReDoc: http://127.0.0.1:8000/redoc 


## main endpoints 

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Check service status and database connectivity | No |
| `POST` | `/auth/register` | Register a new user account | No |
| `POST` | `/auth/login` | Log in and receive access/refresh tokens | No |
| `GET` | `/dictionaries` | List all dictionaries for the current user | Yes |
| `POST` | `/dictionaries` | Create a new dictionary | Yes |
| `GET` | `/dictionaries/{dict_id}/words` | Get words belonging to a specific dictionary | Yes |
| `POST` | `/dictionaries/{dict_id}/words` | Add a new word to a dictionary | Yes |
| `PUT` | `/words/{word_id}` | Update a word, translation, or learning progress | Yes |
| `DELETE` | `/words/{word_id}` | Delete a word from a dictionary | Yes |
| `GET` | `/quiz` | Fetch words for practice or quiz sessions | Yes |


Hope that was interesting for you :D