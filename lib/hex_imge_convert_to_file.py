# 君胜系统中的图片直接被转换成16进制数列的字符串形式
# 经查证,均为PNG 或 JPG格式
# source_string是十六进制数的字符串表示,以0x开头
def convert(source_string,target_file_name):
    write_pointer=0
    index=1
    temp_str=""
    extension="png"
    if str(source_string).startswith("0xFFD8FF"):
        extension="jpg"
    target=open(target_file_name+"."+extension,"wb")

    for c in source_string[2::1]:# 遍历每两个字符,转换成一个字节写入文件
        temp_str=temp_str+c
        if index%2==0:
            target.seek(write_pointer)
            target.write(int(temp_str,16).to_bytes(length=1, byteorder='big', signed=False))
            write_pointer+=1
                
            temp_str=""
        index+=1

    target.close()

if __name__=="__main__":
    convert(input("input:"),"test")
