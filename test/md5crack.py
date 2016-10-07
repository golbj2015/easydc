#!/usr/bin/env python
# encoding=utf8

import string  
import hashlib  

md5input=raw_input("请输入md5：\n")  
md5input=md5input.lower()  
apt=string.printable[:-38]  

print apt
def crack(s,num):  
    m=hashlib.md5()  
    m.update(s)  
    md5temp=m.hexdigest()  

    print s, md5temp
    if md5temp==md5input:  
        print 'crack success:',s,md5temp
        exit(-1)  
    if len(s)==num:  
        return  
    for i in apt:  
        crack(s+i,num)  

myinput=1    #生成字符的位数  
for j in range(1,myinput):  
    crack("",j)  
