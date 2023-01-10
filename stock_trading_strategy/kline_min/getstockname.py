# 将股票名保存到数据库中
import MySQLdb
import pandas as pd
import tushare as ts
from sqlalchemy import create_engine, String, Column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 初始化pro接口
pro = ts.pro_api('f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108')
engine = create_engine('mysql+pymysql://root:qwer12345@23.94.43.9:3306/stock?charset=utf8')

conn = MySQLdb.connect(
    host='23.94.43.9',
    port=3306,
    user='root',
    password='qwer12345',
    database='stock'
)




def pull_stock_name():
    # 拉取股票数据
    df = pro.stock_basic(**{
        "ts_code": "",
        "name": "",
        "exchange": "",
        "market": "",
        "is_hs": "",
        "list_status": "",
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "name"
    ])
    return df


def pull_fun_name():
    df = pro.fund_basic(market='E')
    df2 = df[['ts_code','name']]
    return df2


def create_table():
    cursor = conn.cursor()
    sql = "CREATE TABLE `stockname` ( 'index' varchar(10) , `ts_code` varchar(20) COMMENT '代码', `name` varchar(20) COMMENT '名称', PRIMARY KEY (`ts_code`) ) ENGINE = InnoDB DEFAULT CHARSET=utf8; "
    cursor.execute(sql)


def insert_info():
    #数据插入表中
    con = engine.connect() #使用sqlalchemy的engine类型
    df1 = pull_stock_name()
    df2 = pull_fun_name()
    df = pd.concat([df1,df2], ignore_index=True)
    df.to_csv('name.csv')
    # df.to_sql(name='stockname', con=con, if_exists='replace')
    con.close()


def get_name(stockcode):
    #从表中获取姓名
    cursor = conn.cursor()
    sql = "select name from stockname where ts_code = '%s';" % stockcode
    cursor.execute(sql)
    data = cursor.fetchall()
    return data[0][0]
