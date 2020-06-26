from rest_framework import serializers

from CodePass.models import user, admin, menu, role, user_role, menu_role, msgcontent, oplog, sysmsg, attribute, method, \
    class_table, class_method, class_attribute, file_group, file, file_class, file_group_file, detect_record, \
    record_user, record_group, similarity, matches, similarity_matches


class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        # name, phone, telephone, address, enabled, username, password, userface, remark, token
        fields = (
            'id', 'name', 'phone', 'telephone', 'address', 'enabled', 'username', 'password', 'userface', 'disabled','remark','creator',
            'token')


class adminSerializer(serializers.ModelSerializer):
    class Meta:
        model = admin
        fields = (
            'id', 'name', 'phone', 'telephone', 'address', 'enabled', 'username', 'password', 'userface', 'remark',
            'token')


class menuSerializer(serializers.ModelSerializer):
    class Meta:
        model = menu
        fields = ('id', 'url', 'path','component', 'name', 'iconCls', 'keepAlive', 'requireAuth', 'parentId', 'enabled')


class roleSerializer(serializers.ModelSerializer):
    class Meta:
        model = role
        fields = ('id', 'name', 'nameZh')


class user_roleSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_role
        fields = ('id', 'user', 'role')


class menu_roleSerializer(serializers.ModelSerializer):
    class Meta:
        model = menu_role
        fields = ('id', 'mid', 'rid')


class msgcontentSerializer(serializers.ModelSerializer):
    class Meta:
        model = msgcontent
        fields = ('id', 'title', 'message', 'createDate')


class oplogSerializer(serializers.ModelSerializer):
    class Meta:
        model = oplog
        fields = ('id', 'addDate', 'operate', 'adminid')


class sysmsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = sysmsg
        fields = ('id', 'mid', 'type', 'adminid', 'state')


class attributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = attribute
        fields = ('id', 'type', 'name', 'value', 'enabled')


class methodSerializer(serializers.ModelSerializer):
    class Meta:
        model = method
        fields = ('id', 'name', 'return_type', 'param_list', 'var_sate', 'for_num', 'switch_num', 'if_num', 'while_num',
                  'do_while_num',
                  'var_sate_num', 'enabled')


class class_tableSerializer(serializers.ModelSerializer):
    class Meta:
        model = class_table
        fields = (
        'id', 'name', 'attribute_num', 'method_num', 'for_num', 'switch_num', 'if_num', 'while_num', 'do_while_num',
        'var_sate_num', 'enabled')


class class_methodSerializer(serializers.ModelSerializer):
    class Meta:
        model = class_method
        fields = ('id', 'class_id', 'method_id', 'enabled')


class class_attributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = class_attribute
        fields = ('id', 'class_id', 'attribute_id', 'enabled')


class file_groupSerializer(serializers.ModelSerializer):
    class Meta:
        model = file_group
        fields = ('id', 'name', 'file_num', 'exception_file_num', 'normal_file_num','mild_file_num','moderate_file_num','severe_file_num', 'enabled')


class fileSerializer(serializers.ModelSerializer):
    class Meta:
        model = file
        fields = ('id', 'name', 'path', 'content', 'type', 'encoding', 'copy_rank', 'is_normal', 'enabled')


class file_classSerializer(serializers.ModelSerializer):
    class Meta:
        model = file_class
        fields = ('id', 'file_id', 'class_id', 'enabled')


class file_group_fileSerializer(serializers.ModelSerializer):
    class Meta:
        model = file_group_file
        fields = ('id', 'group_id', 'file_id', 'enabled')


class detect_recordSerializer(serializers.ModelSerializer):
    class Meta:
        model = detect_record
        fields = (
        'id', 'title', 'degree', 'func_type', 'remake', 'file', 'start_time', 'end_time', 'detect_time', 'file_num',
        'exception_file_num', 'normal_file_num','mild_file_num','moderate_file_num','severe_file_num', 'enabled')


class record_userSerializer(serializers.ModelSerializer):
    class Meta:
        model = record_user
        fields = ('id', 'user_id', 'admin_id', 'record_id', 'enabled')


class record_groupSerializer(serializers.ModelSerializer):
    class Meta:
        model = record_group
        fields = ('id', 'record_id', 'group_id', 'enabled')


class similaritySerializer(serializers.ModelSerializer):
    class Meta:
        model = similarity
        fields = ('id', 'file1_id', 'file2_id', 'attribute_similarity', 'struct_similarity', 'sample_text_similarity',
                  'text_similarity','similarity',
                  'is_max_similarity', 'enabled')


class matchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = matches
        fields = ('id','text1_start_line', 'text1_start_pos', 'text1_end_line','text1_end_pos', 'text2_start_line','text2_start_pos','text2_end_line', 'text2_end_pos', 'len', 'enabled')


class similarity_matchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = similarity_matches
        fields = ('id', 'similarity_id', 'match_id', 'enabled')
