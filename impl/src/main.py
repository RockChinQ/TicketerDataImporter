import base64
import time

import pymssql

import getProperties
import json

'''
{
    "sqls":[
        "<导入过程中要执行的SQL>"
    ],
    "data":{
        "amount":<数量>,
        "data":[
            {
                "id":<id>,
                "uid":"<uid>",
                ...每条数据的各个字段(按照orders表的字段命名)...
            }
        ]
    }
}
'''

# 一次多少个
PAGE_LIMIT = 200
# 要导入的表的名称
TARGET_DATABASE_TABLE_NAME = "orders"
properties_path = "config.properties"

insert_sql = ''
# 总计数
count = 0
# 单次计数（PAGE_LIMIT）
instance_count = 0
# 文件名标识
f_tag = 1
# 图片标识
img_tag = 1
# 最终dict
instance_overall_dict = {}
# 单次sql
instance_sql_list = []
instance_data_dict = {}
instance_sub_data_dict = {}
instance_data_list = []


# 字段
params_tuple = ('uid', 'status', 'client', 'phone', 'contact', 'address', 'time', 'deadline', 'type', 'source',
                'brand', 'label', 'description', 'secret', 'workerRecord',
                'documents', 'review', 'reviewTime', 'fault')


def fill(params, values):
    global insert_sql

    insert_sql += '('
    for p, v in zip(params, values):
        try:
            decoded_v = v.encode("latin1").decode("gbk")
            if decoded_v == 'NULL':
                decoded_v = ''
            # special fields check

            if p == 'time' or p == 'deadline' or p == 'reviewTime':
                # 2017年6月11日9时17分55秒
                try:
                    timeArray = time.strptime(decoded_v, "%Y年%m月%d日%H时%M分%S秒")
                    instance_sub_data_dict[p] = int(time.mktime(timeArray)) * 1000
                except ValueError:
                    timeArray = time.strptime(decoded_v, "%Y年%m月%d日%H时%M分")
                    instance_sub_data_dict[p] = int(time.mktime(timeArray)) * 1000
                except BaseException:
                    decoded_v = 0
                    instance_sub_data_dict[p] = decoded_v
                # insert_sql += str(int(time.mktime(timeArray)) * 1000) + ','
            else:
                instance_sub_data_dict[p] = decoded_v
                # insert_sql += '\'' + decoded_v + '\','
        except BaseException:
            # insert_sql += '\'' + '' + '\','
            if p == 'deadline' or p == 'time' or p == 'reviewTime':
                instance_sub_data_dict[p] = 0
            else:
                instance_sub_data_dict[p] = ""
    instance_data_list.append(instance_sub_data_dict)
    # insert_sql += '),'


def reset_sql_for_insert():
    global insert_sql
    insert_sql = ""
    insert_sql = 'INSERT INTO ' + TARGET_DATABASE_TABLE_NAME + '('
    for p1 in params_tuple:
        insert_sql += p1 + ','
    insert_sql += ') VALUES'


def on_finish_single_task():
    global instance_count, insert_sql, instance_sql_list, instance_data_list, f_tag

    print('装配文件' + str(f_tag) + '...', end='')
    instance_count = 0
    insert_sql = insert_sql[:-1]
    insert_sql += ';'
    instance_sql_list.append(insert_sql)

    # 装配一级'data'字段中的内容
    instance_data_dict['data'] = instance_data_list
    instance_data_dict['amount'] = len(instance_data_list)

    # 总装配
    instance_overall_dict['data'] = instance_data_dict
    # instance_overall_dict['sqls'] = instance_sql_list

    f = open('output_' + str(f_tag) + '.txt', 'w', encoding="UTF-8")
    f.write(json.dumps(instance_overall_dict, ensure_ascii=False))
    f.flush()

    f_tag += 1

    instance_data_list = []
    instance_sql_list = []
    reset_sql_for_insert()

    print("OK")


