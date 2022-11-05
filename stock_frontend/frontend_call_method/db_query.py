import easyquotation
import pymysql
quotation = easyquotation.use('sina')  # 新浪 ['sina'] 腾讯 ['tencent', 'qq']
# 数据库
class MySQLDb1:
    def __init__(self):
        self.conn = self.get_conn()  # 连接对象
        self.cursor = self.get_cursor()  # 游标对象

    # 获取连接对象
    def get_conn(self):
        conn = pymysql.connect(host='116.62.135.232',  # 连接名称，默认127.0.0.1
                               user='root',  # 用户名
                               passwd='iamnts',  # 密码
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
    def clean_table(self):
        self.cursor.execute("TRUNCATE TABLE `backtest1`;")

    def __del__(self):
        self.cursor.close()
        self.conn.close()


# 数据库
class MySQLDb2:
    def __init__(self):
        self.conn = self.get_conn()  # 连接对象
        self.cursor = self.get_cursor()  # 游标对象

    # 获取连接对象
    def get_conn(self):
        conn = pymysql.connect(host='116.62.135.232',  # 连接名称，默认127.0.0.1
                               user='root',  # 用户名
                               passwd='iamnts',  # 密码
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
    def clean_table(self):
        self.cursor.execute("TRUNCATE TABLE `backtest2`;")

    def __del__(self):
        self.cursor.close()
        self.conn.close()


def list_for_strategy1():
    db = MySQLDb1()
    sql = "SELECT * FROM backtest1 "
    res = db.select_all(sql)
    items = []
    for it in res:
        item = []
        item.append(it['date'])
        item.append(it['code'])
        item.append(getName(it['code']))
        if it['type'] == 1:
            item.append("买入")
        else:
            item.append("卖出")
        item.append(it['price'])
        item.append(it['num'])
        item.append(it['total'])
        items.append(item)

    return items


def list_for_strategy2():
    db = MySQLDb2()
    sql = "SELECT * FROM backtest2 "
    res = db.select_all(sql)
    items = []
    for it in res:
        item = []
        item.append(it['date'])
        item.append(it['code'])
        item.append(getName(it['code']))
        if it['type'] == 1:
            item.append("买入")
        else:
            item.append("卖出")
        item.append(it['price'])
        item.append(it['num'])
        item.append(it['total'])
        items.append(item)

    return items

# 股票代码格式转换
def stock_code_convert(stock_code):
    lst = stock_code.split('.')
    type = lst[1].lower()
    return type + lst[0]

# 获取股票名称
def getName(stock_code):
    code = stock_code_convert(stock_code)
    data = quotation.real(code)[stock_code[:-3]]['name']
    return data


# list_for_strategy2()