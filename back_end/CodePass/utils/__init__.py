import base64
import collections
import os
from datetime import datetime

import xlrd
import joblib
from code_pass import settings
import chardet
import zipfile
import rarfile
import os
import sys
import numpy as np
import jpype
import os


# jar_path = os.path.join(os.path.abspath('.'), r'F:\jar\MathDemo.jar')   # jar包路径
# jvmPath_32 = r'D:\Program Files\Java\jre_32\bin\client\jvm.dll'     # jre路径
# jpype.startJVM(jvmPath_32, 'ea', '-Djava.class.path=%s' % jar_path)     # 启动虚拟机
# JPackage = jpype.JPackage('com.test')
# difference = JPackage.Main.sub(5, 1)
# print(difference)
# jpype.shutdownJVM()  # 关闭虚拟机

# def chengeChar(path):
#     '''处理乱码'''
#     path = path.rstrip('/').rstrip('\\')  # 去除路径最右边的/
#     file_name = os.path.split(path)[-1]  # 获取最后一段字符，准备转换
#     file_path = os.path.split(path)[0]  # 获取前面的路径，为rename做准备
#     try:  # 将最后一段有乱码的字符串转换，尝试过整个路径转换，不生效，估计是无法获取整个路径的编码格式吧。
#         new_name = file_name.encode('cp437').decode('gbk')
#
#     except UnicodeEncodeError as e:  # 先转换成Unicode再转换回gbk或utf-8
#
#         new_name = file_name.encode('utf-8').decode('utf-8')
#     except UnicodeDecodeError as e:
#         new_name = file_name.encode('cp437').decode('utf-8')
#     path2 = os.path.join(file_path, new_name)  # 将转换完成的字符串组合成新的路径
#     if not os.path.exists(path):
#         return path2
#     try:
#         os.renames(path, path2)  # 重命名文件
#     except:
#         print('renames error！！')
#     return path2
#
#
# def del_zip(path):
#     '''删除解压出来的zip包'''
#     path = chengeChar(path)
#     if path.endswith('.zip') or path.endswith('.rar'):
#         os.remove(path)
#     elif os.path.isdir(path):
#         for i in os.listdir(path):
#             file_path = os.path.join(path, i)
#             del_zip(file_path)  # 递归调用，先把所有的文件删除
#
#
# def unzip_file(z, unzip_path, _path):
#     new_dir = chengeChar(_path.split('.')[0].split('\\')[-1])
#     if not os._exists(os.path.join(unzip_path, new_dir)):
#         os.mkdir(os.path.join(unzip_path, new_dir))
#     unzip_path = os.path.join(unzip_path, new_dir)
#     '''解压zip包'''
#     z.extractall(path=unzip_path)
#     zip_list = z.namelist()  # 返回解压后的所有文件夹和文件list
#     z.close()
#     for zip_file in zip_list:
#         path = os.path.join(unzip_path, zip_file)
#         if os.path.exists(path):
#             unzip_file_main(path, os.path.split(path)[0])
#
#
# def unzip_file_main(path, unzip_path):
#     '''主逻辑函数'''
#     path = chengeChar(path)
#     if os.path.exists(path):
#         # unzip_path = os.path.split(path)[0]  # 解压至当前目录
#         if path.endswith('.zip'):
#             z = zipfile.ZipFile(path, 'r')
#             unzip_file(z, unzip_path, path)
#             os.remove(path)
#
#         elif path.endswith('.rar'):
#             r = rarfile.RarFile(path)
#             unzip_file(r, unzip_path, path)
#             os.remove(path)
#
#         elif os.path.isdir(path):
#             for file_name in os.listdir(path):
#                 path2 = os.path.join(path, file_name)
#                 if os.path.exists(path2):
#                     unzip_file_main(path2, os.path.split(path2)[0])
#         else:
#             print(path)
#     else:
#         print('the path is not exist!!!')
#
#
# 遍历文件夹，得到文件夹内全部的java文件
def walkFile(file):
    javafile_list = []
    for root, dirs, files in os.walk(file):
        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list

        # 遍历文件
        for f in files:
            if f.endswith(".java"):
                javafile_list.append(os.path.join(root, f))
    return javafile_list


