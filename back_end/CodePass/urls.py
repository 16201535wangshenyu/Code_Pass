from django.conf.urls import url

from CodePass import views

# 删除迁移文件，删除数据库表，删除codedupldetec.django_migrations中的记录
# python manage.py makemigrations appName
urlpatterns = [

    # 登陆
    url(r'^login/$', views.login, name="login"),
    # 生成验证码
    url(r'^verifyCode/$', views.verifyCode, name="verifyCode"),
    # 用户头像的上传与获取
    url(r'^user_avatar/$', views.user_avatar, name="user_avatar"),
    # 修改个人信息
    url(r'^userinfo/$', views.userinfo, name="userinfo"),
    # 根据用户id获取整个用户信息
    url(r'^user_info_by_id/$', views.user_info_by_id, name="user_info_by_id"),
    # 用户角色信息的修改
    url(r'^user_role_info/$', views.user_role_info, name="user_role_info"),
    # 用户的禁用与开启
    url(r'^disabled_user/$', views.disabled_user, name="disabled_user"),
    # 退出登陆
    url(r'^logout/$', views.quit, name="logout"),
    # 文件上传
    url(r'^fileUpload/$', views.fileUpload, name="fileUpload"),
    # 保存检测记录
    url(r'^saveDetectRecord/$', views.saveDetectRecord, name="saveDetectRecord"),
    # 开始检测start_detect
    url(r'^start_detect/$', views.start_detect, name="start_detect"),
    # 请求检测记录
    url(r'^detect_record_info/$', views.detect_record_info, name="detect_record_info"),
    # 检测记录回馈
    url(r'^detect_feedback_info/$', views.detect_feedback_info, name="detect_feedback_info"),
    # 请求文件组记录
    url(r'^file_group_info/$', views.file_group_info, name="file_group_info"),
    # 请求文件记录
    url(r'^file_info/$', views.file_info, name="file_info"),
    # 用户资料下载
    url(r'^user_info_download/$', views.user_info_download, name="user_info_download"),
    # 用户手册下载
    url(r'^notice_file_download/$', views.notice_file_download, name="notice_file_download"),
    # 用户资料上传
    url(r'^user_info_upload/$', views.user_info_upload, name="user_info_upload"),
    # 得到当前最大的工号
    url(r'^get_max_work_id/$', views.get_max_work_id, name="get_max_work_id"),
    # 角色管理
    url(r'^role_info/$', views.role_info, name="role_info"),
    # 资源管理
    url(r'^menus_info/$', views.menus_info, name="menus_info"),
    # 根据roleid 获取 menu_id set
    url(r'^get_menu_id_set_by_role/$', views.get_menu_id_set_by_role, name="get_menu_id_set_by_role"),

    # test测试
    url(r'^test/$', views.test, name="test"),
    url(r'^test2/$', views.test2, name="test2"),

]
