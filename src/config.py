import os
from dotenv import load_dotenv

# Carga las variables del archivo .env (que NO se sube a GitHub)
load_dotenv()

# --- BASE DE DATOS ---
# Fíjate que quité la contraseña real del segundo argumento.
# Ahora, si no existe el .env, la variable valdrá None (o lo que pongas de placeholder).
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
# Host local no es secreto grave
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
# Puerto estándar no es secreto
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
# Nombre de DB no suele ser crítico
DB_NAME = os.getenv("POSTGRES_DB", "solaris_db")

# Construcción de la URL
# Si DB_PASS es None, esto fallará al intentar conectar, lo cual es BUENO (fail fast).
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

INPUT_DIR = os.getenv("INPUT_DIR", "/app/data/input")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "/app/data/processed")
