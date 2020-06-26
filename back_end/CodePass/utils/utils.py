import os
import random
import threading
import types
import jpype
import json
import os
import glob
import zipfile
import rarfile
import datetime
import joblib
import numpy as np
from copy import deepcopy
from django.conf import settings
from django.db.models import Q
from xlwt import Workbook

from CodePass.serializers import detect_recordSerializer, file_groupSerializer, fileSerializer, similaritySerializer, \
    matchesSerializer

jar_path = settings.JAR_PATH  # jar包路径
from CodePass.models import detect_record, file, file_group, file_group_file, similarity, matches, similarity_matches, \
    record_group, class_table, file_class, attribute, method, class_attribute, class_method, user

# jar_path = r"../lib/ASTExtractor-0.4.jar"
# jar_property_file = r"../setting/ASTExtractor.properties"
jar_property_file = settings.PROPERTY_FILE_PATH
jvmPath_32 = jpype.getDefaultJVMPath()  # jre路径
jpype.startJVM(jvmPath_32, '-ea', '-Djava.class.path=%s' % jar_path)  # 启动虚拟机
rarfile.UNRAR_TOOL = settings.UNRAR_PATH
# rarfile.UNRAR_TOOL = r"../lib/UnRAR.exe"

lock = threading.Lock()
# ast_extractor = ASTExtractor(r"../lib/ASTExtractor-0.4.jar",
#                              r"G:/python-study/test6/CodePass/setting/ASTExtractor.properties")
null_javaFile_list = []
JPackage = jpype.JPackage('astextractor')
JPackage.ASTExtractorProperties.setProperties(jar_property_file)
clf = joblib.load(settings.PREDICT_MODEL)


def parse_javafile_to_ast(file_path, representation):
    """
    将单个java文件解析成语法树
    :param file_path: 待解析文件路径
    :param representation: ast表示形式：JSON or XML
    :return:
    """
    # print("filepath:"+file_path)
    JPackage = jpype.JPackage('astextractor')
    ast = JPackage.ASTExtractor.parseFile(file_path, representation)
    return ast


def gst(text, pattern, minlen):
    """
    GST算法，求两个字符串的匹配子串集合
    :param text: 文本串
    :param pattern: 模式串
    :param minlen: 最小匹配长度
    :return:
    """
    text = text.replace("_", "")
    pattern = pattern.replace("_", "")
    JClass = jpype.JClass('algorithm.GST')
    instance = JClass()
    # sum = instance.add(1, 2)
    result = instance.gst2(text, pattern, minlen)
    return result


def JVM_close():
    jpype.shutdownJVM()  # 关闭虚拟机


def compute_attribute_similarity(filetable1, filetable2):
    """
    计算两个java文件的属性相似度
    :param filetable1:
    :param filetable2:
    :return:
    """
    # 方法一： 利用余弦相似度，计算两个文件的属性相似度，其效果不太好
    # a = np.array(
    #     [filetable1['attribute_num'], filetable1['method_num'], filetable1['for_num'], filetable1['switch_num'],
    #      filetable1['if_num'], filetable1['while_num'], filetable1['do_while_num'], filetable1['express_state_num'],
    #      filetable1['var_sate_num']])
    # b = np.array(
    #     [filetable2['attribute_num'], filetable2['method_num'], filetable2['for_num'], filetable2['switch_num'],
    #      filetable2['if_num'], filetable2['while_num'], filetable2['do_while_num'], filetable2['express_state_num'],
    #      filetable2['var_sate_num']])
    # attribute_similarity = a.dot(b) / (np.linalg.norm(a) + np.linalg.norm(b))

    # 方法二： 利用 相等属性条数/总属性条数 ，计算的属性相似度更为准确。
    equ_num = 0
    if filetable1['attribute_num'] == filetable2['attribute_num']:
        equ_num = equ_num + 1
    if filetable1['method_num'] == filetable2['method_num']:
        equ_num = equ_num + 1
    if filetable1['for_num'] == filetable2['for_num']:
        equ_num = equ_num + 1
    if filetable1['switch_num'] == filetable2['switch_num']:
        equ_num = equ_num + 1
    if filetable1['if_num'] == filetable2['if_num']:
        equ_num = equ_num + 1
    if filetable1['while_num'] == filetable2['while_num']:
        equ_num = equ_num + 1
    if filetable1['do_while_num'] == filetable2['do_while_num']:
        equ_num = equ_num + 1
    if filetable1['express_state_num'] == filetable2['express_state_num']:
        equ_num = equ_num + 1
    if filetable1['var_sate_num'] == filetable2['var_sate_num']:
        equ_num = equ_num + 1
    return equ_num / 9


def compute_struct_similarity(result_table1, result_table2):
    """
    计算两个java文件ast语法树结构的相似度
    :param result_table1:
    :param result_table2:
    :return:
    """
    ast1_xml = result_table1['result_table']['ast_xml']
    ast2_xml = result_table2['result_table']['ast_xml']
    JPackage = jpype.JPackage('helpers')

    result = JPackage.SimilarityCalHelpers.compute_ast_struct_similarity(ast1_xml, ast2_xml)
    # 若得不到结构相似度计算结果，结束当前线程
    if result is None:
        print("异常：result_table1:", result_table1['java_file'])
        print("异常：result_table2:", result_table2['java_file'])
        sys.exit(0)
    return parse_jsonStr_to_dict(result)


def compute_text_similarity(file_table1, file_table2):
    """
    计算两个java文件的文本相似度
    :param file_table1:
    :param file_table2:
    :return:
    """
    file_table1_token = file_table1['tokens']
    file_table2_token = file_table2['tokens']
    similarity = 0
    # print("file_table1_token:" + file_table1_token)
    # print("file_table2_token:" + file_table2_token)
    result = gst(file_table1_token, file_table2_token, 2)
    # print("result:"+result)
    strList = result.split('\n')[0:-1]
    # 两个字符串匹配的子串集中子串的长度之和
    sub_str_counter = 0
    try:
        for str in strList:
            # Match{m=2922, n=1565, j=10}
            str = str[str.find('j=') + 2: str.find('}')]
            sub_str_counter = sub_str_counter + int(str)
            # print(str)
            if (file_table1_token.__len__() + file_table2_token.__len__()) == 0:
                similarity = 0
            else:
                similarity = (sub_str_counter * 2) / (file_table1_token.__len__() + file_table2_token.__len__())
    except Exception as e:
        print(e)
        print(strList)

    return similarity


# 解析类的属性 file_class_table['class_table'].__setitem__('attribute_table%d' % i, attribute_table)
def parse_FieldDeclaration(FieldDeclaration):
    """
    解析类的属性
    :param FieldDeclaration:ast中属性节点
    :return:
    """
    attribute_table_list = []
    attribute_table = {'type': '', 'name': '', 'value': ''}

    # 解析属性的类型
    FieldDeclaration_keys = list(FieldDeclaration.keys())
    FieldDeclaration_keys.remove('VariableDeclarationFragment')
    if FieldDeclaration_keys[0] == 'SimpleType':
        attribute_table['type'] = parse_SimpleType(FieldDeclaration.get('SimpleType'))
    else:
        attribute_table['type'] = FieldDeclaration.get(FieldDeclaration_keys[0])
    # 解析属性的名字与值
    # 解决int num,grade;
    VariableDeclarationFragments = FieldDeclaration.get('VariableDeclarationFragment')
    attr_name_val = ""
    if type(VariableDeclarationFragments).__name__ == 'str':
        attr_name_val = VariableDeclarationFragments.split('=')
        attribute_table['name'] = attr_name_val[0]
        attribute_table['value'] = ''
        if attr_name_val.__len__() == 2:
            attribute_table['value'] = attr_name_val[1]
        attribute_table_list.append(attribute_table)
    elif type(VariableDeclarationFragments).__name__ == 'list':
        for VariableDeclarationFragment in VariableDeclarationFragments:
            attr_name_val = VariableDeclarationFragment.split('=')
            attribute_table['name'] = attr_name_val[0]
            attribute_table['value'] = ''
            if attr_name_val.__len__() == 2:
                attribute_table['value'] = attr_name_val[1]
            attribute_table_list.append(attribute_table)

    return attribute_table_list


# 解析方法的参数
def parse_SingleVariableDeclaration(SingleVariableDeclaration):
    """
    解析方法的参数
    :param SingleVariableDeclaration: ast中的SingleVariableDeclaration节点
    :return:
    """
    # 得到方法参数的名字
    para_name = SingleVariableDeclaration.get('SimpleName')
    # 得到方法参数的类型
    SingleVariableDeclaration_keys = list(SingleVariableDeclaration.keys())
    SingleVariableDeclaration_keys.remove('SimpleName')
    if SingleVariableDeclaration_keys[0] == 'SimpleType':
        para_type = SingleVariableDeclaration.get('SimpleType').get('SimpleName')
    else:
        para_type = SingleVariableDeclaration.get(SingleVariableDeclaration_keys[0])
    return para_type + para_name


# 解析一个变量的类型
"""
{
    'QualifiedName': {
      'QualifiedName': {
        'SimpleName': ['java', 'io']
      },
      'SimpleName': 'File'
    }
  }
"""


# 解析变量声明的变量类型
def parse_SimpleType(SimpleType):
    """
    解析变量声明的变量类型
    :param SimpleType:
    :return:
    """
    simple_name = ''
    QualifiedName = SimpleType.get("QualifiedName")
    if QualifiedName:
        QualifiedName = QualifiedName.get('QualifiedName')
        SimpleNames = QualifiedName.get('QualifiedName')
        if type(SimpleNames).__name__ == "str":
            simple_name = simple_name + SimpleNames
        elif type(simple_name).__name__ == "list":
            for SimpleName in SimpleNames:
                simple_name = simple_name + SimpleName

        SimpleNames = QualifiedName.get('SimpleName')
        if type(SimpleNames).__name__ == "str":
            simple_name = simple_name + SimpleNames
        elif type(simple_name).__name__ == "list":
            for SimpleName in SimpleNames:
                simple_name = simple_name + SimpleName
    SimpleName = SimpleType.get('SimpleName')
    if SimpleName != None:
        simple_name = simple_name + SimpleName
    return simple_name


# 解析方法内的变量声明语句
def parse_VariableDeclarationStatement(VariableDeclarationStatement):
    """
    解析方法内的变量声明语句
    :param VariableDeclarationStatement:
    :return:
    """
    var_state = ''
    VariableDeclarationStatement_keys = list(VariableDeclarationStatement.keys())
    VariableDeclarationStatement_keys.remove('VariableDeclarationFragment')
    if VariableDeclarationStatement_keys[0] == 'SimpleType':
        # print(VariableDeclarationStatement.get('SimpleType'))
        var_state = var_state + parse_SimpleType(VariableDeclarationStatement.get('SimpleType'))
        # var_state = var_state + VariableDeclarationStatement.get('SimpleType').get(
        #     'SimpleName')
    else:
        var_state = var_state + VariableDeclarationStatement.get(VariableDeclarationStatement_keys[0])

    VariableDeclarationFragments = VariableDeclarationStatement.get('VariableDeclarationFragment')
    if type(VariableDeclarationFragments).__name__ == "str":
        var_state = var_state + VariableDeclarationFragments
    elif type(VariableDeclarationFragments).__name__ == "list":
        for VariableDeclarationFragment in VariableDeclarationFragments:
            var_state = var_state + VariableDeclarationFragment

    return var_state


