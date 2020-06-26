import os
from datetime import datetime
import uuid
from urllib.parse import urlencode

import xlrd
from PIL import Image
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from django.http import JsonResponse, QueryDict
from io import BytesIO
from django.http import HttpResponse
from django.utils.encoding import escape_uri_path
from rest_framework.utils import json
from xlwt import Workbook

from CodePass.models import admin, file, detect_record, record_user, user, file_group_file, file_group, detect_feedback
from django.core import serializers
from django.conf import settings
import shutil

from CodePass.utils import utils
from CodePass.serializers import *
from CodePass.utils.utils import parse_jsonStr_to_dict, load_file_list_from_database

'''
待完成：用户登录，附带其所有的资源，实现权限管理。
'''


def login(request):
    if request.method == "POST":
        # 信息格式没多大问题，验证账号和密码的正确性
        username = request.POST.get("username")
        password = request.POST.get("password")
        identity = request.POST.get("identity")
        code = request.POST.get("code")

        data = {}
        if username and password and code and identity:
            if code.lower() == request.session.get('code').lower():
                adminUser = None
                if identity == "admin":
                    adminUser = admin.objects.filter(username=username).filter(password=password).first()
                    if adminUser is not None:
                        adminUser = adminSerializer(adminUser).data
                elif identity == "others":
                    adminUser = user.object1.filter(username=username).filter(password=password).filter(
                        disabled=False).first()
                    if adminUser is not None:
                        adminUser = userSerializer(adminUser).data
                if adminUser:
                    # adminUser = serializers.serialize("json", adminUser)

                    data = {
                        'status': 200,
                        'msg': "登陆成功！",
                        'data': adminUser
                    }

                else:
                    data = {
                        'status': 500,
                        'msg': "用户名或密码错误！",
                    }
            else:
                data = {
                    'status': 500,
                    'msg': "登录失败，验证码不正确",
                    'data': request.session.get('code')
                }

        else:
            data = {
                'status': 500,
                'msg': "登录失败，参数有的为null",
            }

        return JsonResponse(data=data, safe=False)

        # try:
        #     user = User.objects.get(userAccount=nameid)
        #     if user.userPasswd != pswd:
        #         return redirect('/login/')
        # except User.DoesNotExist as e:
        #     return redirect('/login/')
        #
        # # 登陆成功
        # token = time.time() + random.randrange(1, 100000)
        # user.userToken = str(token)
        # user.save()
        # request.session["username"] = user.userName
        # request.session["token"] = user.userToken
        # return redirect('/mine/')


# 退出登录
def quit(request):
    return JsonResponse(data={"status": 200, "msg": "退出成功！"})


# 生成验证码
def verifyCode(request):
    # 初始化画布，初始化画笔
    from captcha.image import ImageCaptcha
    from random import randint
    list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z',
            '', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
            'W', 'X', 'Y', 'Z']
    chars = ''
    for i in range(4):
        chars += list[randint(0, 61)]
    image = ImageCaptcha().generate_image(chars)

    fp = BytesIO()
    image.save(fp, "png")
    request.session['code'] = chars
    return HttpResponse(fp.getvalue(), content_type="image/jpeg")


# 用户头像图片上传与显示
def user_avatar(request):
    # 用户头像请求
    if request.method == "GET":
        img_name = request.GET.get("img")
        if img_name:
            imgFile = os.path.join(settings.UPLOAD_IMG_FILE_DIR, img_name)
            with Image.open(imgFile) as imgfile:
                fp = BytesIO()
                imgfile.save(fp, "png")
                return HttpResponse(fp.getvalue(), content_type="image/jpeg")

        return JsonResponse(data={"status": 500, "msg": "用户头像获取失败！"})

    elif request.method == "POST":
        imgfile = request.FILES.get("file")
        identity = request.POST.get("identity", None)
        user_id = request.POST.get("user_id", None)
        img_name = str(uuid.uuid1()) + ".jpg"
        if imgfile and identity and user_id:
            with open(os.path.join(settings.UPLOAD_IMG_FILE_DIR, img_name), "wb") as img_file:
                for chunk in imgfile.chunks():
                    img_file.write(chunk)
            if identity == "admin":
                adminObj = admin.objects.filter(id=user_id).first()
                adminObj.userface = "/code_pass/user_avatar/?img=" + img_name
                adminObj.save()
            else:
                userObj = admin.objects.filter(id=user_id).first()
                userObj.userface = "/code_pass/user_avatar/?img=" + img_name
                userObj.save()
            return JsonResponse(data={"status": 200, "msg": "更新成功！"})
        return JsonResponse(data={"status": 500, "msg": "头像更新失败！"})


