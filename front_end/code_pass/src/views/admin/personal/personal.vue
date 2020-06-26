<template>
    <div v-if="current_user" style="margin-top: 50px;margin-left: 50px">
        <el-card class="box-card" style="width: 400px">
            <div slot="header" class="clearfix">
                <span>{{current_user.name}}</span>
            </div>
            <div>
                <div style="display: flex;justify-content: center">
                    <el-upload
                            :show-file-list="false"
                            action="string"
                            :http-request="avatarUpload"
                    >

                        <img title="点击修改用户图像" :src="current_user.userface" style="width: 100px;height: 100px;border-radius: 50px"
                             alt="">
                    </el-upload>
                </div>
                <div class="info">工作账号：
                    <el-tag>{{current_user.username}}</el-tag>
                </div>
                <div class="info">电话号码：
                    <el-tag>{{current_user.telephone}}</el-tag>
                </div>
                <div class="info">手机号码：
                    <el-tag>{{current_user.phone}}</el-tag>
                </div>
                <div class="info">居住地址：
                    <el-tag>{{current_user.address}}</el-tag>
                </div>
                <!--<div>用户标签：-->
                    <!--<el-tag type="success" style="margin-right: 5px" v-for="(r,index) in hr.roles" :key="index">-->
                        <!--{{r.nameZh}}-->
                    <!--</el-tag>-->
                <!--</div>-->
                <div style="display: flex;justify-content: space-around;margin-top: 10px">
                    <el-button type="primary" @click="showUpdateUserInfoView">修改信息</el-button>
                    <el-button type="danger" @click="showUpdatePasswdView">修改密码</el-button>
                </div>
            </div>
        </el-card>
        <el-dialog
                title="修改用户信息"
                :visible.sync="dialogVisible"
                width="30%">
            <div>
                <table>
                    <tr>
                        <td>
                            <el-tag>用户昵称：</el-tag>
                        </td>
                        <td>
                            <el-input v-model="user.name"></el-input>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <el-tag>电话号码：</el-tag>
                        </td>
                        <td>
                            <el-input v-model="user.telephone"></el-input>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <el-tag>手机号码：</el-tag>
                        </td>
                        <td>
                            <el-input v-model="user.phone"></el-input>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <el-tag>用户地址：</el-tag>
                        </td>
                        <td>
                            <el-input v-model="user.address"></el-input>
                        </td>
                    </tr>
                </table>
            </div>
            <span slot="footer" class="dialog-footer">
                <el-button @click="dialogVisible = false">取 消</el-button>
                <el-button type="primary" @click="updateUserInfo">确 定</el-button>
            </span>
        </el-dialog>

        <el-dialog
                title="修改密码"
                :visible.sync="passwdDialogVisible"
                width="30%">
            <div>
                <el-form :model="ruleForm" status-icon :rules="rules" ref="ruleForm" label-width="100px"
                         class="demo-ruleForm">
                    <el-form-item label="请输入旧密码" prop="oldpass">
                        <el-input type="password" v-model="ruleForm.oldpass" autocomplete="off"></el-input>
                    </el-form-item>
                    <el-form-item label="请输入新密码" prop="pass">
                        <el-input type="password" v-model="ruleForm.pass" autocomplete="off"></el-input>
                    </el-form-item>
                    <el-form-item label="新确认密码" prop="checkPass">
                        <el-input type="password" v-model="ruleForm.checkPass" autocomplete="off"></el-input>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" @click="submitForm('ruleForm')">提交</el-button>
                        <el-button @click="resetForm('ruleForm')">重置</el-button>
                    </el-form-item>
                </el-form>
            </div>
        </el-dialog>
    </div>
</template>

<script>
    export default {
        name: "personal",
        data() {

            let validatePass = (rule, value, callback) => {
                if (value === '') {
                    callback(new Error('请输入密码'));
                } else {
                    if (this.ruleForm.checkPass !== '') {
                        this.$refs.ruleForm.validateField('checkPass');
                    }
                    callback();
                }
            };
            let validatePass2 = (rule, value, callback) => {
                if (value === '') {
                    callback(new Error('请再次输入密码'));
                } else if (value !== this.ruleForm.pass) {
                    callback(new Error('两次输入密码不一致!'));
                } else {
                    callback();
                }
            };
            return {
                ruleForm: {
                    oldpass: '',
                    pass: '',
                    checkPass: ''
                },
                rules: {
                    oldpass: [
                        {validator: validatePass, trigger: 'blur'}
                    ],
                    pass: [
                        {validator: validatePass, trigger: 'blur'}
                    ],
                    checkPass: [
                        {validator: validatePass2, trigger: 'blur'}
                    ]
                },
                // user: null,
                user: {
                    id:"",
                    username:"",
                    name:"",
                    phone:"",
                    telephone:"",
                    userface:"",
                    address:"",
                    password:""

                },
                dialogVisible: false,
                passwdDialogVisible: false
            }
        },
        mounted(){
            this.user = this.current_user;
        },
        methods: {
            avatarUpload(param){
                const formData = new FormData();
                formData.append('file', param.file) ;// 要提交给后台的文件
                formData.append('identity', this.current_user.identity) ;// 这个接口必要的项目id
                formData.append('user_id', this.current_user.id); // 这个接口必要的其他的id
                this.postRequest("/user_avatar/",formData,true).then(resp=>{
                    if(resp){
                        this.initUser();
                    }
                });

            },
            updateUserInfo() {
                this.putRequest("/userinfo/", this.user).then(resp => {
                    if (resp) {
                        this.dialogVisible = false;
                        this.initUser();
                    }
                })
            },
            showUpdateUserInfoView() {
                this.dialogVisible = true;
            },

            submitForm(formName) {

                this.$refs[formName].validate((valid) => {
                    if (valid) {
                        this.user.password = this.ruleForm.pass;
                        this.putRequest("/userinfo/", this.user).then(resp => {
                            if (resp) {
                                this.getRequest("/logout/");
                                window.sessionStorage.removeItem("user");
                                this.$store.commit('initRoutes', []);
                                this.$router.replace("/");
                            }
                        })
                    } else {
                        return false;
                    }
                });
            },

            resetForm(formName) {
                this.$refs[formName].resetFields();
            },
            showUpdatePasswdView() {
                this.passwdDialogVisible = true;
            },

            initUser() {

                this.getRequest('/userinfo/?id='+this.current_user.id+"&identity="+this.current_user.identity).then(resp => {
                    if (resp) {
                        this.user = resp.data.data;
                        this.user.identity = this.current_user.identity;
                        window.sessionStorage.setItem("user", JSON.stringify(this.user));
                        this.$store.commit('init_currentUser', this.user);
                    }
                }
                );
            }
        },

        computed:{
            current_user(){
                return this.$store.state.currentHr;
            },
        }
    }
</script>

<style scoped>
    .info{
        margin-top: 5px;
    }

</style>