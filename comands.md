    #generate migration
        activate env before launch alembic
        alembic revision --autogenerate -m "Initial migration 3"
    #run migration
        alembic upgrade head
    #conexion to DB alembic.ini
        sqlalchemy.url = mysql+pymysql://root:rootpassword@127.0.0.1:3389/fastapi_db_petID
    #activate venv
        source venv/bin/activate