# 解析类的方法
def parse_MethodDeclaration(MethodDeclaration):
    """
    解析类的方法
    :param MethodDeclaration:
    :return:
    """
    method_table = {'name': '', 'return_type': '', 'para': '', 'var_sate': '',
                    'express_state_num': 0,
                    'for_num': 0, 'switch_num': 0, 'if_num': 0, 'while_num': 0, 'do_while_num': 0, 'var_sate_num': 0}
    # 得到返回值类型

    MethodDeclaration_keys = list(MethodDeclaration.keys())
    # print(MethodDeclaration)
    # print(MethodDeclaration_keys)
    if MethodDeclaration_keys.__contains__('SingleVariableDeclaration'):
        MethodDeclaration_keys.remove('SingleVariableDeclaration')
    MethodDeclaration_keys.remove('SimpleName')
    if MethodDeclaration_keys.__contains__('Block'):
        MethodDeclaration_keys.remove('Block')
    # print(MethodDeclaration_keys)
    # 防止静态代码块
    if MethodDeclaration_keys.__len__() != 0:
        if MethodDeclaration_keys[0] == 'SimpleType':

            # 防止抛异常的情况SimpleType 会是列表
            # 防止
            SimpleTypes = MethodDeclaration.get('SimpleType')
            if type(SimpleTypes).__name__ == 'list':
                for SimpleType in SimpleTypes:
                    method_table['return_type'] = method_table['return_type'] + SimpleType.get('SimpleName')
            elif type(SimpleTypes).__name__ == 'dict':
                method_table['return_type'] = SimpleTypes.get('SimpleName')
        else:
            method_table['return_type'] = MethodDeclaration.get(MethodDeclaration_keys[0])
    # 得到方法的名字
    method_table['name'] = MethodDeclaration.get('SimpleName')
    # 得到方法的参数列表
    SingleVariableDeclarations = MethodDeclaration.get('SingleVariableDeclaration')
    if type(SingleVariableDeclarations).__name__ == 'list':
        for SingleVariableDeclaration in SingleVariableDeclarations:
            method_table['para'] = method_table['para'] + parse_SingleVariableDeclaration(SingleVariableDeclaration)

    elif type(SingleVariableDeclarations).__name__ == 'dict':
        method_table['para'] = method_table['para'] + parse_SingleVariableDeclaration(SingleVariableDeclarations)
    # 解析方法体内的数据
    # 'express_state_num': '',
    # 'for_num': 0, 'switch_num': 0, 'if_num': 0, 'while_num': 0, 'var_sate_num': 0
    Block = MethodDeclaration.get('Block')
    if type(Block).__name__ == 'dict':
        method_table['for_num'] = dict_get(Block, 'ForStatement', 0)
        method_table['express_state_num'] = dict_get(Block, 'ExpressionStatement', 0)
        method_table['switch_num'] = dict_get(Block, 'SwitchStatement', 0)
        method_table['while_num'] = dict_get(Block, 'WhileStatement', 0)
        method_table['do_while_num'] = dict_get(Block, 'DoStatement', 0)
        method_table['var_sate_num'] = dict_get(Block, 'VariableDeclarationStatement', 0)
        method_table['if_num'] = dict_get(Block, 'IfStatement', 0)
        VariableDeclarationStatements = Block.get('VariableDeclarationStatement')
        var_state = ''
        if type(VariableDeclarationStatements).__name__ == 'list':
            for VariableDeclarationStatement in VariableDeclarationStatements:
                var_state = var_state + parse_VariableDeclarationStatement(VariableDeclarationStatement)
        elif type(VariableDeclarationStatements).__name__ == 'dict':
            var_state = var_state + parse_VariableDeclarationStatement(VariableDeclarationStatements)
        method_table['var_sate'] = var_state
    return method_table


def parse_TypeDeclaration(TypeDeclaration):
    """
    解析一个java文件
    :param TypeDeclaration:
    :return:
    """
    file_class_table = {
        'attribute_num': 0,
        'method_num': 0,
        'for_num': 0,
        'switch_num': 0,
        'if_num': 0,
        'while_num': 0,
        'do_while_num': 0,
        'express_state_num': 0,
        'var_sate_num': 0,
        'class_table': {'name': ''},
        'tokens': ''
    }
    # 解析类的名字
    SimpleName = TypeDeclaration.get('SimpleName')
    file_class_table['class_table']['name'] = SimpleName
    file_class_table['tokens'] = SimpleName
    # 解析类的属性
    FieldDeclarations = TypeDeclaration.get('FieldDeclaration')
    if type(FieldDeclarations).__name__ == 'list':
        file_class_table['attribute_num'] = FieldDeclarations.__len__()
        i = 0
        for FieldDeclaration in FieldDeclarations:
            attribute_table_list = parse_FieldDeclaration(FieldDeclaration)
            for attribute_table in attribute_table_list:
                file_class_table['class_table'].__setitem__('attribute_table%d' % i, attribute_table)
                file_class_table['tokens'] = file_class_table['tokens'] + attribute_table['type'] + attribute_table[
                    'name'] + attribute_table['value']
                i = i + 1
        file_class_table['attribute_num'] = i
    elif type(FieldDeclarations).__name__ == 'dict':
        file_class_table['attribute_num'] = 1
        attribute_table_list = parse_FieldDeclaration(FieldDeclarations)
        j = 0
        for attribute_table in attribute_table_list:
            file_class_table['class_table'].__setitem__('attribute_table%d' % j, attribute_table)
            file_class_table['tokens'] = file_class_table['tokens'] + attribute_table['type'] + attribute_table[
                'name'] + \
                                         attribute_table['value']
            j = j + 1
        file_class_table['attribute_num'] = j

    # 解析类的方法
    MethodDeclarations = TypeDeclaration.get('MethodDeclaration')
    if type(MethodDeclarations).__name__ == 'list':
        file_class_table['method_num'] = MethodDeclarations.__len__()
        i = 0
        for MethodDeclaration in MethodDeclarations:
            method_table = parse_MethodDeclaration(MethodDeclaration)
            file_class_table['class_table'].__setitem__('method_table%d' % i, method_table)
            file_class_table['for_num'] = file_class_table['for_num'] + method_table['for_num']
            file_class_table['switch_num'] = file_class_table['switch_num'] + method_table['switch_num']
            file_class_table['if_num'] = file_class_table['if_num'] + method_table['if_num']
            file_class_table['while_num'] = file_class_table['while_num'] + method_table['while_num']
            file_class_table['do_while_num'] = file_class_table['do_while_num'] + method_table['do_while_num']
            file_class_table['express_state_num'] = file_class_table['express_state_num'] + method_table[
                'express_state_num']
            file_class_table['var_sate_num'] = file_class_table['var_sate_num'] + method_table['var_sate_num']
            # 如果返回值是因为注解造成的
            if type(method_table['return_type']).__name__ == 'dict':
                method_table['return_type'] = ''

            file_class_table['tokens'] = file_class_table['tokens'] + method_table['return_type'] + method_table[
                'para'] + method_table['name'] + method_table['var_sate']

            i = i + 1
    elif type(MethodDeclarations).__name__ == 'dict':
        file_class_table['method_num'] = 1
        method_table = parse_MethodDeclaration(MethodDeclarations)
        file_class_table['class_table'].__setitem__('method_table', method_table)
        file_class_table['for_num'] = method_table['for_num']
        file_class_table['switch_num'] = method_table['switch_num']
        file_class_table['if_num'] = method_table['if_num']
        file_class_table['while_num'] = method_table['while_num']
        file_class_table['do_while_num'] = method_table['do_while_num']
        file_class_table['express_state_num'] = method_table['express_state_num']
        file_class_table['var_sate_num'] = method_table['var_sate_num']
        # print("method_table['name']:" + type(method_table['name']).__name__)
        # print("method_table['var_sate']:" + type(method_table['var_sate']).__name__)
        # print("method_table['return_type']:" + method_table['return_type'].__str__())
        # print("method_table['para']:" + type(method_table['para']).__name__)
        # print("file_class_table['tokens']:" + type(file_class_table['tokens']).__name__)
        file_class_table['tokens'] = file_class_table['tokens'] + method_table['return_type'] + method_table['para'] + \
                                     method_table['name'] + method_table['var_sate']

    return file_class_table


def dict_get(dict, objkey, count):
    """
    统计嵌套字典对象中某个key的个数
    :param dict: 待统计的字典
    :param objkey: 目标key
    :param count:
    :return:
    """
    tmp = dict
    if tmp.keys().__contains__(objkey):
        count = count + 1
    for v in list(tmp.values()):
        if type(v).__name__ == 'list':
            for item in v:
                if type(item).__name__ == 'dict':
                    count = dict_get(item, objkey, count)
        elif type(v).__name__ == 'dict':
            count = dict_get(v, objkey, count)
    return count


def parse_jsonStr_to_dict(json_data):
    """
    将一个json字符串转化为dict对象
    :param json_data:
    :return:
    """
    jsonObject = {}
    try:
        jsonObject = json.loads(json_data)
    except Exception as e:
        print(json_data)
    return dict(jsonObject)


def parse_ast_to_classIfo(json_data):
    """
    解析ast，遍历出ast中类的结构与属性信息
    :param json_data:
    :return:
    """
    jsonDict = parse_jsonStr_to_dict(json_data)
    ast = jsonDict.get("ast")
    ast_xml = jsonDict.get("xml")
    astDict = parse_jsonStr_to_dict(ast)

    CompilationUnit = astDict.get('CompilationUnit')
    result_table = {
        "class_num": 0,
        "file_encoding": jsonDict.get("encoding"),
        "ast_xml": ast_xml,
        'attribute_num': 0,
        'method_num': 0,
        'for_num': 0,
        'switch_num': 0,
        'if_num': 0,
        'while_num': 0,
        'do_while_num': 0,
        'express_state_num': 0,
        'var_sate_num': 0,
        'tokens': ''
    }
    # 解析出来的文件信息为NULL
    if type(CompilationUnit).__name__ == 'str':
        print("语法树为空")
        return None
        # print("CompilationUnit: %s " % CompilationUnit)
        # print(ast)
        # exit(1)
    if CompilationUnit:
        TypeDeclarations = CompilationUnit.get('TypeDeclaration')

        if TypeDeclarations:
            if type(TypeDeclarations).__name__ == 'list':
                i = 0
                for TypeDeclaration in TypeDeclarations:
                    #
                    file_class_table = parse_TypeDeclaration(TypeDeclaration)
                    result_table.__setitem__('file_class_table%d' % i, file_class_table)
                    result_table['class_num'] = result_table['class_num'] + 1
                    result_table['attribute_num'] = result_table['attribute_num'] + file_class_table['attribute_num']
                    result_table['method_num'] = result_table['method_num'] + file_class_table['method_num']
                    result_table['for_num'] = result_table['for_num'] + file_class_table['for_num']
                    result_table['switch_num'] = result_table['switch_num'] + file_class_table['switch_num']
                    result_table['if_num'] = result_table['if_num'] + file_class_table['if_num']
                    result_table['while_num'] = result_table['while_num'] + file_class_table['while_num']
                    result_table['do_while_num'] = result_table['do_while_num'] + file_class_table['do_while_num']
                    result_table['express_state_num'] = result_table['express_state_num'] + file_class_table[
                        'express_state_num']
                    result_table['var_sate_num'] = result_table['var_sate_num'] + file_class_table['var_sate_num']
                    result_table['tokens'] = result_table['tokens'] + file_class_table['tokens']
                    i = i + 1
            elif type(TypeDeclarations).__name__ == 'dict':
                FieldDeclarations = TypeDeclarations.get('FieldDeclaration')
                file_class_table = parse_TypeDeclaration(TypeDeclarations)
                result_table.__setitem__('file_class_table', file_class_table)
                result_table['class_num'] = 1
                result_table['attribute_num'] = file_class_table['attribute_num']
                result_table['method_num'] = file_class_table['method_num']
                result_table['for_num'] = file_class_table['for_num']
                result_table['switch_num'] = file_class_table['switch_num']
                result_table['if_num'] = file_class_table['if_num']
                result_table['while_num'] = file_class_table['while_num']
                result_table['do_while_num'] = file_class_table['do_while_num']
                result_table['express_state_num'] = file_class_table['express_state_num']
                result_table['var_sate_num'] = file_class_table['var_sate_num']
                result_table['tokens'] = file_class_table['tokens']
    return result_table


