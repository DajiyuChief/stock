USE transaction;
DROP TABLE IF EXISTS `history`;

CREATE TABLE
`history` (

`id` int NOT NULL AUTO_INCREMENT COMMENT '记录序号',

`code` varchar(10) COMMENT '股票代码',

`date` varchar(8) COMMENT '日期',

`open`float COMMENT '开盘价',

`high`float COMMENT '最高价',

`low`float COMMENT '最低价',

`close`float COMMENT '收盘价',

PRIMARY KEY (`id`)

) ENGINE = InnoDB DEFAULT CHARSET=utf8;