# 个人信息管理
def userinfo(request):
    if request.method == "POST":
        # 添加用户
        creator_id = request.POST.get("creator_id")
        identity = request.POST.get("identity")

        username = request.POST.get("username")
        name = request.POST.get("name")
        telephone = request.POST.get("telephone")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        userface = request.POST.get("userface")
        password = request.POST.get("password")
        remark = request.POST.get("remark")
        if creator_id and identity:

            print(creator_id)
            print(identity)
            creator = None
            if identity == "admin":
                creator = None
            else:
                creator = user.objects.filter(id=creator_id).first()

            userObj = user.createuser(name=name, phone=phone,
                                      telephone=telephone,
                                      address=address, enabled=True,
                                      username=username, password=password,
                                      userface=userface, remark=remark, creator=creator,
                                      token=None)
            userObj.save()
            return JsonResponse(data={"status": 200, "msg": "创建成功！"})
        else:
            return JsonResponse(data={"status": 500, "msg": "参数不合法！"})
        # 标注创建者，表明是谁创建的
    elif request.method == "PUT":
        # 修改用户
        put = QueryDict(request.body)
        id = put.get("id")
        username = put.get("username")

        name = put.get("name")

        phone = put.get("phone")

        telephone = put.get("telephone")

        address = put.get("address")

        userface = put.get("userface")

        password = put.get("password")
        identity = put.get("identity")
        remark = put.get("remark")
        print(id)
        if username is not None and name is not None and phone is not None and telephone is not None and address is not None and userface is not None and password is not None:
            userObj = None
            if identity and identity == "admin":
                userObj = admin.objects.filter(id=id).first()
            else:
                userObj = user.objects.filter(id=id).first()
            userObj.name = name
            userObj.telephone = telephone
            userObj.address = address
            userObj.username = username
            userObj.password = password
            userObj.userface = userface
            userObj.remark = remark
            userObj.save()
            return JsonResponse(data={"status": 200, "msg": "修改成功！"})
        else:
            return JsonResponse(data={"status": 500, "msg": "参数不合法！"})
    elif request.method == "GET":
        id = request.GET.get("id")
        user_id = request.GET.get("user_id")
        identity = request.GET.get("identity")
        name = request.GET.get("name")
        page = request.GET.get("page")
        size = request.GET.get("size")
        # 根据id查用户
        if id and identity:
            userObj = None
            if identity == "admin":
                userObj = admin.objects.filter(id=id).first()
                userObj = adminSerializer(userObj).data
            else:
                userObj = user.objects.filter(id=id).first()
                userObj = userSerializer(userObj).data
            return JsonResponse(data={"status": 200, "msg": "查询成功！", "data": userObj}, safe=False)
        # 查询用户列表
        if identity and user_id:
            # 管理员得到全部的用户列表
            user_list = []
            total = 0
            if identity == "admin":
                if name:
                    user_list = user.object1.filter(creator=None).filter(name__contains=name).order_by("id")
                else:
                    user_list = user.object1.filter(creator=None).order_by("id")

                total = user_list.count()
                paginator = Paginator(user_list, size)
                try:
                    user_list = paginator.page(page).object_list
                except PageNotAnInteger:
                    user_list = paginator.page(1).object_list
                except EmptyPage:
                    user_list = paginator.page(paginator.num_pages).object_list
                user_list = userSerializer(user_list, many=True).data
                for user_item in user_list:
                    userObj = user.objects.filter(id=user_item['id']).first()
                    role_listObj = role.object1.filter(user_role__user=userObj)
                    role_listObj = roleSerializer(role_listObj, many=True).data
                    user_item.__setitem__("role_list", role_listObj)

            elif identity == "others":
                creator = user.object1.get(id=user_id)
                if name:
                    user_list = user.object1.filter(creator=creator).filter(name__contains=name).order_by("id")
                else:
                    user_list = user.object1.filter(creator=creator).order_by("id")
                total = user_list.count()
                paginator = Paginator(user_list, size)
                try:
                    user_list = paginator.page(page).object_list
                except PageNotAnInteger:
                    user_list = paginator.page(1).object_list
                except EmptyPage:
                    user_list = paginator.page(paginator.num_pages).object_list
                user_list = userSerializer(user_list, many=True).data
                for user_item in user_list:
                    userObj = user.objects.filter(id=user_item['id']).first()
                    role_listObj = role.object1.filter(user_role__user=userObj)
                    role_listObj = roleSerializer(role_listObj, many=True).data
                    user_item.__setitem__("role_list", role_listObj)
            data = {"user_list": user_list, "total": total}
            return JsonResponse(data={"status": 200, "msg": "查询成功！", "data": data}, safe=False)
        return JsonResponse(data={"status": 500, "msg": "参数不合法！"})

    elif request.method == "DELETE":
        # 删除用户
        params = request.get_full_path().split("?")[1]
        ids = params.split("=")[1]
        ids = ids.rstrip(",")
        user_id_list = ids.split(",")
        if user_id_list:
            for user_id in user_id_list:
                userObj = user.objects.filter(id=int(user_id)).first()
                userObj.enabled = False
                userObj.save()
            return JsonResponse(data={"status": 200, "msg": "删除成功！"})
        else:
            return JsonResponse(data={"status": 500, "msg": "参数不合法！"})

    return JsonResponse(data={"status": 500, "msg": "请求不合法！"})