def compute_javafile_similarity(file_path1, file_path2):
    """
    计算两个java文件的相似度
    :param file_path1:
    :param file_path2:
    :return:
    """
    # lock.acquire()
    ast1 = parse_javafile_to_ast(file_path1, "JSON")
    ast2 = parse_javafile_to_ast(file_path2, "JSON")
    # lock.release()
    # fp = open(r"G:\python-study\older\ASTExtractor-master\result.json", "r", encoding="utf-8")
    # ast = fp.read()
    result_table1 = parse_ast_to_classIfo(ast1)
    result_table2 = parse_ast_to_classIfo(ast2)
    # 属性相似度
    similarity1 = compute_attribute_similarity(result_table1, result_table2)
    print("similarity1:" + str(similarity1))
    # 文本相似度
    similarity2 = compute_text_similarity(result_table1, result_table2)
    print("similarity2:" + str(similarity2))
    print("result_table1:" + str(result_table1))
    print("result_table2:" + str(result_table2))
    sum_col = ((result_table1['method_num'] + result_table2['method_num']) * 4 + (
            result_table1['attribute_num'] + result_table2['attribute_num']) * 3 + (
                       result_table1['class_num'] + result_table2['class_num']) * 1 + 9 * 2)
    # print(sum_col)
    # print(((9 * 2) / sum_col))
    # print(similarity1)
    # print(similarity2)
    similarity = similarity1 * ((9 * 2) / sum_col) + similarity2 * (1 - ((9 * 2) / sum_col))
    return similarity


def walkFile(file):
    """
    遍历文件夹，得到文件夹内全部的java文件
    :param file: 待遍历的文件夹
    :return:
    """
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


def thread_task(javafile):
    """
    线程任务：将源文件解析成语法树，并从语法树中遍历出程序属性信息放入result_table
    :param javafile:
    :return:
    """
    # lock.acquire()
    ast = parse_javafile_to_ast(javafile, "JSON")
    # lock.release()
    result_table = parse_ast_to_classIfo(ast)

    if result_table == None:
        return {"java_file": javafile, "result_table": result_table, "error_file": javafile}
    else:
        return {"java_file": javafile, "result_table": result_table}


from concurrent.futures import ThreadPoolExecutor


def get_javafile_to_result_table(folder):
    """
    将一个文件夹中所有的java文件解析成语法树并遍历其中的信息
    :param folder:
    :return:
    """
    result_table_list = []
    javafile_list = walkFile(folder)

    with ThreadPoolExecutor(max_workers=8) as pool:
        # print(id(pool))
        # 使用线程执行map计算
        # 后面元组有3个元素，因此程序启动3条线程来执行action函数
        results = pool.map(thread_task, javafile_list)

        for r in results:
            r.__setitem__("owner_folder", folder)
            result_table_list.append(r)

    # for javafile in javafile_list:
    #     pool.submit(thread_task,javafile)

    # ast = parse_javafile_to_ast(javafile, "JSON")
    # result_table = parse_ast_to_classIfo(ast)

    return result_table_list


def compute_java_folder_similarity(folder):
    """
    计算一个文件夹内所有java文件的文件相似度,该方法速度过慢，后面有用多线程改良版
    :param folder:
    :return:
    """
    javafile_list = walkFile(folder)
    # print('javafile_list:', javafile_list)
    for i in range(javafile_list.__len__() - 1):
        ast1 = parse_javafile_to_ast(javafile_list.__getitem__(i), "JSON")
        # print("java_file:"+javafile_list.__getitem__(i))
        result_table1 = parse_ast_to_classIfo(ast1)
        if result_table1 is None:
            print("问题文件：" + javafile_list.__getitem__(i))
            # global null_javaFile_list
            # null_javaFile_list.append(javafile_list.__getitem__(i))
            continue
        for j in range(i + 1, javafile_list.__len__()):
            # print("java_file:"+javafile_list.__getitem__(j))
            ast2 = parse_javafile_to_ast(javafile_list.__getitem__(j), "JSON")
            result_table2 = parse_ast_to_classIfo(ast2)
            if result_table2 is None:
                print("问题文件：" + javafile_list.__getitem__(j))
                # global null_javaFile_list
                # null_javaFile_list.append(javafile_list.__getitem__(j))
                continue
            # 属性相似度
            similarity1 = compute_attribute_similarity(result_table1, result_table2)
            # 文本相似度
            similarity2 = compute_text_similarity(result_table1, result_table2)

            sum_col = ((result_table1['method_num'] + result_table2['method_num']) * 4 + (
                    result_table1['attribute_num'] + result_table2['attribute_num']) * 3 + (
                               result_table1['class_num'] + result_table2['class_num']) * 1 + 9 * 2)
            # print(sum_col)
            # print(((9 * 2) / sum_col))
            # print(similarity1)
            # print(similarity2)

            similarity = similarity1 * ((9 * 2) / sum_col) + similarity2 * (1 - ((9 * 2) / sum_col))
            print(
                "%s consists for %f of %s " % (javafile_list.__getitem__(i), similarity, javafile_list.__getitem__(j)))


# def thread_task2(result_table1, result_table2):
#     similarity1 = compute_struct_similarity(result_table1.get("result_table"), result_table2.get("result_table"))
#     # 文本相似度
#     similarity2 = compute_text_similarity(result_table1.get("result_table"), result_table2.get("result_table"))
#
#     sum_col = ((result_table1['result_table']['method_num'] + result_table2['result_table']['method_num']) * 4 + (
#             result_table1['result_table']['attribute_num'] + result_table2['result_table']['attribute_num']) * 3 + (
#                        result_table1['result_table']['class_num'] + result_table2['result_table'][
#                    'class_num']) * 1 + 9 * 2)
#
#     similarity = similarity1 * ((9 * 2) / sum_col) + similarity2 * (1 - ((9 * 2) / sum_col))
#     return "%s consists for %f of %s " % (result_table1['java_file'], similarity, result_table2['java_file'])
# 将result_table_list按照二级文件夹进行分离
def group_result_table_list(folder):
    """
    将文件夹中所有源文件解析成语法树，并对解析出来的语法树进行遍历，最后将遍历出的结果集按照源文件夹内的二级文件夹进行分组
    :param folder:
    :return:
    """
    result_table_list = []
    dirs = [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]

    for dir in dirs:
        group_name = folder + os.path.sep + dir
        # second_fold_list.append({'group_name': group_name, 'result_table_list': get_javafile_to_result_table(group_name)})
        for result_table in get_javafile_to_result_table(group_name):
            result_table_list.append(result_table)

    return result_table_list


def thread_task3(result_table_entry):
    """
    子线程任务，对java文件对进行求各种相似度。
    :param result_table_entry:
    :return:
    """
    result_table1 = result_table_entry['result_table1']
    result_table2 = result_table_entry['result_table2']
    # print("result_table1:", result_table1['java_file'])
    # print("result_table2:", result_table2['java_file'])
    # 属性结构相似度
    similarity1 = compute_attribute_similarity(result_table1.get("result_table"),
                                               result_table2.get("result_table"))
    # ast结构相似度
    # lock.acquire()
    similarity_result = compute_struct_similarity(result_table1,
                                                  result_table2)
    # lock.release()
    similarity3 = similarity_result.get("score")
    # distance = similarity_result.get("distance")

    # 文本相似度
    similarity2 = compute_text_similarity(result_table1.get("result_table"), result_table2.get("result_table"))

    # sum_col = ((result_table1['result_table']['method_num'] + result_table2['result_table'][
    #     'method_num']) * 4 + (
    #                    result_table1['result_table']['attribute_num'] + result_table2['result_table'][
    #                'attribute_num']) * 3 + (
    #                    result_table1['result_table']['class_num'] + result_table2['result_table'][
    #                'class_num']) * 1 + 9 * 2)

    # similarity = similarity1 * ((9 * 2) / sum_col) + similarity2 * (1 - ((9 * 2) / sum_col))
    similarity = (1 / 5) * similarity1 + (2 / 5) * similarity2 + (2 / 5) * similarity3

    return {
        "similarity": similarity,
        "java_file1": result_table1['java_file'], "java_file2": result_table2['java_file'],
        "struct_similarity": similarity3,
        "text_similarity": similarity2, "attribute_similarity": similarity1
    }


