import sqlite3


class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        """Достаем id юзера в базе по его user_id"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]


    def get_client_info(self, user_id):
        """Достаём описание пользователя по его user_id из базы"""
        result = self.cursor.execute("SELECT `description` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]


    def add_user(self, user_id):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
        return self.conn.commit()

    def add_record(self, user_id, side, note_from_client):
        """Создаем запись о доходах/расходах"""
        self.cursor.execute("INSERT INTO `records` (`user_id`, `side`, `note_from_client`) VALUES (?, ?, ?)",
                            (self.get_user_id(user_id),
                             side,
                             note_from_client))
        return self.conn.commit()

    def add_client_info(self, user_id, description):
        """Добавляем описание клиента"""
        self.cursor.execute("UPDATE users SET description=? where user_id=?",
                            (description, user_id))
        return self.conn.commit()

    def get_records(self, user_id):
        """Получаем документы"""

        result = self.cursor.execute("SELECT documents, side FROM records WHERE user_id = ? ORDER BY date",
                                     (self.get_user_id(user_id),))
        return result.fetchall()

    def update_record(self, user_id, side, documents, note_from_client):
        """Обноляем статус"""
        self.cursor.execute("UPDATE records SET side=?, note_from_client=? where user_id=? and documents=?",
                            (side, note_from_client, self.get_user_id(user_id), documents,))
        return self.conn.commit()

    def update_side(self, user_id, documents, side=0):
        """Обновляем статус 'мяча', возвращаем на сторону охотников"""
        self.cursor.execute("UPDATE records SET side=? where user_id=? and documents=?",
                            (side, self.get_user_id(user_id), documents, ))
        return self.conn.commit()


    # проверяем, нужно ли уведомить, сбрасывая флаг уведомления в 0 и возвращая user_id, которого нужно уведомить в случае единички в notify
    def check_notify(self):
        """Проверяем, нужно ли уведомить клиента, уведомляем и сбрасываем статус. Обновление раз в час"""
        list_to_update = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `notify` = 1")
        telegram_user_ID = list_to_update.fetchone()[0]
        # возвращаем id пользователей, которых нужно уведомить
        print(telegram_user_ID)
        self.cursor.execute("UPDATE `users` SET `notify` = 0 where `user_id` = ?", (telegram_user_ID,))
        self.conn.commit()
        print("update ok")
        return telegram_user_ID
        #for row in rows:
        #    print(row[0])
        #return row[0]
        # print (result)
        # user_id = result.fetchone()[0]
        # print (user_id)
        # if len(user_id) > 0:
        #     self.cursor.execute("UPDATE users SET notify = 0 where user_id=?", (user_id))
        #     return user_id
        # else:
        #     return 0

    # 31.03.2022
    # Задача - выгрузить список клиентов с их ID и идентификатором в словарь для публикации в чат
    # и дальнейшей обработки через команды чата по соответствию конкретному админу.
    # Пока фокус на выгрузке, здесь должен быть метод
    # выгрузки из БД данных из users - user_id (телеграм ID) и description (наименование фирмы)

    # выгружаем всех админов в паре кортежей ID и surname
    def getadmin_reply(self):
        """Достаем всех админов в базе для выгрузки в чат"""
        result = self.cursor.execute("SELECT id, surname FROM admins")
        return result.fetchall()

    # сначала выгружаем ID админа по его фамилии
    def get_admin_id(self, surname):
        """Достаем id админа в базе по его surname"""
        result = self.cursor.execute("SELECT `id` FROM `admins` WHERE `surname` = ?", (surname,))
        return str(result.fetchone()[0])

    # потом выгружаем все компании, которые за ним закреплены, из базы, по фамилии, с помощью get_admin_id
    def get_group_by_responsible(self, surname):
        """Получаем все компании данного бухгалтера"""

        result = self.cursor.execute("SELECT user_id, description FROM users WHERE responsible = ? ORDER BY join_date",
                                     (self.get_admin_id(surname),))
        return result.fetchall()


    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
