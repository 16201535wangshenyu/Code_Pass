from django.db import models


class UserManager1(models.Manager):
    def get_queryset(self):
        return super(UserManager1, self).get_queryset().filter(enabled=True)


# Create your models here.
class user(models.Model):
    # ID
    id = models.AutoField(max_length=11, primary_key=True)
    # 姓名
    name = models.CharField(max_length=32, null=True)
    # 手机号码
    phone = models.CharField(max_length=16, null=True)
    # 住宅电话
    telephone = models.CharField(max_length=16, null=True)
    # 联系地址
    address = models.CharField(max_length=64, null=True)
    # 可用性
    enabled = models.BooleanField(default=True) \
        # disabled 是否禁用
    disabled = models.BooleanField(default=False)
    username = models.CharField(max_length=255, null=True)
    # 密码
    password = models.CharField(max_length=255, null=True)
    # 头像接口
    userface = models.CharField(max_length=255, null=True)
    # 备注
    remark = models.CharField(max_length=255, null=True)
    # 创建者
    creator = models.ForeignKey('self', null=True)
    # touken验证值，每次登陆之后都会更新
    token = models.CharField(max_length=50, null=True)
    object1 = UserManager1()
    objects = models.Manager()

    @classmethod
    def createuser(cls, name, phone, telephone, address, enabled, username, password, userface, remark, creator, token):
        a = cls(name=name, phone=phone, telephone=telephone, address=address, enabled=enabled,
                username=username, password=password, userface=userface, remark=remark, creator=creator, token=token)
        return a


class AdminManager1(models.Manager):
    def get_queryset(self):
        return super(AdminManager1, self).get_queryset().filter(enabled=True)


# 管理员
class admin(models.Model):
    # ID
    id = models.AutoField(max_length=11, primary_key=True)
    # 姓名
    name = models.CharField(max_length=32, null=True)
    # 手机号码
    phone = models.CharField(max_length=11, null=True)
    # 住宅电话
    telephone = models.CharField(max_length=16, null=True)
    # 联系地址
    address = models.CharField(max_length=64, null=True)
    # 可用性
    enabled = models.BooleanField(default=True)
    # 用户名
    username = models.CharField(max_length=255, null=True)
    # 密码
    password = models.CharField(max_length=255, null=True)
    # 头像接口
    userface = models.CharField(max_length=255, null=True)
    # 备注
    remark = models.CharField(max_length=255, null=True)
    # touken验证值，每次登陆之后都会更新
    token = models.CharField(max_length=50, null=True)
    # admin moder管理器
    objects = AdminManager1()

    @classmethod
    def createadmin(cls, name, phone, telephone, address, enabled, username, password, userface, remark, token):
        a = cls(name=name, phone=phone, telephone=telephone, address=address, enabled=enabled,
                username=username, password=password, userface=userface, remark=remark, token=token)
        return a


