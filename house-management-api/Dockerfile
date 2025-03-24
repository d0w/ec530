# FROM python:3.11-slim

# WORKDIR /app

# # Install SQLite and other dependencies
# RUN apt-get update && \
#     apt-get install -y sqlite3 && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# # Copy requirements and install dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy application code
# COPY . .

# # Initialize SQLite database in the volume directory
# RUN mkdir -p /data

# # # Create a script to initialize the database
# # RUN echo '#!/bin/bash\n\
# # if [ ! -f /data/house_management.db ]; then\n\
# #   echo "Creating new database..."\n\
# #   sqlite3 /data/house_management.db < init_db.sql\n\
# # else\n\
# #   echo "Using existing database"\n\
# # fi\n\
# # exec uvicorn src.main:app --host 0.0.0.0 --port 8000 "$@"\n'\
# # > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# # # Create an SQL script to initialize the database schema
# # RUN echo 'CREATE TABLE IF NOT EXISTS houses (\n\
# #   id INTEGER PRIMARY KEY AUTOINCREMENT,\n\
# #   name TEXT NOT NULL,\n\
# #   address TEXT NOT NULL,\n\
# #   gps TEXT NOT NULL,\n\
# #   owner INTEGER NOT NULL,\n\
# #   occupants TEXT\n\
# # );\n\
# # \n\
# # CREATE TABLE IF NOT EXISTS users (\n\
# #   id INTEGER PRIMARY KEY AUTOINCREMENT,\n\
# #   name TEXT NOT NULL,\n\
# #   username TEXT UNIQUE NOT NULL,\n\
# #   email TEXT UNIQUE NOT NULL,\n\
# #   phone TEXT,\n\
# #   privilege TEXT DEFAULT "user"\n\
# # );\n\
# # \n\
# # CREATE TABLE IF NOT EXISTS rooms (\n\
# #   id INTEGER PRIMARY KEY AUTOINCREMENT,\n\
# #   name TEXT NOT NULL,\n\
# #   floor INTEGER NOT NULL,\n\
# #   sqft REAL,\n\
# #   house_id INTEGER NOT NULL,\n\
# #   type TEXT,\n\
# #   FOREIGN KEY (house_id) REFERENCES houses (id)\n\
# # );\n\
# # \n\
# # CREATE TABLE IF NOT EXISTS devices (\n\
# #   id INTEGER PRIMARY KEY AUTOINCREMENT,\n\
# #   name TEXT

# EXPOSE 8000

# # Use the entrypoint script to initialize the database and start the application
# CMD ["uvicorn", "src.main:app", "--host"]