# 订单数据表字段映射

仅指导对应关系,数据格式需编程转换  

* 以下只展示君胜字段集和Ticketer字段集的交集,其他字段可忽略
* Ticketer字段与君胜字段可能存在一对多的关系,关系将在下表`君胜字段`列说明

|Ticketer字段|君胜字段|目标类型(Java)|默认值|
|:--|:--|:--|:--|
|uid|业务编号|String,唯一|<导入器生成的UUID>|
|status|工单状态|String,值在表`order-status`中|""|
|client|客户|String|""|
|phone|手机|String|""|
|contact|联系电话|String|""|
|address|地址|String|""|
|time|送修时间|long,订单创建日期的时间戳,当日0:00:00的时间戳,包含毫秒数|0|
|deadline|截止时间|long,订单交单日期的时间戳,当日0:00:00的时间戳,包含毫秒数|0|
|type|维修机器|String,值在表`order-types`中|""|
|source|服务类型|String|""|
|brand|品牌|String|""|
|label|系统单号|String|""|
|description|维修备注|String|""|
|secret|内部备注|String|""|
|workerRecord|维修师+维修师1|String|""|
|documents|img1 img2 img3 img4 img5 img6|String,Base64密文,由多条图片资料文件的路径组成,每条路径格式: <路径字符串>,单个订单中整个图片资料列表字符串格式: <单个图片路径>::<单个图片路径>::|""|
|review|型号+\n+维修费用|String|""|
|reviewTime|截止时间|long,订单回访日期的时间戳,当日0:00:00的时间戳,包含毫秒数|0|
|fault|故障原因|String|""|