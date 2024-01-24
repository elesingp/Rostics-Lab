import psycopg2

class Database:
    def __init__(self, dbname, user, host):
        self.dbname = dbname
        self.user = user
        self.host = host
    
    def connect(self):
        # Параметры подключения к базе данных
        conn = psycopg2.connect(
            dbname=self.dbname, 
            user=self.user, 
            host=self.host
        )
        return conn

    def insert(self, cur, table_name, data, columns):
        # SQL-запрос для вставки данных
        placeholders = ', '.join(['%s'] * len(data[0]))  # Создаем placeholders для значений
        column_names = ', '.join(columns)  # Колонки, в которые будут вставляться данные
        insert_query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders});"
        print(data[0], '=====')

        # Вставка данных в таблицу
        for row in data:
            cur.execute(insert_query, row)

    def select(self, cur, table_name):
        # SQL-запрос для выбора данных
        select_query = f"SELECT * FROM {table_name};"

        # Выполнение запроса SELECT
        cur.execute(select_query)

        # Получение и вывод результатов
        rows = cur.fetchall()
        for row in rows:
            print(row)

    def run_table(self, table_name, data, columns):
        connection = self.connect()

        # Создаем курсор для выполнения операций с базой данных
        cursor = connection.cursor()

        self.insert(cursor, table_name, data, columns)
        self.select(cursor, table_name)

        # Закрываем соединение
        cursor.close()
        connection.close()