# 君胜系统中的图片直接被转换成16进制数列的字符串形式
# 经查证,均为PNG 或 JPG格式
# source_string是十六进制数的字符串表示,以0x开头
def imgAsFile(source_string, target_file_name):
    try:
        write_pointer = 0
        index = 1
        temp_str = ""
        extension = "png"
        if str(source_string).startswith("0xFFD8FF"):
            extension = "jpg"
        target = open(target_file_name + "." + extension, "wb")

        for c in source_string[2::1]:  # 遍历每两个字符,转换成一个字节写入文件
            temp_str = temp_str + c
            if index % 2 == 0:
                target.seek(write_pointer)
                target.write(int(temp_str, 16).to_bytes(length=1, byteorder='big', signed=False))
                write_pointer += 1

                temp_str = ""
            index += 1

        target.close()
    except BaseException:
        print(source_string)
    return target_file_name + "." + extension


if __name__ == '__main__':
    prop = getProperties.Properties(properties_path).getProperties()
    print(prop)

    # 连接到mssql
    db = pymssql.connect(server=prop['db_address'], user=prop['db_user'], password=prop['db_password'])
    cursor = db.cursor(as_dict=True)
    db.autocommit(True)

    # properties文件配置获取
    db_database = prop['db_database']
    begin = int(prop['beginning'])
    end = int(prop['ending'])
    count = begin

    print("从数据库抓取数据...", end='')
    # 得到mssql所有的数据
    sql = "SELECT * FROM {}.dbo.业务管理".format(db_database)
    # sql = "SELECT [COLUMN_NAME] FROM [INFORMATION_SCHEMA].[Columns] WHERE [TABLE_NAME] = 'junsheng.dbo.业务管理'"
    cursor.execute(sql)
    data = cursor.fetchall()
    print("OK")

    # 初始化sql串
    reset_sql_for_insert()

    '''
    orders表中的artifacts、techWorker字段请直接留空
    将填到status、type字段中的值,若不包含在强制格式要求要求的表中,需要添加
    '''
    for i in data:
        if count == end:
            break
        if count >= begin:
            instance_sub_data_dict = {}

            # packaging 'documents' field
            field_documents_img = ''
            if i['img1'] != 'NULL':
                field_documents_img += imgAsFile(i['img1'], 'img_'+str(img_tag)+'_'+'1') + '::'
            if i['img2'] != 'NULL':
                field_documents_img += imgAsFile(i['img2'], 'img_'+str(img_tag)+'_'+'2') + '::'
            if i['img3'] != 'NULL':
                field_documents_img += imgAsFile(i['img3'], 'img_'+str(img_tag)+'_'+'3') + '::'
            if i['img4'] != 'NULL':
                field_documents_img += imgAsFile(i['img4'], 'img_'+str(img_tag)+'_'+'4') + '::'
            if i['img5'] != 'NULL':
                field_documents_img += imgAsFile(i['img5'], 'img_'+str(img_tag)+'_'+'5') + '::'
            if i['img6'] != 'NULL':
                field_documents_img += imgAsFile(i['img6'], 'img_'+str(img_tag)+'_'+'6') + '::'
            if field_documents_img != '':
                field_documents_img = base64.b64encode(field_documents_img.encode('utf-8'))
                print(str(field_documents_img))

            field_worker_record = ''
            if i["维修师"] != 'NULL':
                field_worker_record += i["维修师"]+'+'
            else:
                field_worker_record += '+'
            if i["维修师1"] != 'NULL':
                field_worker_record += i["维修师1"]

            values_tuple = (i["业务编号"], i["工单状态"], i["客户"], i["手机"], i["联系电话"], i["地址"], i["送修时间"],
                            i["截止时间"], i["维修机器"], i["服务类型"], i["品牌"], i["系统单号"], i["维修备注"],
                            i["内部备注"], field_worker_record, str(field_documents_img),
                            str(i["型号"]) + '\n' + str(i["维修费用"]), i["截止时间"], i["故障原因"])
            fill(params_tuple, values_tuple)
        img_tag += 1
        count += 1
        instance_count += 1
        if instance_count == PAGE_LIMIT:
            on_finish_single_task()

    # 剩下来的数据的处理
    if instance_count > 0:
        on_finish_single_task()