def compute_java_project_folder_similarity_thread(folder):
    """
    多线程版 计算每一个学生的java工程文件与其他学生的所有java工程文件的文件相似度
    :param folder:
    :return:
    """
    similarity_list = []
    # result_table_list = get_javafile_to_result_table(folder)
    # 将result_table_list按照二级文件夹进行分离
    result_table_list = group_result_table_list(folder)
    normal_file_list = []
    error_file_list = []
    result_table_entry_list = []
    for result_table in result_table_list:
        if result_table.get("error_file") is None:
            normal_file_list.append(result_table["java_file"])
        else:
            error_file_list.append(result_table["error_file"])

    for i in range(result_table_list.__len__() - 1):
        result_table1 = result_table_list.__getitem__(i)
        if result_table1.get("error_file") is not None:
            print("问题文件：" + result_table1.get("error_file"))
            continue
        for j in range(i + 1, result_table_list.__len__()):
            result_table2 = result_table_list.__getitem__(j)
            if result_table1['owner_folder'] == result_table2['owner_folder']:
                continue
            if result_table2.get("error_file") is not None:
                print("问题文件：" + result_table2.get("error_file"))
                continue
            result_table_entry_list.append({"result_table1": result_table1, "result_table2": result_table2})
            # result_table_list2.append([result_table1 , result_table2])

            # # 属性相似度
            # similarity1 = compute_attribute_similarity(result_table1.get("result_table"),
            #                                            result_table2.get("result_table"))
            # # ast结构相似度
            # similarity_result = compute_struct_similarity(result_table1,
            #                                               result_table2)
            # similarity3 = similarity_result.get("score")
            #
            #
            # # 抽样文本相似度
            # similarity2 = compute_text_similarity(result_table1.get("result_table"), result_table2.get("result_table"))
            #
            # # similarity = similarity1 * ((9 * 2) / sum_col) + similarity2 * (1 - ((9 * 2) / sum_col))
            # similarity = (1 / 5) * similarity1 + (2 / 5) * similarity2 + (2 / 5) * similarity3
            #
            #
            #
            # similarity_list.append({"similarity": similarity,
            #                         "java_file1": result_table1['java_file'], "java_file2": result_table2['java_file'],
            #                         "struct_similarity": similarity3,
            #                         "text_similarity": similarity2, "attribute_similarity": similarity1})
    print("多线程求相似度开始……", result_table_entry_list.__len__())

    with ThreadPoolExecutor(max_workers=3) as pool:
        # print(id(pool))
        # 使用线程执行map计算
        # 后面元组有3个元素，因此程序启动3条线程来执行action函数
        result = pool.map(thread_task3, result_table_entry_list)
        similarity_list = list(result)
    print("多线程求相似度结束……")
    # 每一个java文件与其他java文件最大的相似度匹配对
    max_similarity_file_list = {}
    # 找到每一个文件最大相似度匹配对
    for similarity_info in similarity_list:

        for normal_file in normal_file_list:
            if similarity_info['java_file1'] == normal_file or similarity_info['java_file2'] == normal_file:
                max_similarity_file = max_similarity_file_list.get(normal_file)
                if (max_similarity_file is None) or (
                        max_similarity_file is not None and max_similarity_file["similarity"] < similarity_info[
                    'similarity']):
                    # #去重操作
                    # if not list(max_similarity_file_list.values()).__contains__({"filepath1": similarity_info['java_file1'],
                    #                                                    "filepath2": similarity_info['java_file2'],
                    #                                                    "similarity": similarity_info['similarity']}):

                    max_similarity_file_list.__setitem__(normal_file, {"filepath1": similarity_info['java_file1'],
                                                                       "filepath2": similarity_info['java_file2'],
                                                                       "attribute_similarity": similarity_info[
                                                                           'attribute_similarity'],
                                                                       "struct_similarity": similarity_info[
                                                                           'struct_similarity'],
                                                                       "similarity": similarity_info['similarity']})

    return {
        "result_table_list": result_table_list,
        "similarity_list": similarity_list,
        "normal_file_list": normal_file_list,
        "error_file_list": error_file_list,
        "max_similarity_file_list": max_similarity_file_list
    }

    # lock.acquire()


def compute_java_folder_similarity_thread(folder):
    """
    多线程版 计算一个文件夹内所有java文件的文件相似度
    :param folder:
    :return:
    """
    # starttime = datetime.datetime.now()
    similarity_list = []
    result_table_list = get_javafile_to_result_table(folder)
    normal_file_list = []
    error_file_list = []
    result_table_entry_list = []
    for result_table in result_table_list:
        if result_table.get("error_file") is None:
            normal_file_list.append(result_table["java_file"])
        else:
            error_file_list.append(result_table["error_file"])

    for i in range(result_table_list.__len__() - 1):
        result_table1 = result_table_list.__getitem__(i)
        if result_table1.get("error_file") is not None:
            print("问题文件：" + result_table1.get("error_file"))
            continue
        for j in range(i + 1, result_table_list.__len__()):
            result_table2 = result_table_list.__getitem__(j)
            if result_table2.get("error_file") is not None:
                print("问题文件：" + result_table2.get("error_file"))
                continue
            # result_table_list2.append([result_table1 , result_table2])
            result_table_entry_list.append({"result_table1": result_table1, "result_table2": result_table2})
            # # 属性结构相似度
            # similarity1 = compute_attribute_similarity(result_table1.get("result_table"),
            #                                            result_table2.get("result_table"))
            # # ast结构相似度
            # similarity_result = compute_struct_similarity(result_table1,
            #                                               result_table2)
            # similarity3 = similarity_result.get("score")
            # distance = similarity_result.get("distance")
            #
            # # 文本相似度
            # similarity2 = compute_text_similarity(result_table1.get("result_table"), result_table2.get("result_table"))
            #
            # # sum_col = ((result_table1['result_table']['method_num'] + result_table2['result_table'][
            # #     'method_num']) * 4 + (
            # #                    result_table1['result_table']['attribute_num'] + result_table2['result_table'][
            # #                'attribute_num']) * 3 + (
            # #                    result_table1['result_table']['class_num'] + result_table2['result_table'][
            # #                'class_num']) * 1 + 9 * 2)
            #
            # # similarity = similarity1 * ((9 * 2) / sum_col) + similarity2 * (1 - ((9 * 2) / sum_col))
            # similarity = (1 / 5) * similarity1 + (2 / 5) * similarity2 + (2 / 5) * similarity3
            # info = "%s consists for %f of %s " % (result_table1['java_file'], similarity, result_table2['java_file'])
            #
            # similarity_list.append({"similarity": similarity, "info": info,
            #                         "java_file1": result_table1['java_file'], "java_file2": result_table2['java_file'],
            #                         "struct_similarity": similarity3, "ast_distance": distance,
            #                         "text_similarity": similarity2, "attribute_similarity": similarity1})

    print("多线程求相似度开始……", result_table_entry_list.__len__())

    with ThreadPoolExecutor(max_workers=3) as pool:
        # print(id(pool))
        # 使用线程执行map计算
        # 后面元组有3个元素，因此程序启动3条线程来执行action函数
        result = pool.map(thread_task3, result_table_entry_list)
        similarity_list = list(result)
        # for item in result:
        #     similarity_list.append(item)
        # print("内层循环的similarity_list",list(similarity_list))

    # 每一个java文件与其他java文件最大的相似度匹配对
    # endtime = datetime.datetime.now()
    print("多线程求相似度结束……")
    # print(similarity_list.__len__())
    # print("共花费：", (endtime - starttime).seconds, "秒")
    max_similarity_file_list = {}
    # 找到每一个文件最大相似度匹配对
    for similarity_info in similarity_list:

        for normal_file in normal_file_list:
            if similarity_info['java_file1'] == normal_file or similarity_info['java_file2'] == normal_file:
                max_similarity_file = max_similarity_file_list.get(normal_file)
                if (max_similarity_file is None) or (
                        max_similarity_file is not None and max_similarity_file["similarity"] < similarity_info[
                    'similarity']):
                    max_similarity_file_list.__setitem__(normal_file, {"filepath1": similarity_info['java_file1'],
                                                                       "filepath2": similarity_info['java_file2'],
                                                                       "attribute_similarity": similarity_info[
                                                                           'attribute_similarity'],
                                                                       "struct_similarity": similarity_info[
                                                                           'struct_similarity'],
                                                                       "similarity": similarity_info['similarity']})

    return {
        "result_table_list": result_table_list,
        "similarity_list": similarity_list,
        "normal_file_list": normal_file_list,
        "error_file_list": error_file_list,
        "max_similarity_file_list": max_similarity_file_list

    }

    # if similarity_info['similarity'] > sim:
    #     print(similarity_info['info'])

    # pool = ThreadPoolExecutor(max_workers=100)
    # with ThreadPoolExecutor(max_workers=100) as pool:
    #     print(id(pool))
    #     print(result_table_list2)
    #     # 使用线程执行map计算
    #     # 后面元组有3个元素，因此程序启动3条线程来执行action函数
    #     results = pool.map(thread_task2, result_table_list2)
    #     print("hhhhhhhhhhhhhhhhhhh")
    #     for r in results:
    #         print(r)


def compute_javaFileContent_similarity(jsonStr):
    """
    计算JSON数据集中，所有java文件对的相似度
    :param jsonStr:
    :return:
    """
    JPackage = jpype.JPackage('helpers')
    result_json = JPackage.SimilarityCalHelpers.compute_files_entry_set_similarity(jsonStr)
    # return result
    jsonObject = {}
    try:
        jsonObject = json.loads(result_json)
    except Exception as e:
        print(result_json)

    jsonDict = dict(jsonObject)

    return jsonDict


def remove_duplicate(dict_list):
    """
    删除列表中重复的字典对象
    :param dict_list:
    :return:
    """
    seen = set()
    new_dict_list = []
    for dict_item in dict_list:
        t_dict = {"filepath1": dict_item['filepath1'], "filepath2": dict_item['filepath2'],
                  "similarity": dict_item['similarity']}
        t_tup = tuple(t_dict.items())
        if t_tup not in seen:
            seen.add(t_tup)
            new_dict_list.append(dict_item)
    return new_dict_list


def chengeChar(path):
    """
    修复解压出来的文件乱码的问题
    :param path:
    :return:
    """
    path = path.rstrip('/').rstrip('\\')  # 去除路径最右边的/
    file_name = os.path.split(path)[-1]  # 获取最后一段字符，准备转换
    file_path = os.path.split(path)[0]  # 获取前面的路径，为rename做准备
    try:  # 将最后一段有乱码的字符串转换，尝试过整个路径转换，不生效，估计是无法获取整个路径的编码格式吧。
        new_name = file_name.encode('cp437').decode('gbk')
    except UnicodeEncodeError as e:  # 先转换成Unicode再转换回gbk或utf-8
        new_name = file_name.encode('utf-8').decode('utf-8')
    except UnicodeDecodeError as e:
        new_name = file_name.encode('cp437').decode('utf-8')
    path2 = os.path.join(file_path, new_name)  # 将转换完成的字符串组合成新的路径
    if not os.path.exists(path):
        return path2
    try:
        os.renames(path, path2)  # 重命名文件
    except:
        print('renames error！！')
    return path2


def del_zip(path):
    """
    删除解压出来的zip包
    :param path:
    :return:
    """
    path = chengeChar(path)
    if path.endswith('.zip') or path.endswith('.rar'):
        os.remove(path)
    elif os.path.isdir(path):
        for i in os.listdir(path):
            file_path = os.path.join(path, i)
            del_zip(file_path)  # 递归调用，先把所有的文件删除


def unzip_file(z, unzip_path, _path):
    """
    对文件进行解压
    :param z:
    :param unzip_path:
    :param _path:
    :return:
    """
    new_dir = chengeChar(_path.split('.')[0].split('\\')[-1])
    if not os._exists(os.path.join(unzip_path, new_dir)):
        os.mkdir(os.path.join(unzip_path, new_dir))
    unzip_path = os.path.join(unzip_path, new_dir)
    '''解压zip包'''
    z.extractall(path=unzip_path)
    zip_list = z.namelist()  # 返回解压后的所有文件夹和文件list
    z.close()
    for zip_file in zip_list:
        path = os.path.join(unzip_path, zip_file)
        if os.path.exists(path):
            unzip_file_main(path, os.path.split(path)[0])


def unzip_file_main(path, unzip_path):
    """
    解压程序的入口函数
    :param path:
    :param unzip_path:
    :return:
    """
    path = chengeChar(path)
    if os.path.exists(path):
        # unzip_path = os.path.split(path)[0]  # 解压至当前目录
        if path.endswith('.zip'):
            z = zipfile.ZipFile(path, 'r')
            unzip_file(z, unzip_path, path)
            os.remove(path)

        elif path.endswith('.rar'):
            r = rarfile.RarFile(path)
            unzip_file(r, unzip_path, path)
            os.remove(path)

        elif os.path.isdir(path):
            for file_name in os.listdir(path):
                path2 = os.path.join(path, file_name)
                if os.path.exists(path2):
                    unzip_file_main(path2, os.path.split(path2)[0])

    else:
        print('the path is not exist!!!')