# 根据用户id得到整个用户信息
def user_info_by_id(request):
    if request.method == "GET":
        user_id = request.GET.get("user_id")
        if user_id:
            userObj = user.objects.filter(id=user_id).first()
            userObj = userSerializer(userObj).data
            if userObj is not None:
                role_listObj = role.object1.filter(user_role__user__id=userObj['id'])
                role_listObj = roleSerializer(role_listObj, many=True).data
                userObj.__setitem__("role_list", role_listObj)
            return JsonResponse(data={"status": 200, "data": userObj}, safe=False)
        else:
            return JsonResponse(data={"status": 500, "msg": "非法参数！"})

    return JsonResponse(data={"status": 500, "msg": "非法请求！"})


# 禁用与开启用户
def disabled_user(request):
    if request.method == "PUT":
        put = QueryDict(request.body)
        user_id = put.get("user_id")
        disabled = put.get("disabled")
        print(disabled)
        if disabled == "false":
            disabled = False
        else:
            disabled = True
        userObj = user.objects.filter(id=user_id).first()
        userObj.disabled = disabled
        userObj.save()
        msg = ""
        if disabled is True:
            msg = userObj.name + " 用户已禁用！"
        else:
            msg = userObj.name + " 用户已启用！"
        return JsonResponse(data={"status": 200, "msg": msg})
    return JsonResponse(data={"status": 500, "msg": "非法请求！"})


# 检测文件上传
def fileUpload(request):
    if request.method == "POST":
        upload_file = request.FILES.get("file", None)
        if not upload_file:
            return JsonResponse(data={'status': 500, 'msg': "上传文件为空！"})
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H-%M-%S')
        # 创建上传文件目录
        if not os.path.exists(os.path.join(settings.UPLOAD_FILE_DIR, current_date, current_time)):
            os.makedirs(os.path.join(settings.UPLOAD_FILE_DIR, current_date, current_time))
        destination = open(os.path.join(settings.UPLOAD_FILE_DIR, current_date, current_time, upload_file.name), "wb+")
        for chunk in upload_file.chunks():
            destination.write(chunk)
        destination.close()
        # filename, filetype = os.path.splitext(destination.name)
        # 将文件进行解压处理
        # 创建解压文件目录
        if not os.path.exists(os.path.join(settings.UPLOAD_UNZIP_FILE_DIR, current_date, current_time)):
            os.makedirs(os.path.join(settings.UPLOAD_UNZIP_FILE_DIR, current_date, current_time))
        try:
            utils.unzip_file_main(path=destination.name,
                                  unzip_path=os.path.join(settings.UPLOAD_UNZIP_FILE_DIR, current_date, current_time))
        except Exception as e:
            shutil.rmtree(os.path.join(settings.UPLOAD_UNZIP_FILE_DIR, current_date))
            shutil.rmtree(os.path.join(settings.UPLOAD_FILE_DIR, current_date))
            return JsonResponse({'status': 500, 'msg': "压缩文件有问题，解压出错！"})

        # 将解压后的上传文件信息写入数据库
        fileObj = file.createfile(name=upload_file.name.split(".")[0],
                                  path=os.path.join(settings.UPLOAD_UNZIP_FILE_DIR, current_date, current_time,
                                                    upload_file.name.split(".")[0]), type="DIR", encoding="",
                                  copy_rank=0, is_normal=True, enabled=True, content="")
        fileObj.save()
        fileId = fileObj.id
        return JsonResponse(data={'status': 200, 'file_id': fileId})
    return JsonResponse(data={'status': 500, 'msg': "请求方式不对！"})


# 保存检测记录
def saveDetectRecord(request):
    # 将检测记录写入数据库
    if request.method == "POST":
        person = request.POST.get("user")
        name = request.POST.get('name')
        # 检测类型
        region = request.POST.get('region')
        # 功能类型
        type = request.POST.get('type')
        desc = request.POST.get('desc')
        fileid = request.POST.get('fileid')
        fileObj = file.objects.filter(id=fileid).first()
        # 保存记录
        detect_recordObj = detect_record.createdetect_record(title=name, degree=region, func_type=type, remake=desc,
                                                             file=fileObj, start_time=None, end_time=None,
                                                             detect_time=None, file_num=None,
                                                             exception_file_num=None, normal_file_num=None,
                                                             enabled=True)
        detect_recordObj.save()
        record_id = detect_recordObj.id
        # 保存record_user
        person = parse_jsonStr_to_dict(person)
        if person.get("identity") == "admin":
            record_userObj = record_user.createrecord_user(record_id=record_id, user_id=None, admin_id=person.get("id"),
                                                           enabled=True)
            record_userObj.save()
        elif person.get("identity") == "user":
            record_userObj = record_user.createrecord_user(record_id=record_id, user_id=person.get("id"), admin_id=None,
                                                           enabled=True)
            record_userObj.save()

        # 将检测记录id返回
        return JsonResponse(data={"status": 200, "data": {"record_id": record_id}})

    return JsonResponse(data={"status": 500, "msg": "请求方式不对！"})


