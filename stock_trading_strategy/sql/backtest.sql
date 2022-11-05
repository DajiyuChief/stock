USE transaction;
DROP TABLE IF EXISTS `backtest1`;

CREATE TABLE
`backtest1` (

`id` int NOT NULL AUTO_INCREMENT COMMENT '交易序号',

`code` varchar(10) COMMENT '股票代码',

`date` varchar(8) COMMENT '交易日期',

`type` bool COMMENT '交易类型',

`price`float COMMENT '成交价',

`num` float COMMENT '本次交易成交股数',

`position` float COMMENT '交易后仓位股数',

`poundage` float COMMENT '手续费',

`stoploss` bool COMMENT '强制止损',

`total` float COMMENT '总资产',

PRIMARY KEY (`id`)

) ENGINE = InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `backtest2`;

CREATE TABLE
`backtest2` (

`id` int NOT NULL AUTO_INCREMENT COMMENT '交易序号',

`code` varchar(10) COMMENT '股票代码',

`date` varchar(8) COMMENT '交易日期',

`type` bool COMMENT '交易类型',

`price`float COMMENT '成交价',

`num` float COMMENT '本次交易成交股数',

`position` float COMMENT '交易后仓位股数',

`poundage` float COMMENT '手续费',

`stoploss` bool COMMENT '强制止损',

`total` float COMMENT '总资产',

PRIMARY KEY (`id`)

) ENGINE = InnoDB DEFAULT CHARSET=utf8;