def get_item_list_from_dict(dict_obj, key):
    """
    key关键字模糊查询一个字典
    :param dict_obj:
    :param key: 查询的关键词
    :return: 字典中所有键以key开头的值的列表
    """
    key_list = []
    result_list = []
    for k in dict_obj.keys():
        if k.startswith(key):
            key_list.append(k)
    for kk in key_list:
        result_list.append(dict_obj.get(kk))
    return result_list


def write_result_table_to_database(result_table_list, detect_recordObj, forder):
    """
    将result_table写入数据库
    :param result_table_list:
    :param detect_recordObj:
    :param forder:
    :return:
    """
    # 检测记录-文件组表
    file_group_set = set()
    file_groupObj_list = {}
    fileObj_list = {}
    error_file_num = 0
    for result_table in result_table_list:
        result_table_item = result_table['result_table']
        # 写入文件信息
        is_normal = True
        # owner_folder
        if result_table.get("error_file") is not None:
            error_file_num = error_file_num + 1
            is_normal = False
        path = result_table["java_file"]
        name = os.path.basename(path).split(".")[0]
        type = os.path.basename(path).split(".")[1]
        fileobj = file.createfile(name=name, path=path[forder.__len__() + 1:], content=None, type=type,
                                  encoding=result_table_item['file_encoding'],
                                  copy_rank=0,
                                  is_normal=is_normal, enabled=True)
        fileobj.save()
        fileObj_list.__setitem__(path, fileobj.id)
        # 写入文件组信息
        if not file_group_set.__contains__(result_table['owner_folder']):

            file_group_set.add(result_table['owner_folder'])

            file_groupObj = file_group.createfile_group(name=result_table['owner_folder'].split(os.path.sep)[-1],
                                                        file_num=1, exception_file_num=0 if is_normal else 1,
                                                        normal_file_num=1 if is_normal else 0,
                                                        enabled=True)
            file_groupObj.save()
            file_groupObj_list.__setitem__(result_table['owner_folder'], file_groupObj.id)
            # 写入文件组-文件信息

            file_group_fileObj = file_group_file.createfile_group_file(group_id=file_groupObj, file_id=fileobj,
                                                                       enabled=True)
            file_group_fileObj.save()
            # 检测记录-文件组信息
            record_groupObj = record_group.createrecord_group(record_id=detect_recordObj, group_id=file_groupObj,
                                                              enabled=True)
            record_groupObj.save()
        else:
            file_group_id = file_groupObj_list.get(result_table['owner_folder'])
            file_groupObj = file_group.objects.filter(id=file_group_id).first()
            file_groupObj.file_num = file_groupObj.file_num + 1
            if is_normal:
                file_groupObj.normal_file_num = file_groupObj.normal_file_num + 1
            else:
                file_groupObj.exception_file_num = file_groupObj.exception_file_num + 1
            file_groupObj.save()
            # 写入文件组-文件信息
            file_group_fileObj = file_group_file.createfile_group_file(group_id=file_groupObj, file_id=fileobj,
                                                                       enabled=True)
            file_group_fileObj.save()

        # 写入类信息
        # for class_item in get_item_list_from_dict(result_table, "file_class_table"):
        #
        #     class_tableObj = class_table.createclass(name=class_item['class_table']['name'],
        #                                              attribute_num=class_item['attribute_num'],
        #                                              method_num=class_item['method_num'], for_num=class_item['for_num'],
        #                                              switch_num=class_item['switch_num'], if_num=class_item['if_num'],
        #                                              while_num=class_item['while_num'],
        #                                              do_while_num=class_item['do_while_num'],
        #                                              var_sate_num=class_item['var_sate_num'], enabled=True)
        #     class_tableObj.save()
        #     # 写入文件-类关联
        #     file_classObj = file_class.createfile_class(file_id=fileobj, class_id=class_tableObj, enabled=True)
        #     file_classObj.save()
        #     # 写入属性信息
        #     for attribute_item in get_item_list_from_dict(class_item['class_table'], "attribute_table"):
        #         attributeObj = attribute.createattribute(type=attribute_item['type'], name=attribute_item['name'],
        #                                                  value=attribute_item['value'], enabled=True)
        #         attributeObj.save()
        #         # 写入类-属性关联
        #         class_attributeObj = class_attribute.createclass_attribute(class_id=class_tableObj,
        #                                                                    attribute_id=attributeObj, enabled=True)
        #         class_attributeObj.save()
        #     # 写入方法信息
        #     for method_item in get_item_list_from_dict(class_item['class_table'], "method_table"):
        #         methodObj = method.createmethod(name=method_item['name'], return_type=method_item['return_type'],
        #                                         param_list=method_item['para'], var_sate=method_item['var_sate'],
        #                                         for_num=method_item['for_num'],
        #                                         switch_num=method_item['switch_num'], if_num=method_item['if_num'],
        #                                         while_num=method_item['while_num'],
        #                                         do_while_num=method_item['do_while_num'],
        #                                         var_sate_num=method_item['var_sate_num'], enabled=True)
        #         methodObj.save()
        #         # 写入类-方法关联
        #         class_methodObj = class_method.createclass_method(class_id=class_tableObj, method_id=methodObj,
        #                                                           enabled=True)
        #         class_methodObj.save()
    # 写入文件组信息

    # 保存检测记录，正 异常文件
    detect_recordObj.file_num = result_table_list.__len__()
    detect_recordObj.exception_file_num = error_file_num
    detect_recordObj.normal_file_num = result_table_list.__len__() - error_file_num
    detect_recordObj.save()
    return fileObj_list


def write_similarity_list_to_database(similarity_list, fileObj_list):
    """
    similarity_list写入数据库
    :param similarity_list:
    :param fileObj_list:
    :return:
    """
    # {"similarity": similarity, "info": info,
    #                         "java_file1": result_table1['java_file'], "java_file2": result_table2['java_file'],
    #                         "struct_similarity": similarity3, "ast_distance": distance,
    #                         "text_similarity": similarity2, "attribute_similarity": similarity1}
    similarityObj_list = {}
    for similarity_item in similarity_list:
        file1 = file.objects.filter(id=fileObj_list.get(similarity_item['java_file1'])).first()
        file2 = file.objects.filter(id=fileObj_list.get(similarity_item['java_file2'])).first()
        # 设置抄袭等级
        copy_rank = 0
        if similarity_item['similarity'] > 0.8:
            copy_rank = 3

        elif similarity_item['similarity'] > 0.6:
            copy_rank = 2

        elif similarity_item['similarity'] > 0.4:
            copy_rank = 1

        file1.copy_rank = copy_rank if file1.copy_rank is None or (file1.copy_rank < copy_rank) else file1.copy_rank
        file2.copy_rank = copy_rank if file2.copy_rank is None or (file2.copy_rank < copy_rank) else file2.copy_rank
        file1.save()
        file2.save()
        similarityObj = similarity.createsimilarity(file1_id=file1, file2_id=file2,
                                                    attribute_similarity=similarity_item['attribute_similarity'],
                                                    struct_similarity=similarity_item['struct_similarity'],
                                                    sample_text_similarity=similarity_item['text_similarity'],
                                                    text_similarity=None,
                                                    similarity=similarity_item['similarity'],
                                                    is_max_similarity=False, enabled=True)
        similarityObj.save()
        similarityObj_list.__setitem__(str(similarityObj.file1_id.id) + str(similarityObj.file2_id.id),
                                       similarityObj.id)

    return similarityObj_list


def write_max_similarity_file_list_to_database(max_similarity_file_list, similarityObj_list, fileObj_list):
    """
    max_similarity_file_list写入数据库
    :param max_similarity_file_list:
    :param similarityObj_list:
    :param fileObj_list:
    :return:
    """
    # {"filepath1": similarity_info['java_file1'],
    #  "filepath2": similarity_info['java_file2'],
    #  "similarity": similarity_info['similarity']}
    for max_similarity_file_item in max_similarity_file_list.values():
        file1_id = fileObj_list.get(max_similarity_file_item['filepath1'])
        file2_id = fileObj_list.get(max_similarity_file_item['filepath2'])
        similarity_id = 0
        try:
            similarity_id = similarityObj_list.get(str(file1_id) + str(file2_id))
            similarityObj = similarity.objects.filter(id=similarity_id).first()
            similarityObj.is_max_similarity = True
            similarityObj.save()
        except Exception as e:
            print("file1_id:", file1_id)
            print("file2_id:", file2_id)
            print("similarity_id:", similarity_id)


def write_similarity_result_list_to_database(similarity_result_list, fileObj_list):
    """
    similarity_result_list写入数据库
    :param similarity_result_list:
    :param fileObj_list:
    :return:
    """
    # 中度抄袭文件path
    mid_copy_file_list = []
    # similarity_sum = 0
    # 求相似度总和
    # for similarity_result in similarity_result_list:
    #     item = similarity_result.get("similarity_files_entry_set")[0]
    #     similarity_sum = similarity_sum + item['similarity']
    #
    # sim = similarity_sum / similarity_result_list.__len__()

    for similarity_result in similarity_result_list:

        item = similarity_result.get("similarity_files_entry_set")[0]
        # file1 = file.objects.filter(id=fileObj_list.get(item['filepath1'])).first()
        # file2 = file.objects.filter(id=fileObj_list.get(item['filepath2'])).first()
        similarityObj = similarity.objects.filter(file1_id__id=fileObj_list.get(item['filepath1'])).filter(
            file2_id=fileObj_list.get(item['filepath2'])).first()
        # similarityObj = similarity.createsimilarity(file1_id=file1,
        #                                             file2_id=file2,
        #                                             attribute_similarity=None,
        #                                             struct_similarity=None,
        #                                             sample_text_similarity=None,
        #                                             text_similarity=item['similarity'],
        #                                             similarity=item['similarity'],
        #                                             is_max_similarity=False, enabled=True)
        similarityObj.text_similarity = item['similarity']
        similarityObj.save()
        # 写入文件的内容、抄袭的等级
        fileObj1 = file.objects.filter(id=similarityObj.file1_id.id).first()
        fileObj2 = file.objects.filter(id=similarityObj.file2_id.id).first()
        fileObj1.content = item['file_content1']
        fileObj2.content = item['file_content2']
        # 模型预测

        a = np.array([item['attribute_similarity'], item['struct_similarity'], item['similarity']]).reshape(-1, 3).astype(np.float64)


        copy_rank = clf.predict(a).__getitem__(0)

        # A文本与B文本存在很长的一段相同代码块。
        if item['has_longer_match'] is True:
            copy_rank = 1 if copy_rank == 0 else copy_rank

        # A文件与B文件相似度抄袭判定为1，A文件与C文件相似度抄袭判定为2，那么A文件的抄袭判定应为2
        fileObj1.copy_rank = copy_rank if fileObj1.copy_rank is None or (
                fileObj1.copy_rank < copy_rank) else fileObj1.copy_rank
        fileObj2.copy_rank = copy_rank if fileObj2.copy_rank is None or (
                fileObj2.copy_rank < copy_rank) else fileObj2.copy_rank
        fileObj1.save()
        fileObj2.save()

        # 写匹配表
        for match in item['matches']:
            start_pos = match['start_pos']
            end_pos = match['end_pos']
            matchesObj = matches.creatematches(text1_start_line=start_pos['start_line'],
                                               text1_start_pos=start_pos['start_index'],
                                               text1_end_line=start_pos['end_line'],
                                               text1_end_pos=start_pos['end_index'],
                                               text2_start_line=end_pos['start_line'],
                                               text2_start_pos=end_pos['start_index'],
                                               text2_end_line=end_pos['end_line'], text2_end_pos=end_pos['end_index'],
                                               len=match['j'], enabled=True)
            matchesObj.save()
            # 相似度匹配关联表
            similarity_matchesObj = similarity_matches.createsimilarity_matches(similarity_id=similarityObj,
                                                                                match_id=matchesObj,
                                                                                enabled=True)
            similarity_matchesObj.save()


