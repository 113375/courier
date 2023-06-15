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

    def query(self, query, fetch=False):
        try:
            self.cursor.execute(query)
            if fetch:
                return self.cursor.fetchall()
            else:
                return True
        except Exception as e:
            return f"Ошибка: {e}"

    def check_chat_id(self, id):
        return self.query(f"SELECT * FROM client WHERE chat_id={int(id)}", True)

    def insert_into_users(self, id):
        return self.query(f"INSERT INTO client (chat_id) VALUES ({int(id)})")
