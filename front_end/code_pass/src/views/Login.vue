<template>
    <div>
        <el-form
                :rules="rules"
                ref="loginForm"
                v-loading="loading"
                element-loading-text="正在登录..."
                element-loading-spinner="el-icon-loading"
                element-loading-background="rgba(0, 0, 0, 0.8)"
                :model="loginForm"
                class="loginContainer">
            <h3 class="loginTitle">系统登录</h3>
            <el-form-item prop="username">
                <el-input size="normal" type="text" v-model="loginForm.username" auto-complete="off"
                          placeholder="请输入用户名"></el-input>
            </el-form-item>
            <el-form-item prop="password">
                <el-input size="normal" type="password" v-model="loginForm.password" auto-complete="off"
                          placeholder="请输入密码"></el-input>
            </el-form-item >
            <el-form-item prop="identity">
                <el-select size="normal" v-model="loginForm.identity" style="width: 200px" clearable placeholder="请选择身份">
                    <el-option label="管理员" value="admin"></el-option>
                    <el-option label="其他" value="others"></el-option>
                </el-select>
            </el-form-item>


            <el-form-item prop="code">
                <el-input size="normal" type="text" v-model="loginForm.code" auto-complete="off"
                          placeholder="点击图片更换验证码" @keydown.enter.native="submitLogin" style="width: 200px"></el-input>
                <img :src="vcUrl" @click="updateVerifyCode" alt="" style="cursor: pointer;width: 100px;height: 40px;margin-left: 50px">
            </el-form-item>
            <el-checkbox size="normal" class="loginRemember" v-model="checked">记住密码</el-checkbox>
            <el-button size="normal" type="primary" style="width: 100%;" @click="submitLogin">登录</el-button>
            <el-button type="text" @click="" style="margin-left: 150px;margin-top: 5px">忘记密码</el-button>
        </el-form>
    </div>
</template>

<script>

    export default {
        name: "Login",
        data() {
            return {
                loading: false,
                vcUrl: '/code_pass/verifyCode?a='+(new Date().valueOf()),
                loginForm: {
                    username: '16201535',
                    password: '123',
                    identity:'admin',
                    code:''
                },
                checked: true,
                rules: {
                    username: [{required: true, message: '请输入用户名', trigger: 'blur'}],
                    password: [{required: true, message: '请输入密码', trigger: 'blur'}],
                    identity: [{ required: true, message: '请选择身份', trigger: 'change' }],
                    code: [{required: true, message: '请输入验证码', trigger: 'blur'}]
                }
            }
        },

        methods: {
            updateVerifyCode() {
                this.vcUrl = '/code_pass/verifyCode?a='+(new Date().valueOf());
            },
            submitLogin() {
                this.$refs.loginForm.validate((valid) => {
                    if (valid) {
                        this.loading = true;
                        this.postRequest('/login/', this.loginForm).then(resp => {
                            this.loading = false;
                            if (resp) {

                                let user = resp.data.data;
                                console.log(user);
                                user.identity = this.loginForm.identity;
                                //
                                this.$store.commit('init_currentUser', user);
                                // //
                                window.sessionStorage.setItem("user", JSON.stringify(user));
                                let path = this.$route.query.redirect;
                                this.$router.replace((path == '/' || path == undefined) ? '/home' : path);
                            }else{
                                // this.getIdentifyCode()
                                this.vcUrl = '/code_pass/verifyCode?a='+(new Date().valueOf())
                            }
                        })
                    } else {
                        return false;
                    }

                });
            },
            /**
             * 是否刷新，获取验证码图片
             */
            // getIdentifyCode: function() {
            //     console.log("进来了！")
            //         // , "arraybuffer"
            //     this.getRequest("/verifyCode").then(response => {
            //         console.log("进来了！！")
            //         console.log(response)
            //         return 'data:image/png;base64,' + btoa(
            //             new Uint8Array(response.data).reduce((data, byte) => data + String.fromCharCode(byte), '')
            //         );
            //     }).then(data => {
            //         this.vcUrl = data;
            //     }).catch(ex => {
            //         console.log(ex);
            //     })
            // },
        },
        // created(){
        //     this.getIdentifyCode()
        //
        // },

    }
</script>

<style>
    .loginContainer {
        border-radius: 15px;
        background-clip: padding-box;
        margin: 180px auto;
        width: 350px;
        padding: 15px 35px 15px 35px;
        background: #fff;
        border: 1px solid #eaeaea;
        box-shadow: 0 0 25px #cac6c6;
    }

    .loginTitle {
        margin: 15px auto 20px auto;
        text-align: center;
        color: #505458;
    }

    .loginRemember {
        text-align: left;
        margin: 0px 0px 15px 0px;
    }
    .el-form-item__content{
        display: flex;
        align-items: center;
    }
</style>
