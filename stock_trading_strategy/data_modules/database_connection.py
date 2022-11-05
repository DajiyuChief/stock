import pymysql


# 数据库
class MySQLDb:
    def __init__(self):
        self.conn = self.get_conn()  # 连接对象
        self.cursor = self.get_cursor()  # 游标对象

    # 获取连接对象
    def get_conn(self):
        conn = pymysql.connect(host='23.94.43.9',  # 连接名称，默认127.0.0.1
                               user='root',  # 用户名
                               passwd='qwer12345',  # 密码
                               port=3306,  # 端口，默认为3306
                               db='transaction',  # 数据库名称
                               charset='utf8'  # 字符编码
                               )
        return conn

    # 获取游标对象
    def get_cursor(self):
        cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
        return cursor

    def select_all(self, sql):
        """
        查询全部
        :param sql: 查询语句
        :return: [{},{}]
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def select_one(self, sql):
        """
        查询一个
        :param sql: 查询语句
        :return: {}
        """
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def commit_data(self, sql):
        """
        提交数据
        :param sql:
        :return:
        """
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            pass

    # 清空表数据
    def clean_table(self, sql):
        self.cursor.execute(sql)

    def __del__(self):
        self.cursor.close()
        self.conn.close()