def thread_task2(files_entry):
    """
    子线程任务，计算文件对的文本相似度
    :param files_entry:
    :return:
    """
    # lock.acquire()
    similarity_result = compute_javaFileContent_similarity({"compute_files_entry_set": [
        {"filepath1": files_entry['filepath1'], "filepath2": files_entry['filepath2'],
         "struct_similarity": files_entry.get("struct_similarity"),
         "attribute_similarity": files_entry.get("attribute_similarity")}]}.__str__())
    # lock.release()
    return similarity_result


def simple_detect_file(forder, detect_recordObj):
    """
    对文件内所有文件进行简单检测
    :param forder:
    :param detect_recordObj:
    :return:
    """
    javafile_list = walkFile(forder)
    javafileObj_list = {}
    similarity_listObj = {}
    files_entry_list = []
    similarity_result_list = []
    max_similarity_result_list = {}
    if javafile_list.__len__() >= 2:
        for i in range(javafile_list.__len__() - 1):
            file1 = javafile_list.__getitem__(i)
            for j in range(i + 1, javafile_list.__len__()):
                file2 = javafile_list.__getitem__(j)
                files_entry_list.append({"filepath1": file1, "filepath2": file2})
                # similarity_reult = compute_javaFileContent_similarity({"compute_files_entry_set": [{"filepath1": file1,"filepath2": file2}]}.__str__())

        with ThreadPoolExecutor(max_workers=8) as pool:
            # print(id(pool))
            # 使用线程执行map计算
            # 后面元组有3个元素，因此程序启动3条线程来执行action函数
            results = pool.map(thread_task2, files_entry_list)
            similarity_result_list = list(results)
            # for r in results:
            #     item = r.get("similarity_files_entry_set")[0]
            #     print("%s 与 %s 相似度是: %f" % (item["filepath1"], item["filepath2"], item["similarity"]))

            # similarity_reult_list.append(r)
        # 写入数据库
        # try:

        # 写文件组表
        file_groupObj = file_group.createfile_group(name=forder.split(os.path.sep)[-1],
                                                    file_num=javafile_list.__len__(), exception_file_num=0,
                                                    normal_file_num=javafile_list.__len__(),
                                                    enabled=True)
        file_groupObj.save()
        # 检测记录
        detect_recordObj.file_num = file_groupObj.file_num
        detect_recordObj.normal_file_num = file_groupObj.normal_file_num
        detect_recordObj.exception_file_num = file_groupObj.exception_file_num
        detect_recordObj.save()
        # 检测记录-文件组关联
        record_groupObj = record_group.createrecord_group(record_id=detect_recordObj, group_id=file_groupObj,
                                                          enabled=True)
        record_groupObj.save()

        # 写入文件表，名字、路径、内容、type、编码、
        for javafile in javafile_list:
            fileObj = file.createfile(name=os.path.basename(javafile).split('.')[0],
                                      path=javafile[forder.__len__() + 1:], content=None,
                                      type=os.path.basename(javafile).split('.')[1], encoding=None, copy_rank=0,
                                      is_normal=True, enabled=True)
            fileObj.save()
            similarity_listObj.__setitem__(fileObj.id, {})

            file_group_fileObj = file_group_file.createfile_group_file(group_id=file_groupObj,
                                                                       file_id=fileObj, enabled=True)
            file_group_fileObj.save()
            javafileObj_list.__setitem__(javafile, fileObj.id)
        # 写入相似度表
        for similarity_result in similarity_result_list:
            item = similarity_result.get("similarity_files_entry_set")[0]
            file1 = file.objects.filter(id=javafileObj_list.get(item['filepath1'])).first()
            file2 = file.objects.filter(id=javafileObj_list.get(item['filepath2'])).first()
            similarityObj = similarity.createsimilarity(file1_id=file1,
                                                        file2_id=file2,
                                                        attribute_similarity=None,
                                                        struct_similarity=None,
                                                        sample_text_similarity=None,
                                                        text_similarity=item['similarity'],
                                                        similarity=item['similarity'],
                                                        is_max_similarity=False, enabled=True)
            similarityObj.save()
            # 找到最大相似度文件对
            similarity1_dict = similarity_listObj[similarityObj.file1_id.id]
            if similarity1_dict.get("max_similarity") is None or similarity1_dict.get("max_similarity") < item[
                'similarity']:
                similarity1_dict.__setitem__("max_similarity", item['similarity'])
                similarity1_dict.__setitem__("similarity_id", similarityObj.id)
                similarity1_dict.__setitem__("matches", item['matches'])
                similarity1_dict.__setitem__("file_content1", item['file_content1'])
                similarity1_dict.__setitem__("file_content2", item['file_content2'])
                similarity1_dict.__setitem__("file1_encoding", item['file1_encoding'])
                similarity1_dict.__setitem__("file2_encoding", item['file2_encoding'])
            similarity2_dict = similarity_listObj[similarityObj.file2_id.id]
            if similarity2_dict.get("max_similarity") is None or similarity2_dict.get("max_similarity") < item[
                'similarity']:
                similarity2_dict.__setitem__("max_similarity", item['similarity'])
                similarity2_dict.__setitem__("similarity_id", similarityObj.id)
                similarity2_dict.__setitem__("matches", item['matches'])
                similarity2_dict.__setitem__("file_content1", item['file_content1'])
                similarity2_dict.__setitem__("file_content2", item['file_content2'])
                similarity2_dict.__setitem__("file1_encoding", item['file1_encoding'])
                similarity2_dict.__setitem__("file2_encoding", item['file2_encoding'])

        print("相似度链表遍历完成！")
        # 设置最大匹配对，写入数据库

        similarity_id_set = set()
        for max_similarity_item in similarity_listObj.values():
            if not similarity_id_set.__contains__(max_similarity_item["similarity_id"]):
                similarity_id_set.add(max_similarity_item["similarity_id"])
                similarityObj = similarity.objects.filter(id=max_similarity_item["similarity_id"]).first()
                similarityObj.is_max_similarity = True
                similarityObj.save()
                # 写入matches匹配链表
                # 修改文件
                fileObj1 = file.objects.filter(id=similarityObj.file1_id.id).first()
                fileObj2 = file.objects.filter(id=similarityObj.file2_id.id).first()
                fileObj1.encoding = max_similarity_item['file1_encoding']
                fileObj1.content = max_similarity_item['file_content1']
                fileObj2.encoding = max_similarity_item['file2_encoding']
                fileObj2.content = max_similarity_item['file_content2']
                copy_rank = 0
                if max_similarity_item['max_similarity'] > 0.8:
                    copy_rank = 3
                elif max_similarity_item['max_similarity'] > 0.6:
                    copy_rank = 2
                elif max_similarity_item['max_similarity'] > 0.4:
                    copy_rank = 1
                fileObj1.copy_rank = copy_rank if fileObj1.copy_rank is None or (
                        fileObj1.copy_rank < copy_rank) else fileObj1.copy_rank
                fileObj2.copy_rank = copy_rank if fileObj2.copy_rank is None or (
                        fileObj2.copy_rank < copy_rank) else fileObj2.copy_rank
                fileObj1.save()
                fileObj2.save()
                # 写匹配表

                for match in max_similarity_item['matches']:
                    start_pos = match['start_pos']
                    end_pos = match['end_pos']
                    matchesObj = matches.creatematches(text1_start_line=start_pos['start_line'],
                                                       text1_start_pos=start_pos['start_index'],
                                                       text1_end_line=start_pos['end_line'],
                                                       text1_end_pos=start_pos['end_index'],
                                                       text2_start_line=end_pos['start_line'],
                                                       text2_start_pos=end_pos['start_index'],
                                                       text2_end_line=end_pos['end_line'],
                                                       text2_end_pos=end_pos['end_index'],
                                                       len=match['j'], enabled=True)
                    matchesObj.save()
                    similarity_matchesObj = similarity_matches.createsimilarity_matches(
                        similarity_id=similarity.objects.filter(id=max_similarity_item['similarity_id']).first(),
                        match_id=matchesObj,
                        enabled=True)
                    similarity_matchesObj.save()
        print("最大相似度写入完成！")
        # except Exception as e:
        #     print(e)
        #     return {"result": False, "msg": "数据库写入失败！"}
        return {"result": True, "msg": "检测成功"}
    else:
        print("java文件数量过少")
        return {"result": False, "msg": "java文件数量过少"}


def normal_detect_file(forder, detect_recordObj):
    """
    对文件内所有文件进行普通检测
    :param forder:
    :param detect_recordObj:
    :return:
    """
    javafile_list = walkFile(forder)
    if javafile_list.__len__() >= 2:
        # try:
        result = compute_java_folder_similarity_thread(forder)
        fileObj_list = write_result_table_to_database(result['result_table_list'], detect_recordObj, forder)
        similarityObj_list = write_similarity_list_to_database(result['similarity_list'], fileObj_list)

        write_max_similarity_file_list_to_database(result['max_similarity_file_list'], similarityObj_list,
                                                   fileObj_list)
        # except Exception as e:
        #     print(e)
        #     return {"result": False, "msg": "检测失败，出现异常"}
        return {"result": True, "msg": "检测成功！"}
    else:
        return {"result": False, "msg": "java文件数量过少"}
    # "max_similarity_file_list": max_similarity_file_list
    # 存入数据库


def deep_detect_file(forder, detect_recordObj):
    """
    对文件内所有文件进行深度检测
    :param forder:
    :param detect_recordObj:
    :return:
    """
    javafile_list = walkFile(forder)
    similarity_result_list = []
    if javafile_list.__len__() >= 2:
        # try:
        result = compute_java_folder_similarity_thread(forder)
        fileObj_list = write_result_table_to_database(result['result_table_list'], detect_recordObj, forder)
        similarityObj_list = write_similarity_list_to_database(result['similarity_list'], fileObj_list)

        write_max_similarity_file_list_to_database(result['max_similarity_file_list'], similarityObj_list,
                                                   fileObj_list)
        # 将result['max_similarity_file_list']去重后，进行二次深度检测
        # final_result = compute_javaFileContent_similarity(
        #     {"compute_files_entry_set": remove_duplicate(
        #         list(result["max_similarity_file_list"].values()))}.__str__())
        with ThreadPoolExecutor(max_workers=8) as pool:
            # print(id(pool))
            # 使用线程执行map计算
            # 后面元组有3个元素，因此程序启动3条线程来执行action函数
            results = pool.map(thread_task2, remove_duplicate(
                list(result["max_similarity_file_list"].values())))
            similarity_result_list = list(results)
        # 将similarity_result_list写入数据库
        write_similarity_result_list_to_database(similarity_result_list, fileObj_list)

        # except Exception as e:
        #     print(e)
        #     return {"result": False, "msg": "检测失败，出现异常"}
        return {"result": True, "msg": "检测成功！"}
    else:
        return {"result": False, "msg": "java文件数量过少"}


