# stock_trading_system
设置数据库密码
user='root',  # 用户名
passwd='root',  # 密码
依次运行sql目录下的init.sql,backtest.sql,suggest.sql

数据表内容说明：
backtest1保存策略一回测交易记录
backtest2保存策略二回测交易记录
actual1保存系统推荐的策略一交易记录
actual2保存系统推荐的策略二交易记录

以下是代码模块说明
每个.py文件底部都有主方法的调用示例


回测（策略一策略二采用相同的接口形式，唯一的区别在于percent的含义）
策略一
backtest.py文件下的backtest1(span, stock_code, principal, percent, stoploss, isCharge, isWhole)方法
参数依次为：
回测周期 如：30
股票代码
初始本金
MACD柱值变化检测比率
强制止损比例
是否计算手续费 True:计算手续费 False:不计算手续费
是否采用全仓策略 True:全仓策略 False:加仓策略
交易记录保存在数据库中


策略二
backtest2.py文件下的backtest2(span, stock_code, principal, percent, stoploss, isCharge, isWhole)方法
参数依次为：
回测周期 如：30
股票代码
初始本金
RSI-6变化比率
强制止损比例
是否计算手续费 True:计算手续费 False:不计算手续费
是否采用全仓策略 True:全仓策略 False:加仓策略
交易记录保存在数据库中


实时交易（策略一策略二采用相同的接口形式，唯一的区别在于percent的含义）
策略一
trading.py文件下的real_time_trading(stock_code, percent)方法
参数依次为：
股票代码
MACD柱值变化检测比率
返回两个bool值，第一个代表是否看多，第二个代表是否看空
交易推荐记录保存在数据库中

策略二
trading2.py文件下的real_time_trading(stock_code, percent)方法
参数依次为：
股票代码
RSI-6变化比率
返回两个bool值，第一个代表是否看多，第二个代表是否看空
交易推荐记录保存在数据库中