# 开始检测
def start_detect(request):
    if request.method == "POST":
        record_id = request.POST.get('record_id')
        print(request.POST)
        record_id = int(record_id)
        print(record_id)
        # try:
        result = utils.start_detect(record_id)
        print("检测完成！")
        if result['result'] is True:
            # 检测记录表
            detect_recordObj = detect_record.objects.filter(id=record_id).first()
            # 文件组记录
            # 轻度抄袭文件个数
            file_group_listObj = file_group.objects.filter(record_group__record_id=record_id)
            # 中度抄袭文件个数
            # 重度抄袭文件个数
            mild_file_num = 0
            moderate_file_num = 0
            severe_file_num = 0
            for item in file_group_listObj:
                item.mild_file_num = file.objects.filter(file_group_file__group_id=item).filter(
                    copy_rank=1).count()
                mild_file_num += item.mild_file_num
                item.moderate_file_num = file.objects.filter(file_group_file__group_id=item).filter(
                    copy_rank=2).count()
                moderate_file_num += item.moderate_file_num
                item.severe_file_num = file.objects.filter(file_group_file__group_id=item).filter(
                    copy_rank=3).count()
                severe_file_num += item.severe_file_num
                item.save()
            # 写入三种文件
            detect_recordObj.mild_file_num = mild_file_num
            detect_recordObj.moderate_file_num = moderate_file_num
            detect_recordObj.severe_file_num = severe_file_num
            detect_recordObj.save()
            detect_recordObj = detect_recordSerializer(detect_recordObj).data

            # file_group_listObj = file_groupSerializer(file_group_listObj, many=True).data
            #
            # for file_group_item in file_group_listObj:
            #
            #     # 文件记录
            #     file_listobj = file.objects.filter(file_group_file__group_id=file_group_item.get("id"))
            #     file_listobj = fileSerializer(file_listobj, many=True).data
            #     for file_item in file_listobj:
            #         # 加入similarity_list以及匹配记录
            #         similarity_list_obj = similarity.objects.filter(
            #             Q(file1_id=file_item.get("id")) | Q(file2_id=file_item.get("id")))
            #         similarity_list_obj = similaritySerializer(similarity_list_obj, many=True).data
            #         # 加入匹配记录
            #         for similarity_item in similarity_list_obj:
            #             matches_listObj = matches.objects.filter(
            #                 similarity_matches__similarity_id=similarity_item.get("id"))
            #             matches_listObj = matchesSerializer(matches_listObj, many=True).data
            #             similarity_item.__setitem__("matches_list", matches_listObj)
            #
            #         file_item.__setitem__("similarity_list", similarity_list_obj)
            #
            #     file_group_item.__setitem__("file_list", file_listobj)
            # detect_recordObj.__setitem__("file_group_list", file_group_listObj)
            data = {
                "record": detect_recordObj,
            }
            # 回传相似度数据 filter() all() exclude() order_by("-id")

            # , "data": data
            return JsonResponse(data={"status": 200, "msg": "检测成功！", "data": data}, safe=False)
        else:
            print(result['msg'])
            return JsonResponse(data={"status": 500, "msg": result['msg']})
        # except Exception as e:
        #
        #     return JsonResponse(data={"status": 500, "msg": "检测失败，出现异常！"})

    return JsonResponse(data={"status": 500, "msg": "请求方式不对！"})


