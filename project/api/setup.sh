sudo -u postgres psql
CREATE DATABASE wordlas;
CREATE USER admin WITH PASSWORD 'your_password';  # using 'admin' as user
GRANT ALL PRIVILEGES ON DATABASE wordlas TO admin;
\q
