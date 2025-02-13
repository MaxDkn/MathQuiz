# Utilisation d'une image Python optimisée
FROM python:3.11

# Définition du répertoire de travail
WORKDIR /app

# Copie des fichiers nécessaires
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste de l'application
COPY . .

# Exposition du port de FastAPI
EXPOSE 8000

# Lancement de l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