# 检测回馈
def detect_feedback_info(request):
    if request.method == "POST":
        file_id = request.POST.get("file_id")
        copy_rank = request.POST.get("severe_sim")

        if file_id and copy_rank:

            fileObj = file.objects.filter(id=file_id).first()
            detect_feedbackObj = detect_feedback.objects.filter(file=fileObj).first()
            similarityObj = similarity.objects.filter(is_max_similarity=True).filter(
                Q(file1_id=fileObj) | Q(file2_id=fileObj)).first()
            if detect_feedbackObj is not None:
                detect_feedbackObj.text_similarity = similarityObj.text_similarity
                detect_feedbackObj.attribute_similarity = similarityObj.attribute_similarity
                detect_feedbackObj.struct_similarity = similarityObj.struct_similarity
                detect_feedbackObj.copy_rank = copy_rank
                detect_feedbackObj.save()
            else:
                detect_feedbackObj = detect_feedback.createdetect_feedback(file=fileObj,
                                                                           text_similarity=similarityObj.text_similarity,
                                                                           attribute_similarity=similarityObj.attribute_similarity,
                                                                           struct_similarity=similarityObj.struct_similarity,
                                                                           copy_rank=copy_rank
                                                                           )
                detect_feedbackObj.save()
            return JsonResponse(data={"status": 200, "msg": "保存成功，感谢您的反馈！"})
        else:
            return JsonResponse(data={"status": 500, "msg": "非法参数！"})

    return JsonResponse(data={"status": 500, "msg": "非法请求！"})


# 根据不同身份的人列出该人的检测记录
def detect_record_info(request):
    if request.method == "GET":
        record_id = request.GET.get("record_id")
        user_id = request.GET.get("user_id")
        page = request.GET.get("page")
        size = request.GET.get("size")
        identity = request.GET.get("identity")
        # page = request.GET.get("page")
        # size = request.GET.get("size")
        # 查询单个检测记录
        if record_id:
            recordObj = detect_record.objects.filter(id=record_id).first()
            recordObj = detect_recordSerializer(recordObj).data
            return JsonResponse(data={"status": 200, "msg": "查询成功！", "data": recordObj}, safe=False)
        if identity and user_id:

            if identity == "admin":
                record_listObj = detect_record.object1.all().order_by("id")
                total = record_listObj.count()

                deep_detect_num = record_listObj.filter(degree="3").count()
                mid_detect_num = record_listObj.filter(degree="2").count()
                simple_detect_num = record_listObj.filter(degree="1").count()
                project_detect_num = record_listObj.filter(func_type="工程检测").count()
                file_detect_num = record_listObj.filter(func_type="文件检测").count()
                paginator = Paginator(record_listObj, size)
                try:
                    record_listObj = paginator.page(page).object_list
                except PageNotAnInteger:
                    record_listObj = paginator.page(1).object_list
                except EmptyPage:
                    record_listObj = paginator.page(paginator.num_pages).object_list

                record_listObj = detect_recordSerializer(record_listObj, many=True).data
                data = {}
                data.__setitem__("record_list", record_listObj)
                data.__setitem__("deep_detect_num", deep_detect_num)
                data.__setitem__("mid_detect_num", mid_detect_num)
                data.__setitem__("simple_detect_num", simple_detect_num)
                data.__setitem__("project_detect_num", project_detect_num)
                data.__setitem__("file_detect_num", file_detect_num)
                data.__setitem__("total", total)
                return JsonResponse(data={"status": 200, "msg": "查询成功！", "data": data}, safe=False)
            else:
                search_user = user.object1.filter(id=user_id)
                record_listObj = detect_record.object1.filter(record_user__user_id=search_user).order_by()
                total = record_listObj.count()
                deep_detect_num = record_listObj.filter(degree="3").count()
                mid_detect_num = record_listObj.filter(degree="2").count()
                simple_detect_num = record_listObj.filter(degree="1").count()
                project_detect_num = record_listObj.filter(func_type="工程检测").count()
                file_detect_num = record_listObj.filter(func_type="文件检测").count()
                paginator = Paginator(record_listObj, size)
                try:
                    record_listObj = paginator.page(page).object_list
                except PageNotAnInteger:
                    record_listObj = paginator.page(1).object_list
                except EmptyPage:
                    record_listObj = paginator.page(paginator.num_pages).object_list
                record_listObj = detect_recordSerializer(record_listObj, many=True).data
                data = {}
                data.__setitem__("record_list", record_listObj)
                data.__setitem__("deep_detect_num", deep_detect_num)
                data.__setitem__("mid_detect_num", mid_detect_num)
                data.__setitem__("simple_detect_num", simple_detect_num)
                data.__setitem__("project_detect_num", project_detect_num)
                data.__setitem__("file_detect_num", file_detect_num)
                data.__setitem__("total", total)
                return JsonResponse(data={"status": 200, "msg": "查询成功！", "data": data}, safe=False)
        else:
            return JsonResponse(data={"status": 500, "msg": "参数错误！"})
    elif request.method == "DELETE":
        # 删除用户
        params = request.get_full_path().split("?")[1]
        ids = params.split("=")[1]
        ids = ids.rstrip(",")
        record_id_list = ids.split(",")
        for record_id in record_id_list:
            recordObj = detect_record.objects.filter(id=record_id).first()
            recordObj.enabled = False
            recordObj.save()
        return JsonResponse(data={"status": 200, "msg": "删除成功！"})

    return JsonResponse(data={"status": 500, "msg": "请求方式不对！"})


