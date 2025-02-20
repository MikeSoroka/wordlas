## DB initialization
Make sure, you have installed postgres
Go to wordlas/project/ in terminal and run:
<br>
`sudo -u postgres psql`
<br>
If you are using Windows, run open cmd as admin and simply run:
`psql -U postgres`
<br>
In appeared postgres console paste:
```
CREATE DATABASE wordlas;
CREATE USER admin WITH PASSWORD 'PostgresDevPassword';
GRANT ALL PRIVILEGES ON DATABASE wordlas TO admin;
\q
```

Then run:
```
python manage.py makemigrations
python manage.py migrate
```

As a result, PostgreSQL database should appear in the place, where your postgres is installed