def simple_detect_folder(forder, detect_recordObj):
    """
    对文件内所有二级文件夹进行简单检测
    :param forder:
    :param detect_recordObj:
    :return:
    """
    group_file_list = []
    file_group_list = []
    files_entry_list = []
    javafileObj_list = {}
    file_groupObj_list = {}
    similarity_listObj = {}
    max_similarity_result_list = {}
    similarity_result_list = []
    javafile_list = walkFile(forder)
    # 将二级文件夹列表中的文件全部删除不检测
    onlyfiles = [os.path.join(forder, f) for f in os.listdir(forder) if f.endswith(".java")]
    for file_item in onlyfiles:
        javafile_list.remove(file_item)

    dirs = [f for f in os.listdir(forder) if os.path.isdir(os.path.join(forder, f))]

    for dir in dirs:
        group_name = forder + os.path.sep + dir
        for f in javafile_list:
            if f.startswith(group_name):
                group_file_list.append({"owner_folder": dir, "file": f})
        file_group_list.append({"dir": dir, "files": walkFile(group_name)})

    if javafile_list.__len__() >= 2:
        for i in range(group_file_list.__len__() - 1):
            file1 = group_file_list.__getitem__(i)
            for j in range(i + 1, group_file_list.__len__()):
                file2 = group_file_list.__getitem__(j)
                if file1['owner_folder'] == file2['owner_folder']:
                    continue
                files_entry_list.append({"filepath1": file1['file'], "filepath2": file2['file']})

        # similarity_reult = compute_javaFileContent_similarity({"compute_files_entry_set": [{"filepath1": file1,"filepath2": file2}]}.__str__())
        with ThreadPoolExecutor(max_workers=8) as pool:
            # 使用线程执行map计算
            # 后面元组有3个元素，因此程序启动3条线程来执行action函数
            results = pool.map(thread_task2, files_entry_list)
            similarity_result_list = list(results)

        # 写入数据库
        # try:
        # 写文件组表
        for file_group_item in file_group_list:
            file_groupObj = file_group.createfile_group(name=file_group_item['dir'],
                                                        file_num=file_group_item['files'].__len__(),
                                                        exception_file_num=0,
                                                        normal_file_num=file_group_item['files'].__len__(),
                                                        enabled=True)
            file_groupObj.save()
            file_groupObj_list.__setitem__(file_groupObj.name, file_groupObj.id)

            # 检测记录-文件组关联
            record_groupObj = record_group.createrecord_group(record_id=detect_recordObj,
                                                              group_id=file_groupObj, enabled=True)
            record_groupObj.save()
        # 检测记录
        detect_recordObj.file_num = javafile_list.__len__()
        detect_recordObj.normal_file_num = javafile_list.__len__()
        detect_recordObj.exception_file_num = 0
        detect_recordObj.save()
        # 写入文件表，名字、路径、内容、type、编码、

        for group_file_item in group_file_list:
            fileObj = file.createfile(name=os.path.basename(group_file_item['file']).split('.')[0],
                                      path=group_file_item['file'][forder.__len__() + 1:], content=None,
                                      type=os.path.basename(group_file_item['file']).split('.')[1], encoding=None,
                                      copy_rank=0,
                                      is_normal=True, enabled=True)

            fileObj.save()
            similarity_listObj.__setitem__(fileObj.id, {})
            # 存入文件组-文件关联对象
            file_groupObj = file_group.objects.filter(
                id=file_groupObj_list.get(group_file_item['owner_folder'])).first()
            file_group_fileObj = file_group_file.createfile_group_file(
                group_id=file_groupObj,
                file_id=fileObj, enabled=True)
            file_group_fileObj.save()
            javafileObj_list.__setitem__(group_file_item['file'], fileObj.id)
        print("写入相似度表--开始")
        # 写入相似度表
        for similarity_result in similarity_result_list:
            item = similarity_result.get("similarity_files_entry_set")[0]
            file1 = file.objects.filter(id=javafileObj_list.get(item['filepath1'])).first()
            file2 = file.objects.filter(id=javafileObj_list.get(item['filepath2'])).first()
            similarityObj = similarity.createsimilarity(file1_id=file1,
                                                        file2_id=file2,
                                                        attribute_similarity=None,
                                                        struct_similarity=None,
                                                        sample_text_similarity=None,
                                                        text_similarity=item['similarity'],
                                                        similarity=item['similarity'],
                                                        is_max_similarity=False, enabled=True)
            similarityObj.save()
            # 找到最大相似度文件对
            similarity1_dict = similarity_listObj[similarityObj.file1_id.id]
            if similarity1_dict.get("max_similarity") is None or similarity1_dict.get("max_similarity") < item[
                'similarity']:
                similarity1_dict.__setitem__("max_similarity", item['similarity'])
                similarity1_dict.__setitem__("similarity_id", similarityObj.id)
                similarity1_dict.__setitem__("matches", item['matches'])
                similarity1_dict.__setitem__("file_content1", item['file_content1'])
                similarity1_dict.__setitem__("file_content2", item['file_content2'])
                similarity1_dict.__setitem__("file1_encoding", item['file1_encoding'])
                similarity1_dict.__setitem__("file2_encoding", item['file2_encoding'])
            similarity2_dict = similarity_listObj[similarityObj.file2_id.id]
            if similarity2_dict.get("max_similarity") is None or similarity2_dict.get("max_similarity") < item[
                'similarity']:
                similarity2_dict.__setitem__("max_similarity", item['similarity'])
                similarity2_dict.__setitem__("similarity_id", similarityObj.id)
                similarity2_dict.__setitem__("matches", item['matches'])
                similarity2_dict.__setitem__("file_content1", item['file_content1'])
                similarity2_dict.__setitem__("file_content2", item['file_content2'])
                similarity2_dict.__setitem__("file1_encoding", item['file1_encoding'])
                similarity2_dict.__setitem__("file2_encoding", item['file2_encoding'])

        print("相似度链表遍历完成！")
        # 设置最大匹配对，写入数据库
        similarity_id_set = set()

        for max_similarity_item in similarity_listObj.values():
            if not similarity_id_set.__contains__(max_similarity_item["similarity_id"]):
                similarity_id_set.add(max_similarity_item["similarity_id"])
                similarityObj = similarity.objects.filter(id=max_similarity_item["similarity_id"]).first()
                similarityObj.is_max_similarity = True
                similarityObj.save()

                # 修改文件
                fileObj1 = file.objects.filter(id=similarityObj.file1_id.id).first()

                fileObj2 = file.objects.filter(id=similarityObj.file2_id.id).first()

                fileObj1.encoding = max_similarity_item['file1_encoding']
                fileObj1.content = max_similarity_item['file_content1']

                fileObj2.encoding = max_similarity_item['file2_encoding']
                fileObj2.content = max_similarity_item['file_content2']
                copy_rank = 0
                if max_similarity_item['max_similarity'] > 0.8:
                    copy_rank = 3
                elif max_similarity_item['max_similarity'] > 0.6:
                    copy_rank = 2
                elif max_similarity_item['max_similarity'] > 0.4:
                    copy_rank = 1
                # if fileObj1.copy_rank != ""
                fileObj1.copy_rank = copy_rank if fileObj1.copy_rank is None or (
                        fileObj1.copy_rank < copy_rank) else fileObj1.copy_rank
                fileObj2.copy_rank = copy_rank if fileObj2.copy_rank is None or (
                        fileObj2.copy_rank < copy_rank) else fileObj2.copy_rank
                fileObj1.save()
                fileObj2.save()
                # 写匹配表
                for match in max_similarity_item['matches']:
                    start_pos = match['start_pos']
                    end_pos = match['end_pos']
                    matchesObj = matches.creatematches(text1_start_line=start_pos['start_line'],
                                                       text1_start_pos=start_pos['start_index'],
                                                       text1_end_line=start_pos['end_line'],
                                                       text1_end_pos=start_pos['end_index'],
                                                       text2_start_line=end_pos['start_line'],
                                                       text2_start_pos=end_pos['start_index'],
                                                       text2_end_line=end_pos['end_line'],
                                                       text2_end_pos=end_pos['end_index'],
                                                       len=match['j'], enabled=True)
                    matchesObj.save()
                    similarity_matchesObj = similarity_matches.createsimilarity_matches(
                        similarity_id=similarity.objects.filter(id=max_similarity_item['similarity_id']).first(),
                        match_id=matchesObj,
                        enabled=True)
                    similarity_matchesObj.save()

        print("最大相似度写入完成！")
        # except Exception as e:
        #     print(e)
        #     return {"result": False, "msg": "数据库写入失败！"}

        return {"result": True, "msg": "检测成功"}
    else:
        print("java文件数量过少")
        return {"result": False, "msg": "java文件数量过少"}


def normal_detect_folder(forder, detect_recordObj):
    """
    对文件内所有二级文件夹进行普通检测
    :param forder:
    :param detect_recordObj:
    :return:
    """
    javafile_list = walkFile(forder)
    if javafile_list.__len__() >= 2:
        # try:
        result = compute_java_project_folder_similarity_thread(forder)
        fileObj_list = write_result_table_to_database(result['result_table_list'], detect_recordObj, forder)
        similarityObj_list = write_similarity_list_to_database(result['similarity_list'], fileObj_list)
        write_max_similarity_file_list_to_database(result['max_similarity_file_list'], similarityObj_list,
                                                   fileObj_list)
        # except Exception as e:
        #     print(e)
        #     return {"result": False, "msg": "检测失败，出现异常"}
        return {"result": True, "msg": "检测成功！"}
    else:
        return {"result": False, "msg": "java文件数量过少"}


def deep_detect_folder(forder, detect_recordObj):
    """
    对文件内所有二级文件夹进行深度检测
    :param forder:
    :param detect_recordObj:
    :return:
    """
    javafile_list = walkFile(forder)
    similarity_result_list = []
    if javafile_list.__len__() >= 2:
        # try:
        result = compute_java_project_folder_similarity_thread(forder)
        print("相似度计算完成！")
        fileObj_list = write_result_table_to_database(result['result_table_list'], detect_recordObj, forder)
        print("result_table_list完成！")
        similarityObj_list = write_similarity_list_to_database(result['similarity_list'], fileObj_list)
        print("similarity_list完成！")
        write_max_similarity_file_list_to_database(result['max_similarity_file_list'], similarityObj_list,
                                                   fileObj_list)
        print("max_similarity_file_list完成！")
        with ThreadPoolExecutor(max_workers=8) as pool:
            # print(id(pool))
            # 使用线程执行map计算
            # 后面元组有3个元素，因此程序启动3条线程来执行action函数
            results = pool.map(thread_task2, remove_duplicate(
                list(result["max_similarity_file_list"].values())))
            similarity_result_list = list(results)
            # 将similarity_result_list写入数据库
        write_similarity_result_list_to_database(similarity_result_list, fileObj_list)
        print("检测成功！！")

        # except Exception as e:
        #     print(e)
        #     return {"result": False, "msg": "检测失败，出现异常"}
        return {"result": True, "msg": "检测成功！"}
    else:
        return {"result": False, "msg": "java文件数量过少"}


