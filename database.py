import psycopg2


class DataBase:
    def __init__(self, dbname, user, password, host, port):
        """Класс для подключения к базе данных"""
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.con = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.con.autocommit = True
        self.cursor = self.con.cursor()
