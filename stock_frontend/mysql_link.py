
import pymysql

class MysqlData():
    def __init__(self,host='116.62.135.232',username='root',password='root',database='stock_db'):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.db = pymysql.connect(host=self.host, user=self.username, password=self.password, database=self.database, charset="utf8")
        self.cursor = self.db.cursor()

    def register(self, user_name, user_pwd):

        sql = 'select user_name from user_info where user_name = "{}"'.format(user_name)
        self.cursor.execute(sql)
        if self.cursor.rowcount:
            print('该帐号已注册！')
            return
        try:
            sql = "insert into user_info (user_name, user_pwd) values('%s','%s')" % (user_name, user_pwd)
            self.cursor.execute(sql)
            self.db.commit()
            print("注册成功")
        except:
            print('注册失败！')
        finally:
            self.db.close()

    def login(self, user_name, password):
        sql = 'select user_name,user_pwd from user_info where user_name = "{}"'.format(user_name)
        self.cursor.execute(sql)
        if not self.cursor.rowcount:
            print("用户不存在")
            return False
        else:
            num = self.cursor.fetchone()[1]
            if num == password:
                print('登录成功')
                return True
            else:
                print('登录失败')
                return False

    def insert_info(self, pstr, pass_time):
            sql = "insert into user_info (pstr, pass_time) values('%s','%s')" % (pstr, pass_time)
            self.cursor.execute(sql)
            self.db.commit()
    def select_info(self, pstr, pass_time):
        sql = 'select pstr,pass_time from user_info where pstr = "{}"'.format(pstr)
        self.cursor.execute(sql)
        if not self.cursor.rowcount:
            self.insert_info(pstr, pass_time)
        else:
            num = self.cursor.fetchone()[1]
            return num
            print(num)

if __name__ == '__main__':
   my = MysqlData()#"116.62.135.232", "root", "root", "stock_db")
   my.login('1','1')