# 对文件夹开始检测
def start_detect(record_id):
    detect_recordObj = detect_record.objects.get(id=record_id)
    forder = detect_recordObj.file.path
    func_type = detect_recordObj.func_type
    detect_degree = detect_recordObj.degree
    # 对folder进行预处理
    if os.path.exists(forder):
        # 对folder进行预处理 解决解压出来的文件带有两层目录172015-exam1/172015-exam1/
        dirs = [f for f in os.listdir(forder) if os.path.isdir(os.path.join(forder, f))]
        if dirs.__len__() == 1 and forder.split(os.path.sep)[-1] == dirs[0]:
            forder = forder + os.path.sep + dirs[0]

        starttime = datetime.datetime.now()
        result = {}
        if func_type == '文件检测':
            if detect_degree == "1":
                result = simple_detect_file(forder, detect_recordObj)
            elif detect_degree == "2":
                result = normal_detect_file(forder, detect_recordObj)
            elif detect_degree == "3":
                result = deep_detect_file(forder, detect_recordObj)
        elif func_type == '工程检测':
            if detect_degree == "1":
                result = simple_detect_folder(forder, detect_recordObj)
            elif detect_degree == "2":
                result = normal_detect_folder(forder, detect_recordObj)
            elif detect_degree == "3":
                result = deep_detect_folder(forder, detect_recordObj)
        endtime = datetime.datetime.now()
        detect_recordObj.start_time = starttime.strftime("%Y-%m-%d %H:%M:%S")
        detect_recordObj.end_time = endtime.strftime("%Y-%m-%d %H:%M:%S")
        detect_recordObj.detect_time = (endtime - starttime).seconds
        detect_recordObj.save()
        return result
    else:
        print("文件夹不存在")
        return {"result": False, "msg": "文件夹不存在"}

    # 轻度抄袭检测，检测两两java文件的文本相似度
    # 工程检测

    # 文件检测

    # 中度抄袭检测，检测两两java文件的抽样文本相似度，结构相似度，属性相似度，总相似度。
    # 工程检测

    # 文件检测
    # 重度抄袭检测，全面检测
    # 工程检测

    # 文件检测


# 从数据库中加载file_list
def load_file_list_from_database(file_listobj):
    file_listobj = fileSerializer(file_listobj, many=True).data
    for file_item in file_listobj:
        # 加入similarity_list以及匹配记录
        similarity_list_obj = similarity.objects.filter(
            Q(file1_id=file_item.get("id")) | Q(file2_id=file_item.get("id")))
        similarity_list_obj = similaritySerializer(similarity_list_obj, many=True).data
        # 加入匹配记录
        for similarity_item in similarity_list_obj:
            matches_listObj = matches.objects.filter(
                similarity_matches__similarity_id=similarity_item.get("id"))
            matches_listObj = matchesSerializer(matches_listObj, many=True).data

            similarity_item.__setitem__("matches_list", matches_listObj)

            file1 = deepcopy(file_item)
            similarity_item.__setitem__("file1", file1)
            similarity_item.__setitem__("is_change", file1['id'] != similarity_item['file1_id'])
            fileObj = file.objects.filter(
                id=similarity_item['file2_id'] if similarity_item['file1_id'] == file_item.get("id") else
                similarity_item['file1_id']).first()
            fileObj = fileSerializer(fileObj).data
            similarity_item.__setitem__("file2", fileObj)
            similarity_item.__delitem__('file1_id')
            similarity_item.__delitem__('file2_id')
        file_item.__setitem__("similarity_list", similarity_list_obj)

    return file_listobj


# 处理excel文件，并写入数据库
def process_file_data(file_data, identity, user_id):
    try:
        table = file_data.sheet_by_index(0)
        # print(table)
        nrows = table.nrows  # 总行数
        ncols = table.ncols  # 总列数
        # sheet_row_val = table.row_values(3)
        # sheet_col_val = table.col_values(3)
        # print(sheet_row_val)
        # print(sheet_col_val)
        # for item in sheet_col_val:
        #     print(str(item).split(".")[0])
        creator = None
        if identity == "admin":
            creator = None
        else:
            creator = user.objects.filter(id=user_id).first()

        for i in range(1, table.nrows):
            row_data = table.row_values(i)
            userObj = user.createuser(name=row_data[1].strip(),
                                      phone=row_data[3] if type(row_data[3]).__name__ == "str" else str(
                                          int(row_data[3])),
                                      telephone=row_data[2] if type(row_data[2]).__name__ == "str" else str(
                                          int(row_data[2])),
                                      address=str(row_data[4]).strip(),
                                      enabled=True,
                                      username=str(row_data[0]).strip(), password=str(row_data[5]).strip(),
                                      userface=str(row_data[7]).strip(),
                                      remark=str(row_data[6]).strip(), creator=creator, token=None)
            userObj.save()
    except Exception as e:
        print(e)
        return False
    return True


# 将用户资料写入excel文件
def write_user_info_list_to_excel(list_obj):
    try:  # 创建工作薄
        ws = Workbook(encoding="UTF-8")
        w = ws.add_sheet(u'用户资料')
        w.write(0, 0, '工号')
        w.write(0, 1, u'姓名')
        w.write(0, 2, u'座机号码')
        w.write(0, 3, u'手机号码')
        w.write(0, 4, u'联系地址')
        w.write(0, 5, u'用户密码')
        w.write(0, 6, u'用户备注')
        w.write(0, 7, u'用户头像')
        # 写入数据
        excel_row = 1
        for obj in list_obj:
            data_username = obj.username
            data_name = obj.name
            data_telephone = obj.telephone
            data_phone = obj.phone
            data_address = obj.address
            data_password = obj.password
            data_remark = obj.remark
            data_userface = obj.userface
            w.write(excel_row, 0, data_username)
            w.write(excel_row, 1, data_name)
            w.write(excel_row, 2, data_telephone)
            w.write(excel_row, 3, data_phone)
            w.write(excel_row, 4, data_address)
            w.write(excel_row, 5, data_password)
            w.write(excel_row, 6, data_remark)
            w.write(excel_row, 7, data_userface)
            excel_row += 1
            print(excel_row)
        return {"result": True, "ws": ws}
    except Exception as e:
        print(e)
        return {"result": False, "ws": None}


if __name__ == '__main__':
    # folder = r"C:\Users\w1579\Desktop\test"
    # java_files = walkFile(folder)
    # for i in range(0,java_files.__len__()-1):
    #     for j in range(i+1, java_files.__len__()):
    #         # lock.release()
    #         result_table1 = parse_ast_to_classIfo(parse_javafile_to_ast(java_files.__getitem__(i), "JSON"))
    #         result_table2 = parse_ast_to_classIfo(parse_javafile_to_ast(java_files.__getitem__(j), "JSON"))
    #         # 属性结构相似度
    #         similarity1 = compute_attribute_similarity(result_table1,
    #                                                    result_table2)
    #         # ast结构相似度
    #         similarity_result = compute_struct_similarity(result_table1,
    #                                                       result_table2)
    #         similarity3 = similarity_result.get("score")
    #         distance = similarity_result.get("distance")
    #
    #         # 文本相似度
    #         similarity2 = compute_text_similarity(result_table1, result_table2)
    #
    #         # sum_col = ((result_table1['result_table']['method_num'] + result_table2['result_table'][
    #         #     'method_num']) * 4 + (
    #         #                    result_table1['result_table']['attribute_num'] + result_table2['result_table'][
    #         #                'attribute_num']) * 3 + (
    #         #                    result_table1['result_table']['class_num'] + result_table2['result_table'][
    #         #                'class_num']) * 1 + 9 * 2)
    #
    #         # similarity = similarity1 * ((9 * 2) / sum_col) + similarity2 * (1 - ((9 * 2) / sum_col))
    #         similarity = (1 / 5) * similarity1 + (2 / 5) * similarity2 + (2 / 5) * similarity3
    #         print("%s 与 %s 的相似度为 %f" % (java_files.__getitem__(i),java_files.__getitem__(j),similarity))

    starttime = datetime.datetime.now()
    folder = r"G:\python-study\test6\static\CodePass\file\unzip_file\2020-05-15\21-00-15\172041-exam1\172041-exam1"
    result = compute_java_folder_similarity_thread(folder)

    endtime = datetime.datetime.now()
    print("一共花费秒数如下：")
    print((endtime - starttime).seconds)

    # import datetime
    #
    # starttime = datetime.datetime.now()
    # # compute_java_folder_similarity(folder)
    # result = compute_java_folder_similarity_thread(folder)
    # # print(result['similarity_list'])
    # # for item in result['similarity_list']:
    # #     print(item['java_file1'])
    # #     print(item['java_file2'])
    # #     print("ast_distance: %d ,struct_similarity:%f" % (item['ast_distance'], item['struct_similarity']))
    #     # print(item['ast_distance'])
    #     # print(item['struct_similarity'])
    # # result = compute_java_project_folder_similarity_thread(folder)
    # # print({"compute_files_entry_set":remove_duplicate(list(result["max_similarity_file_list"].values()))}.__str__())
    # # 去掉max_similarity_file_list中重复的字典对象
    # final_result = compute_javaFileContent_similarity(
    #     {"compute_files_entry_set": remove_duplicate(list(result["max_similarity_file_list"].values()))}.__str__())
    # # print(final_result)
    # for item in final_result.get("similarity_files_entry_set"):
    #     print(item['filepath1'])
    #     print(item['filepath2'])
    #     # print(item['matches'])
    #     print(item["similarity"])
    # print("len : %d" % final_result.get("similarity_files_entry_set").__len__())
    # endtime = datetime.datetime.now()
    # print("一共花费秒数如下：")
    # print((endtime - starttime).seconds)

    # G:\python-study\ASTExtractor-master\src\astextractor\ASTExtractor.java
    # ast = parse_javafile_to_ast(r"C:\Users\w1579\Desktop\wsdc\wsdc\src\com\itbaizhan\bean\AdminLoginBean.java", "JSON")
    # ast = parse_javafile_to_ast(r"C:\Users\w1579\Desktop\java实验\172041-exam1\17204125\Main.java", "JSON")
    # print(ast)
    # unzip_file_main(r'C:\Users\w1579\Desktop\java实验\42班第四次试验.zip',
    #                 r"G:\python-study\test6\static\CodePass\file\unzip_file")
    # change_name(r"G:\python-study\test6\static\CodePass\file\unzip_file")
    # tokens1 = ''''''
    # tokens2 = ''''''
    #
    # result = gst(tokens1, tokens2 , 2)
    # print(result)
    # print(result)
    # similarity = compute_javafile_similarity(r"C:\Users\w1579\Desktop\java实验\172041-exam1\17204124\FindMax.java",r"C:\Users\w1579\Desktop\java实验\172041-exam1\17204125\Main.java")
    # print(similarity)
    #
    # print("%s consists for %f of %s " % (file_path1,similarity,file_path2))
    # print(similarity)

    # fp = open("result.json", "w+", encoding="utf-8")

    # fp.write(json.dumps(result_table, ensure_ascii=False, indent=2))
    # fp.seek(0, 0)
    # data = fp.read()
    # fp.close()
    # print(result_table)
# 如果解析的ast中并没有内容或者内容缺失，必须返回这个文件