if __name__ == '__main__':
    a = {"a": None}
    a = a.get("b")
    print(a)
    # clf = joblib.load(r"../lib/VotingClassifier.pkl")
    # a = np.array([0.1, 0.2, 0.3]).reshape(-1, 3)
    #
    # print(type(clf.predict(a).__getitem__(0)))

    # a = np.array([1,2,3])
    # b = np.array([5,5,6])
    # attribute_similarity = a.dot(b) / (np.linalg.norm(a) * np.linalg.norm(b))
    # print(a.dot(b))
    # print(np.linalg.norm(a))
    # print(np.linalg.norm(b))
    # print(attribute_similarity)
    # forder = r"C:\Users\w1579\Desktop\java实验\172041-exam1"
    # javafile = r"C:\Users\w1579\Desktop\java实验\172041-exam1\17204101\17204101.java"
    # print(os.path.sep.__len__())
    # print(javafile.find(forder))
    # print(javafile[forder.__len__()+1:])
    # file_data = xlrd.open_workbook(r"C:\Users\w1579\Desktop\用户信息.xls", encoding_override='utf-8')
    # table = file_data.sheet_by_index(0)
    # # print(table)
    # nrows = table.nrows  # 总行数
    # ncols = table.ncols  # 总列数
    # print(nrows)
    # print(ncols)
    # # sheet_row_val = table.row_values(3)
    # sheet_col_val = table.col_values(3)
    # # print(sheet_row_val)
    # print(sheet_col_val)
    # for item in sheet_col_val:
    #     print(type(item).__name__)
    # for i in range(1,table.nrows):
    #     print(table.row_values(i))

    # print(os.listdir(r"G:\python-study\test6\static\CodePass\file\temp_file"))
    # d4 = collections.OrderedDict()
    # d4["name"] = "wangshenyu"
    # print(d4.get("name"))
    # d4.__setitem__("a","b")
    # d4.__setitem__("a", "c")
    # d4.__delitem__("a")
    # print(d4)
    # print(None < 1)
    # a = [1,2,3,4,5]
    # print(a[-1])
    # group_file_list = []
    # forder = r"C:\Users\w1579\Desktop\java实验\172042第一次实验"
    # javafile_list = walkFile(forder)
    # onlyfiles = [os.path.join(forder, f) for f in os.listdir(forder) if f.endswith(".java")]
    # # onlyfolder = [f for f in os.listdir(forder) if os.path.isdir(os.path.join(forder, f))]
    # print(onlyfiles)
    # # print(onlyfolder)
    # for item in onlyfiles:
    #     javafile_list.remove(item)
    # for root, dirs, files in os.walk(forder):
    #
    #     for dir in dirs:
    #         # print(dir)
    #         group_name = root + os.path.sep + dir
    #         for f in javafile_list:
    #             if f.startswith(group_name):
    #                 group_file_list.append({"owner_folder": dir, "file": f})
    # for item in group_file_list:
    #     print(item)
    # folder = r"G:\\python-study\\test6\\static\\CodePass\\file\\unzip_file\\2020-05-01\\21-00-58\\17204201-潘奕霏"
    # a = ""
    # print(1.0 + 3)
    # a.split()
    # file_group_set = set()
    # file_group_set.add(1)
    # file_group_set.add(1)
    # file_group_set.add("瑜")
    # print(file_group_set.__contains__(1))
    # print(folder.split(os.path.sep)[-1])
    # jar_path = r"G:\python-study\test6\CodePass\lib\ASTExtractor-0.4.jar" # jar包路径
    # jvmPath_32 = jpype.getDefaultJVMPath()  # jre路径
    # print(jvmPath_32)
    # jpype.startJVM(jvmPath_32, '-ea', '-Djava.class.path=%s' % jar_path)  # 启动虚拟机
    # JPackage = jpype.JPackage('astextractor')
    # difference = JPackage.ASTExtractor.parseFile(r"G:\python-study\ASTExtractor-master\src\algorithm\GST.java", "JSON")
    # print(difference)
    # jpype.shutdownJVM()  # 关闭虚拟机

    # JClass = jpype.JClass('astextractor.ASTExtractor')
    # instance = JClass()
    # sum = instance.add(1, 2)
    # print(sum)
    # jpype.shutdownJVM()  # 关闭虚拟机
    # print("j薧期趓+?+apb澴".encode('gbk').decode('utf-8'))
#     # zip_path = r"C:\Users\w1579\Desktop\java实验\42班第四次试验.zip"  # 接收传入的路径参数
#     # print(chengeChar('java瀹為獙5.doc'))
#     # print(chengeChar('42班第四次试验.zip'))
#     # print(os.path.isdir('G:\\python-study\\test6\\static\\CodePass\\file\\unzip_file\\42班第四次试验\\42班第四次试验\\17204201-┼╦▐╚÷¡.zip'))
#     # print(os.listdir(zip_path))
#     # unzip_file_main(zip_path, r"G:\python-study\test6\static\CodePass\file\unzip_file")
#     # if zipfile.is_zipfile(r"G:\python-study\test6\static\CodePass\file\unzip_file"):  # 删除解压出来的压缩包
#     #     del_zip(os.path.splitext(zip_path)[0])  # 以后缀名切割
#     fencoding = chardet.detect("j薧期趓+?+apb澴".encode())
#     print(fencoding.get('encoding'))
#     print("j薧期趓+?+apb澴".encode().decode('gbk'))
#     print("a.txt".split(".")[0])