# 根据record_id 获取所有的file_group_list
def file_group_info(request):
    if request.method == "GET":
        page = request.GET.get("page")
        size = request.GET.get("size")
        record_id = request.GET.get("record_id")
        if page and size and record_id:
            recordObj = detect_record.object1.filter(id=record_id).first()
            file_group_listObj = file_group.objects.filter(record_group__record_id=recordObj).order_by("id")
            total = file_group_listObj.count()
            paginator = Paginator(file_group_listObj, size)
            try:
                file_group_listObj = paginator.page(page).object_list
            except PageNotAnInteger:
                file_group_listObj = paginator.page(1).object_list
            except EmptyPage:
                file_group_listObj = paginator.page(paginator.num_pages).object_list
            file_group_listObj = file_groupSerializer(file_group_listObj, many=True).data
            data = {}
            data.__setitem__("file_group_list", file_group_listObj)
            data.__setitem__("total", total)
            return JsonResponse(data={"status": 200, "msg": "文件组列表查询成功！", "data": data}, safe=False)
        else:
            return JsonResponse(data={"status": 500, "msg": "参数不合法！"})
    elif request.method == "DELETE":
        return JsonResponse(data={"status": 200, "msg": "此功能暂未完成！"})

    return JsonResponse(data={"status": 500, "msg": "请求方式不对！"})


# 根据group_id 获取所有的file_list
def file_info(request):
    if request.method == "GET":
        page = request.GET.get("page")
        size = request.GET.get("size")
        group_id = request.GET.get("group_id")
        if page and size and group_id:
            groupObj = file_group.objects.filter(id=group_id).first()
            file_listObj = file.objects.filter(file_group_file__group_id=groupObj).order_by("id")
            total = file_listObj.count()
            paginator = Paginator(file_listObj, size)
            try:
                file_listObj = paginator.page(page).object_list
            except PageNotAnInteger:
                file_listObj = paginator.page(1).object_list
            except EmptyPage:
                file_listObj = paginator.page(paginator.num_pages).object_list
            file_listObj = load_file_list_from_database(file_listObj)

            data = {}
            data.__setitem__("file_list", file_listObj)
            data.__setitem__("total", total)
            return JsonResponse(data={"status": 200, "msg": "文件列表查询成功！", "data": data}, safe=False)
        else:
            return JsonResponse(data={"status": 500, "msg": "参数不合法！"})
    elif request.method == "DELETE":
        return JsonResponse(data={"status": 200, "msg": "此功能暂未完成！"})

    return JsonResponse(data={"status": 500, "msg": "请求方式不对！"})


# 角色的创建、修改、删除、查询
def role_info(request):
    # 创建角色信息
    if request.method == "POST":
        # creator字段为空的为admin创建

        identity = request.POST.get("identity")
        user_id = request.POST.get("user_id")

        name = request.POST.get("name")
        nameZh = request.POST.get("nameZh")
        if identity and name and user_id and nameZh:
            creator = None
            if identity == "admin":
                creator = None
            else:
                creator = user.object1.filter(id=user_id).first()
            roleObj = role.createrole(name=name, nameZh=nameZh, creator=creator, enabled=True)
            roleObj.save()
            return JsonResponse(data={'status': 200, "msg": "创建成功！"})

        return JsonResponse(data={'status': 500, "msg": "参数不合法！"})
    # 修改信息
    elif request.method == "PUT":
        put = QueryDict(request.body)
        mids = put.get("mids")
        mids = mids.split(",")
        role_id = put.get("role_id")
        if mids and role_id:
            menu_role.objects.filter(rid_id=role_id).delete()
            for mid in mids:
                menuObj = menu.objects.filter(id=mid).first()
                roleObj = role.objects.filter(id=role_id).first()
                menu_roleObj = menu_role.createmenu_role(menuObj, roleObj)
                menu_roleObj.save()
            return JsonResponse(data={"status": 200, "msg": "修改成功！"})
        else:
            return JsonResponse(data={"status": 500, "msg": "参数不合法"})
    # 删除信息
    elif request.method == "DELETE":
        params = request.get_full_path().split("?")[1]
        role_id = params.split("=")[1]
        if role_id:
            roleObj = role.object1.filter(id=role_id).first()
            roleObj.enabled = False
            roleObj.save()
            return JsonResponse(data={"status": 200, "msg": "删除成功！"})
        else:
            return JsonResponse(data={"status": 500, "msg": "参数不合法"})
    elif request.method == "GET":
        user_id = request.GET.get("user_id")
        identity = request.GET.get("identity")
        if user_id and identity:
            if identity == "admin":
                role_listObj = role.object1.filter(creator=None)
                role_listObj = roleSerializer(role_listObj, many=True).data

                return JsonResponse(data={"status": 200, "msg": "查询成功！", "data": role_listObj})
            else:
                creator = user.object1.filter(id=user_id)
                role_listObj = role.object1.filter(creator=creator)
                role_listObj = roleSerializer(role_listObj, many=True).data
                return JsonResponse(data={"status": 200, "msg": "查询成功！", "data": role_listObj})
        return JsonResponse(data={"status": 500, "msg": "参数不合法！"})

    return JsonResponse(data={"status": 500, "msg": "请求不合法！"})


