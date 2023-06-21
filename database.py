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

    def insert_into_client_chat_id(self, id):
        return self.query(f"INSERT INTO client (chat_id) VALUES ({int(id)})")

    def insert_into_client_name(self, id, name):
        return self.query(f"UPDATE client set name='{name}' WHERE chat_id={int(id)}")

    def insert_into_client_courier(self, id, is_courier=False):
        return self.query(f"UPDATE client SET is_courier={is_courier} WHERE chat_id={int(id)}")

    def delete_delivery(self, id):
        return self.query(
            f"DELETE FROM delivery WHERE delivery_id = (SELECT max(delivery_id) FROM delivery WHERE user_id={id})")

    def add_location_from(self, id, latitude, longitude):
        """В базе данных сначала широта, потом долгота, разделитель _"""
        coords = "_".join(list(map(str, [latitude, longitude])))
        delivery_id = self.query("SELECT max(delivery_id) FROM delivery", True)
        if delivery_id[0][0] is None:
            delivery_id = 0
        else:
            delivery_id = int(delivery_id[0][0]) + 1
        return self.query(
            f"INSERT INTO delivery (delivery_id, user_id, delivery_from) VALUES ({delivery_id}, {id}, '{coords}')")

    def get_delivery_id(self, id):
        return int(self.query(f"SELECT MAX(delivery_id) from delivery WHERE user_id={id}", True)[0][0])

    def add_location_to(self, delivery_id, latitude, longitude):
        """В базе данных сначала широта, потом долгота, разделитель _"""
        coords = "_".join(list(map(str, [latitude, longitude])))
        return self.query(
            f"UPDATE delivery set delivery_to='{coords}' WHERE delivery_id={delivery_id}")

    def add_description(self, delivery_id, text):
        return self.query(f"UPDATE delivery set description='{text}' WHERE delivery_id={delivery_id}")

    def get_couriers_chat_id(self):
        return self.query("SELECT chat_id FROM client WHERE is_courier=true", True)

    def get_delivery_info(self, id):
        return self.query(f"SELECT * FROM delivery WHERE delivery_id={id}", True)[0]

    def add_courier_to_delivery(self, delivery_id, courier_id):
       return self.query(f"UPDATE delivery set courier_id={courier_id} WHERE delivery_id={delivery_id}", True)