# 资源表
class menu(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 资源接口
    url = models.CharField(max_length=64, null=True)
    # 路由路径
    path = models.CharField(max_length=64, null=True)
    # 资源组件
    component = models.CharField(max_length=64, null=True)
    # 名称
    name = models.CharField(max_length=64, null=True)
    # 图标
    iconCls = models.CharField(max_length=64, null=True)
    # 是否保持组件状态
    keepAlive = models.BooleanField(default=True)
    # 是否需要授权
    requireAuth = models.BooleanField(default=True)
    # 父组件id
    parentId = models.ForeignKey('self', null=True)
    # 可用性
    enabled = models.BooleanField(default=True)

    @classmethod
    def createmenu(cls, url, component, name, iconCls, keepAlive, requireAuth, parentId, enabled):
        m = cls(url=url, component=component, name=name, iconCls=iconCls, keepAlive=keepAlive,
                requireAuth=requireAuth, parentId=parentId, enabled=enabled)
        return m


class roleManager1(models.Manager):
    def get_queryset(self):
        return super(roleManager1, self).get_queryset().filter(enabled=True)


# 角色表
class role(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 名称
    name = models.CharField(max_length=64, null=True)
    # 英文名称
    nameZh = models.CharField(max_length=64, null=True)
    # 创建者
    creator = models.ForeignKey(user, null=True)
    # 可用性
    enabled = models.BooleanField(default=True)
    objects = models.Manager()
    object1 = roleManager1()

    @classmethod
    def createrole(cls, name, nameZh, creator, enabled=enabled):
        r = cls(name=name, nameZh=nameZh, creator=creator, enabled=enabled)
        return r


# 用户角色表
class user_role(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # user_id
    user = models.ForeignKey(user)
    # role_id
    role = models.ForeignKey(role)

    @classmethod
    def createuser_role(cls, user, role):
        r = cls(user=user, role=role)
        return r


# 资源-角色表
class menu_role(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 资源接口
    mid = models.ForeignKey(menu)
    # 资源组件
    rid = models.ForeignKey(role)

    @classmethod
    def createmenu_role(cls, mid, rid):
        mr = cls(mid=mid, rid=rid)
        return mr


# 系统消息表
class msgcontent(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 消息名称
    title = models.CharField(max_length=64, null=True)
    # 消息内容
    message = models.CharField(max_length=64, null=True)
    # 创建时间
    createDate = models.DateTimeField(auto_now_add=True)

    @classmethod
    def createmsgcontent(cls, title, message):
        mc = cls(title=title, message=message)
        return mc


# 系统操作日志表
class oplog(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 添加日期
    addDate = models.DateTimeField(auto_now_add=True)
    # 操作内容
    operate = models.CharField(max_length=255, null=True)
    # 操作员ID
    adminid = models.ForeignKey(admin, null=True)

    @classmethod
    def createoplog(cls, operate, adminid):
        o = cls(operate=operate, adminid=adminid)
        return o


# admin-msg表
class sysmsg(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 消息id
    mid = models.ForeignKey(msgcontent, null=True)
    # '0表示群发消息',
    type = models.BooleanField(default=False)
    # 这条消息是给谁的
    adminid = models.ForeignKey(admin, null=True)
    # 是否已读
    state = models.BooleanField(default=False)

    @classmethod
    def createsysmsg(cls, mid, type, adminid, state):
        sys = cls(mid=mid, type=type, adminid=adminid, state=state)
        return sys


# 属性表
class attribute(models.Model):
    # ID
    id = models.AutoField(max_length=11, primary_key=True)
    # 类型
    type = models.CharField(max_length=255, null=True)
    # 名称
    name = models.CharField(max_length=255, null=True)
    # 属性值
    value = models.CharField(max_length=255, null=True)
    # 可用性
    enabled = models.BooleanField(default=True)

    # attribute moder管理器
    # objects = AdminManager1()

    @classmethod
    def createattribute(cls, type, name, value, enabled):
        a = cls(type=type, name=name, value=value, enabled=enabled)
        return a


# 方法表
class method(models.Model):
    # ID
    id = models.AutoField(max_length=11, primary_key=True)
    # 名字
    name = models.CharField(max_length=255, null=True)
    # 返回值类型
    return_type = models.CharField(max_length=255, null=True)
    # 所有参数列表
    param_list = models.CharField(max_length=255, null=True)
    # 变量声明语句
    var_sate = models.TextField(null=True)
    # for语句个数
    for_num = models.IntegerField(null=True)
    # switch语句个数
    switch_num = models.IntegerField(null=True)
    # if语句个数
    if_num = models.IntegerField(null=True)
    # while语句个数
    while_num = models.IntegerField(null=True)
    # do_while语句个数
    do_while_num = models.IntegerField(null=True)
    # 表达式语句个数
    express_state_num = models.IntegerField(null=True)
    # 变量声明语句个数
    var_sate_num = models.IntegerField(null=True)
    # 可用性
    enabled = models.BooleanField(default=True)

    @classmethod
    def createmethod(cls, name, return_type, param_list, var_sate, for_num, switch_num, if_num, while_num, do_while_num,
                     var_sate_num, enabled):
        a = cls(name=name, return_type=return_type, param_list=param_list, var_sate=var_sate, for_num=for_num,
                switch_num=switch_num, if_num=if_num, while_num=while_num, do_while_num=do_while_num,
                var_sate_num=var_sate_num, enabled=enabled)
        return a


# 类表
class class_table(models.Model):
    # 类ID
    id = models.AutoField(max_length=11, primary_key=True)
    # 类名
    name = models.CharField(max_length=255)
    # 属性个数
    attribute_num = models.IntegerField(null=True)
    # 方法个数
    method_num = models.IntegerField(null=True)
    # for语句个数
    for_num = models.IntegerField(null=True)
    # switch语句个数
    switch_num = models.IntegerField(null=True)
    # if语句个数
    if_num = models.IntegerField(null=True)
    # while语句个数
    while_num = models.IntegerField(null=True)
    # do_while语句个数
    do_while_num = models.IntegerField(null=True)
    # 表达式语句个数
    express_state_num = models.IntegerField(null=True)
    # 变量声明语句个数
    var_sate_num = models.IntegerField(null=True)
    # 可用性
    enabled = models.BooleanField(default=True)

    @classmethod
    def createclass(cls, name, attribute_num, method_num, for_num, switch_num, if_num, while_num, do_while_num,
                    var_sate_num, enabled):
        a = cls(name=name, attribute_num=attribute_num, method_num=method_num, for_num=for_num,
                switch_num=switch_num, if_num=if_num, while_num=while_num, do_while_num=do_while_num,
                var_sate_num=var_sate_num, enabled=enabled)
        return a


# 类-方法-属性表
# class class_method_attribute(models.Model):
#     # id
#     id = models.AutoField(max_length=11, primary_key=True)
#     # 类id
#     class_id = models.ForeignKey(class_table)
#     # 方法id
#     method_id = models.ForeignKey(method)
#     # 属性id
#     attribute_id = models.ForeignKey(attribute)
#     # 可用性
#     enabled = models.BooleanField(default=True)
#
#     @classmethod
#     def createclass_method_attribute(cls, class_id, method_id, attribute_id, enabled):
#         a = cls(class_id=class_id, method_id=method_id, attribute_id=attribute_id, enabled=enabled)
#         return a
# 类-方法表关联
# 类-方法关联
class class_method(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 类id
    class_id = models.ForeignKey(class_table, null=True)
    # 方法id
    method_id = models.ForeignKey(method, null=True)
    # 可用性
    enabled = models.BooleanField(default=True)

    @classmethod
    def createclass_method(cls, class_id, method_id, enabled):
        a = cls(class_id=class_id, method_id=method_id, enabled=enabled)
        return a


# 类属性表关联
class class_attribute(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 类id
    class_id = models.ForeignKey(class_table, null=True)
    # 属性id
    attribute_id = models.ForeignKey(attribute, null=True)
    # 可用性
    enabled = models.BooleanField(default=True)

    @classmethod
    def createclass_attribute(cls, class_id, attribute_id, enabled):
        a = cls(class_id=class_id, attribute_id=attribute_id, enabled=enabled)
        return a


# 文件组表
class file_group(models.Model):
    # 组id
    id = models.AutoField(max_length=11, primary_key=True)
    # 组名
    name = models.CharField(max_length=255, null=True)
    # 组文件个数
    file_num = models.IntegerField(null=True)
    # 组内异常文件个数
    exception_file_num = models.IntegerField(null=True)
    # 正常文件个数
    normal_file_num = models.IntegerField(null=True)
    # 轻度抄袭文件个数
    mild_file_num = models.IntegerField(null=True)
    # 中度抄袭文件个数
    moderate_file_num = models.IntegerField(null=True)
    # 重度抄袭文件个数
    severe_file_num = models.IntegerField(null=True)
    # 可用性
    enabled = models.BooleanField(default=True)

    @classmethod
    def createfile_group(cls, name, file_num, exception_file_num, normal_file_num, enabled):
        a = cls(name=name, file_num=file_num, exception_file_num=exception_file_num, normal_file_num=normal_file_num,
                enabled=enabled)
        return a


# 文件表
class file(models.Model):
    # 文件id
    id = models.AutoField(max_length=11, primary_key=True)
    # 文件名
    name = models.CharField(max_length=255, null=True)
    # 文件路径
    path = models.CharField(max_length=255, null=True)
    # 文件内容
    content = models.TextField(null=True)
    # 文件类型
    type = models.CharField(max_length=128, null=True)
    # 文件编码
    encoding = models.CharField(max_length=128, null=True)
    # 抄袭等级 正常文件 进行第二次检测轻度抄袭文件  进行完检测，有大匹配串或者约前50%为中度抄袭文件 文本相似度大于80%的为中度抄袭文件。
    # mild 1  moderate 2 severe 3
    copy_rank = models.IntegerField(default=0)
    # 是否异常
    is_normal = models.BooleanField(default=True)
    # 可用性
    enabled = models.BooleanField(default=True)

    @classmethod
    def createfile(cls, name, path, content, type, encoding, copy_rank, is_normal, enabled):
        a = cls(name=name, path=path, content=content, type=type, encoding=encoding, copy_rank=copy_rank,
                is_normal=is_normal, enabled=enabled)
        return a


# 文件-类表
class file_class(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 文件ID
    file_id = models.ForeignKey(file, null=True)
    # 类ID
    class_id = models.ForeignKey(class_table, null=True)
    # 可用性
    enabled = models.BooleanField(default=True)

    @classmethod
    def createfile_class(cls, file_id, class_id, enabled):
        a = cls(file_id=file_id, class_id=class_id, enabled=enabled)
        return a


# 文件组-文件表
class file_group_file(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 文件组id
    group_id = models.ForeignKey(file_group, null=True)
    # 文件id
    file_id = models.ForeignKey(file, null=True)
    # 可用性
    enabled = models.BooleanField(default=True)

    @classmethod
    def createfile_group_file(cls, group_id, file_id, enabled):
        a = cls(group_id=group_id, file_id=file_id, enabled=enabled)
        return a


class detect_recordManager1(models.Manager):
    def get_queryset(self):
        return super(detect_recordManager1, self).get_queryset().filter(enabled=True)


# 检测记录表
class detect_record(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 记录标题
    title = models.CharField(max_length=128, null=True)
    # 检测程度  1：简单检测 2、普通检测 3、深度检测
    degree = models.CharField(max_length=255, default="SIMPLE")
    # 功能类型 工程检测 文件检测
    func_type = models.CharField(max_length=255, default="PROJECT")
    # 记录备注
    remake = models.CharField(max_length=255, null=True)
    # 检测文件
    file = models.ForeignKey(file, null=True)
    # 开始时间
    start_time = models.DateTimeField(null=True)
    # 结束时间
    end_time = models.DateTimeField(null=True)
    # 检测时长
    detect_time = models.IntegerField(null=True)
    # 检测总文件个数
    file_num = models.IntegerField(null=True)
    # 异常文件个数
    exception_file_num = models.IntegerField(null=True)
    # 正常文件个数
    normal_file_num = models.IntegerField(null=True)
    # 轻度抄袭文件个数
    mild_file_num = models.IntegerField(null=True)
    # 中度抄袭文件个数
    moderate_file_num = models.IntegerField(null=True)
    # 重度抄袭文件个数
    severe_file_num = models.IntegerField(null=True)
    # 可用性
    enabled = models.BooleanField(default=True)
    objects = models.Manager()
    object1 = detect_recordManager1()

    @classmethod
    def createdetect_record(cls, title, degree, func_type, remake, file, start_time, end_time, detect_time, file_num,
                            exception_file_num, normal_file_num, enabled):
        a = cls(title=title, degree=degree, func_type=func_type, remake=remake, file=file, start_time=start_time,
                end_time=end_time, detect_time=detect_time, file_num=file_num,
                exception_file_num=exception_file_num, normal_file_num=normal_file_num, enabled=enabled)
        return a


# 检测回馈表
class detect_feedback(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # record
    file = models.ForeignKey(file)
    # 最大相似度对中的文本相似度
    text_similarity = models.FloatField(null=True, default=0)
    # 最大相似度对中的属性相似度
    attribute_similarity = models.FloatField(null=True, default=0)
    # 最大相似度对中的结构相似度
    struct_similarity = models.FloatField(null=True, default=0)
    # 期望的文件抄袭等级
    copy_rank = models.IntegerField(null=True, default=0)

    @classmethod
    def createdetect_feedback(cls, file, text_similarity, attribute_similarity, struct_similarity, copy_rank):
        a = cls(file=file, text_similarity=text_similarity, attribute_similarity=attribute_similarity,
                struct_similarity=struct_similarity, copy_rank=copy_rank)
        return a


# 检测记录-用户表
class record_user(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 用户id
    user_id = models.ForeignKey(user, null=True)
    # 管理员id
    admin_id = models.ForeignKey(admin, null=True)
    # 记录id
    record_id = models.ForeignKey(detect_record, null=True)
    # 可用性
    enabled = models.BooleanField(default=True)

    @classmethod
    def createrecord_user(cls, user_id, admin_id, record_id, enabled):
        a = cls(user_id=user_id, admin_id=admin_id, record_id=record_id, enabled=enabled)
        return a


# 检测记录-文件组表
class record_group(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 记录id
    record_id = models.ForeignKey(detect_record, null=True)
    # 文件组id
    group_id = models.ForeignKey(file_group, null=True)
    # 可用性
    enabled = models.BooleanField(default=True)

    @classmethod
    def createrecord_group(cls, record_id, group_id, enabled):
        a = cls(record_id=record_id, group_id=group_id, enabled=enabled)
        return a


# 相似度表
class similarity(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 文件1id
    file1_id = models.ForeignKey(file, null=True, related_name='file1_foreign')
    # 文件2id
    file2_id = models.ForeignKey(file, null=True, related_name='file2_foreign')
    # 程序属性相似度
    attribute_similarity = models.FloatField(null=True)
    # 结构相似度
    struct_similarity = models.FloatField(null=True)
    # 抽样文本相似度
    sample_text_similarity = models.FloatField(null=True)
    # java文本相似度
    text_similarity = models.FloatField(null=True)
    # 总相似度
    similarity = models.FloatField(null=True)
    # 是不是文件对的最大相似度
    is_max_similarity = models.BooleanField(default=False)
    # 可用性
    enabled = models.BooleanField(default=True)

    @classmethod
    def createsimilarity(cls, file1_id, file2_id, attribute_similarity, struct_similarity, sample_text_similarity,
                         text_similarity, similarity,
                         is_max_similarity, enabled):
        a = cls(file1_id=file1_id, file2_id=file2_id, attribute_similarity=attribute_similarity,
                struct_similarity=struct_similarity,
                sample_text_similarity=sample_text_similarity, text_similarity=text_similarity, similarity=similarity,
                is_max_similarity=is_max_similarity, enabled=enabled)
        return a


# 文件文本匹配表
class matches(models.Model):
    # 匹配id
    id = models.AutoField(max_length=11, primary_key=True)
    # 文本一起始行
    text1_start_line = models.IntegerField(null=True)
    # 文本一起始标记
    text1_start_pos = models.IntegerField(null=True)
    # 文本一结束行
    text1_end_line = models.IntegerField(null=True)
    # 文本一结束标记
    text1_end_pos = models.IntegerField(null=True)

    # 文本二起始行
    text2_start_line = models.IntegerField(null=True)
    # 文本二起始标记
    text2_start_pos = models.IntegerField(null=True)
    # 文本二结束行
    text2_end_line = models.IntegerField(null=True)
    # 文本二结束标记
    text2_end_pos = models.IntegerField(null=True)

    # 匹配长度
    len = models.IntegerField(null=True)
    # 可用性
    enabled = models.BooleanField(default=True)

    @classmethod
    def creatematches(cls, text1_start_line, text1_start_pos, text1_end_line, text1_end_pos, text2_start_line,
                      text2_start_pos, text2_end_line, text2_end_pos, len, enabled):
        a = cls(text1_start_line=text1_start_line, text1_start_pos=text1_start_pos, text1_end_line=text1_end_line,
                text1_end_pos=text1_end_pos, text2_start_line=text2_start_line, text2_start_pos=text2_start_pos,
                text2_end_line=text2_end_line, text2_end_pos=text2_end_pos, len=len, enabled=enabled)
        return a


# 相似度-匹配表
class similarity_matches(models.Model):
    # id
    id = models.AutoField(max_length=11, primary_key=True)
    # 相似度id
    similarity_id = models.ForeignKey(similarity, null=True)
    # 匹配id
    match_id = models.ForeignKey(matches, null=True)
    # 可用性
    enabled = models.BooleanField(default=True)

    @classmethod
    def createsimilarity_matches(cls, similarity_id, match_id, enabled):
        a = cls(similarity_id=similarity_id, match_id=match_id, enabled=enabled)
        return a