# 用户角色信息的修改
def user_role_info(request):
    if request.method == "PUT":
        put = QueryDict(request.body)
        role_ids = put.get("role_ids")
        role_ids = role_ids.split(",")
        user_id = put.get("user_id")
        print(type(role_ids))
        print(role_ids)
        if user_id and role_ids:
            user_role.objects.filter(user_id=user_id).delete()
            if role_ids[0] != '':
                for role_id in role_ids:
                    userObj = user.objects.filter(id=user_id).first()
                    roleObj = role.objects.filter(id=role_id).first()
                    user_roleObj = user_role.createuser_role(userObj, roleObj)
                    user_roleObj.save()
            return JsonResponse(data={"status": 200, "msg": "修改成功！"})
        else:
            return JsonResponse(data={"status": 500, "msg": "参数非法！"})
    return JsonResponse(data={"status": 500, "msg": "请求非法！"})

# 资源信息管理，资源的查看
def menus_info(request):
    if request.method == "GET":
        user_id = request.GET.get("user_id")
        identity = request.GET.get("identity")
        if user_id and identity:
            if identity == "admin":
                # parentObj = menu.objects.filter(id=1).first()
                parent_menu_listObj = menu.objects.filter(parentId_id=1)
                parent_menu_listObj = menuSerializer(parent_menu_listObj, many=True).data
                for menu_item in parent_menu_listObj:
                    menu_children = menu.objects.filter(parentId_id=menu_item['id'])
                    menu_children = menuSerializer(menu_children, many=True).data
                    menu_item.__setitem__("children", menu_children)
                return JsonResponse(data={"status": 200, "msg": "查询成功！", "data": parent_menu_listObj}, safe=False)
            else:
                userObj = user.objects.filter(id=user_id).first()
                role_listObj = role.object1.filter(user_role__user=userObj)
                # role_listObj = roleSerializer(role_listObj,many=True)
                menu_id_set = set()
                menu_parent_id_set = set()
                for role_item in role_listObj:
                    menu_listObj = menu.objects.filter(menu_role__rid=role_item)
                    for menu_item in menu_listObj:
                        menu_id_set.add(menu_item.id)
                        menu_parent_id_set.add(menu_item.parentId.id)
                menu_parent_listObj = menu.objects.filter(id__in=menu_parent_id_set)
                menu_parent_listObj = menuSerializer(menu_parent_listObj, many=True).data
                for parent_item in menu_parent_listObj:
                    menu_children = menu.objects.filter(id__in=menu_id_set).filter(parentId_id=parent_item['id'])
                    menu_children = menuSerializer(menu_children, many=True).data
                    parent_item.__setitem__("children", menu_children)
                return JsonResponse(data={"status": 200, "msg": "查询成功！", "data": menu_parent_listObj}, safe=False)

        else:
            return JsonResponse(data={"status": 500, "msg": "请求参数非法！"})

    return JsonResponse(data={"status": 500, "msg": "非法请求！"})


# 获取某个角色已经拥有的menu_id_set
def get_menu_id_set_by_role(request):
    # from django.core import serializers
    if request.method == "GET":
        role_id = request.GET.get("role_id")
        if role_id:
            menu_id_set = set()
            roleObj = role.objects.filter(id=role_id).first()
            menu_roleObj = menu_role.objects.filter(rid=roleObj)
            for menu_role_item in menu_roleObj:
                menu_id_set.add(menu_role_item.mid.id)
            data = {
                "menu_id_set": list(menu_id_set)
            }
            data = json.dumps(data)
            return JsonResponse(data={"status": 200, "data": data})
        else:
            return JsonResponse(data={"status": 500, "msg": "非法参数！"})

    return JsonResponse(data={"status": 500, "msg": "非法请求！"})


# 用户资料的上传
def user_info_upload(request):
    if request.method == "POST":
        upload_file = request.FILES.get("file", None)
        identity = request.POST.get("identity", None)
        user_id = request.POST.get("user_id", None)
        print(identity)
        print(upload_file)
        if upload_file:
            # 将文件下载下来
            destination = open(os.path.join(settings.TEMP_FILE_DIR, "user_info.xls"), "wb+")
            for chunk in upload_file.chunks():
                destination.write(chunk)
            destination.close()
            # 读取文件内容
            file_data = xlrd.open_workbook(os.path.join(settings.TEMP_FILE_DIR, "user_info.xls"),
                                           encoding_override='utf-8')
            # 处理文件内容并写入数据库
            if utils.process_file_data(file_data, identity, user_id):
                return JsonResponse(data={"status": 200, "msg": "导入成功！"})
            else:
                return JsonResponse(data={"status": 500, "msg": "导入失败，请检查文件内容格式！"})
        else:
            return JsonResponse(data={"status": 200, "msg": "上传文件为空！"})

    return JsonResponse(data={"status": 500, "msg": "请求非法！"})


