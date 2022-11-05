USE transaction;
DROP TABLE IF EXISTS `actual1`;

CREATE TABLE
`actual1` (

`id` int NOT NULL AUTO_INCREMENT COMMENT '交易序号',

`code` varchar(10) COMMENT '股票代码',

`date` varchar(8) COMMENT '交易日期',

`time` varchar(9) COMMENT '时分秒',

`type` bool COMMENT '交易类型',

`price`float COMMENT '成交价',

PRIMARY KEY (`id`)

) ENGINE = InnoDB DEFAULT CHARSET=utf8;



DROP TABLE IF EXISTS `actual2`;

CREATE TABLE
`actual2` (

`id` int NOT NULL AUTO_INCREMENT COMMENT '交易序号',

`code` varchar(10) COMMENT '股票代码',

`date` varchar(8) COMMENT '交易日期',

`time` varchar(9) COMMENT '时分秒',

`type` bool COMMENT '交易类型',

`price`float COMMENT '成交价',

PRIMARY KEY (`id`)

) ENGINE = InnoDB DEFAULT CHARSET=utf8;