# 用户资料的下载
def user_info_download(request):
    identity = request.GET.get("identity")
    creator_id = request.GET.get("creator_id")
    creatorObj = None
    if identity == "admin":
        creatorObj = None
    else:
        creatorObj = user.objects.filter(id=creator_id).first()
    list_obj = user.object1.filter(creator=creatorObj).order_by("username")

    result = utils.write_user_info_list_to_excel(list_obj)
    if result['result'] is True:
        ws = result.get("ws")
        sio = BytesIO()
        ws.save(sio)
        sio.seek(0)
        response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=stu_info.xls'
        response.write(sio.getvalue())
        return response
    else:
        return JsonResponse(data={"status": 500, "msg": "导出失败！"})
    # sheet = excel.pe.Sheet([[1, 2], [3, 4]])


# 公告文件下载
def notice_file_download(request):
    if request.method == "GET":
        file_id = request.GET.get("file_id")
        # UPLOAD_NOTICE_FILE_DIR
        fileName = None
        if file_id == "1":
            fileName = "代码抄袭检测系统-用户手册.docx"
        elif file_id == "2":
            fileName = "代码抄袭检测系统-权限控制说明.docx"
        elif file_id == "3":
            fileName = "代码抄袭检测系统-功能说明.docx"
        elif file_id == "4":
            fileName = "代码抄袭检测系统-通知公告.docx"
        with open(os.path.join(settings.UPLOAD_NOTICE_FILE_DIR, fileName), "rb") as notice_file:
            sio = BytesIO()
            while True:
                strb = notice_file.read(1024)
                if strb == b"":
                    break
                sio.write(strb)
            # notice_file.
            sio.seek(0)
            response = HttpResponse(sio.getvalue(),
                                    content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(fileName))
            response.write(sio.getvalue())
            return response
    return JsonResponse(data={"status": 500, "msg": "非法请求~！"})


# 得到当前最大的工号
def get_max_work_id(request):
    userobj = user.object1.all().order_by("username").last()
    max_work_id = int(userobj.username)
    max_work_id += 1
    max_work_id = str(max_work_id).zfill(8)

    return JsonResponse(data={"status": 200, "max_work_id": max_work_id})


# test
def test(request):
    # 检测记录表
    start_time = datetime.now()
    detect_recordObj = detect_record.objects.filter(id=5).first()
    # 文件组记录
    # 轻度抄袭文件个数
    file_group_listObj = file_group.objects.filter(record_group__record_id=5)
    # 中度抄袭文件个数
    # 重度抄袭文件个数
    mild_file_num = 0
    moderate_file_num = 0
    severe_file_num = 0
    for item in file_group_listObj:
        item.mild_file_num = file.objects.filter(file_group_file__group_id=item).filter(copy_rank="mild").count()
        mild_file_num += item.mild_file_num
        item.moderate_file_num = file.objects.filter(file_group_file__group_id=item).filter(
            copy_rank="moderate").count()
        moderate_file_num += item.moderate_file_num
        item.severe_file_num = file.objects.filter(file_group_file__group_id=item).filter(copy_rank="severe").count()
        severe_file_num += item.severe_file_num
        item.save()
    # 写入三种文件
    detect_recordObj.mild_file_num = mild_file_num
    detect_recordObj.moderate_file_num = moderate_file_num
    detect_recordObj.severe_file_num = severe_file_num
    detect_recordObj.save()
    detect_recordObj = detect_recordSerializer(detect_recordObj).data
    file_group_listObj = file_groupSerializer(file_group_listObj, many=True).data

    for file_group_item in file_group_listObj:

        # 文件记录
        file_listobj = file.objects.filter(file_group_file__group_id=file_group_item.get("id"))
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

            file_item.__setitem__("similarity_list", similarity_list_obj)

        file_group_item.__setitem__("file_list", file_listobj)

    detect_recordObj.__setitem__("file_group_list", file_group_listObj)
    data = {
        "record": detect_recordObj,
    }
    end_time = datetime.now()
    print((end_time - start_time).seconds)
    # 回传相似度数据 filter() all() exclude() order_by("-id")

    # , "data": data
    return JsonResponse(data={"status": 200, "msg": "检测成功！", "data": data}, safe=False)


def test2(request):
   return JsonResponse(data={"status":200,"msg":"成功！"})
