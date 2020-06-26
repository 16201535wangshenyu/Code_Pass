<template>
    <el-container>

        <el-header>
            <el-steps  :active="current_step"  simple  style="text-align: center;" >
                <el-step title="参数配置" icon="el-icon-setting"></el-step>
                <el-step title="上传文件" icon="el-icon-upload"></el-step>
                <el-step title="代码检测" icon="el-icon-circle-check"></el-step>
            </el-steps>
        </el-header>

        <el-main  >
            <el-row style="background-color: #E9EEF3; height: 100%; border-radius: 3px" type="flex" justify="center">
                <el-col :span="10" v-if="recordFormDisplay" style="padding-top: 100px">
                    <el-form :model="ruleForm" :rules="rules" ref="ruleForm"    label-width="100px" class="demo-ruleForm" >
                        <el-form-item label="检测标题" prop="name">
                            <el-input v-model="ruleForm.name"></el-input>
                        </el-form-item>
                        <el-form-item label="功能选择" prop="type">
                            <el-radio-group v-model="ruleForm.type" size="medium">
                                <el-radio border label="工程检测"></el-radio>
                                <el-radio border label="文件检测"></el-radio>
                            </el-radio-group>
                        </el-form-item>

                        <el-form-item label="检测类型" prop="region">
                            <el-select v-model="ruleForm.region" placeholder="请选择检测类型">
                                <el-option label="简单检测" value="1"></el-option>
                                <el-option label="普通检测" value="2"></el-option>
                                <el-option label="深度检测" value="3"></el-option>
                            </el-select>
                        </el-form-item>

                        <el-form-item label="记录备注" prop="desc">
                            <el-input type="textarea" v-model="ruleForm.desc"></el-input>
                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary" @click="submitForm('ruleForm')">下一步</el-button>
                            <el-button @click="resetForm('ruleForm')">重置</el-button>
                        </el-form-item>
                    </el-form>
                </el-col>
                <el-col :span="10" v-if="uploadFileDisplay" style="padding-top: 100px" v-loading="upload_loading"
                        element-loading-text="上传中...">
                    <el-row style="height: 60%;">
                        <el-upload
                                ref="upload"
                                class="upload-demo"
                                drag
                                :limit="1"
                                action="/code_pass/fileUpload/"
                                :on-success="uploadSuccess"
                                :on-error="uploadError"
                                :on-remove="handleFileRemove"
                                accept=".zip"
                                :on-exceed="handleExceed"
                                :auto-upload="false">
                            <i class="el-icon-upload"></i>
                            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
                            <div class="el-upload__tip" slot="tip">只能上传单个zip文件，且不超过500kb</div>
                        </el-upload>
                    </el-row>
                    <el-row>
                        <el-button type="primary" style="margin-top: 50px" @click="submitUploadFile">下一步</el-button>
                    </el-row>
                </el-col>
                <el-col :span="24" v-if="detectFolderDisplay" v-loading="detect_loading"
                        element-loading-text="检测中..." >
                    <el-row style="height: 100px" type="flex"  justify="center">
                        <el-col :span="3" style="margin-top: 30px">
                            <el-button :type="detect_button_status" :disabled="detect_button_disabled" :loading="detect_button_loading" v-text="detect_button_text" @click="start_detect(status)"></el-button>
                        </el-col>

                    </el-row>
                    <el-row>
                        <el-col :span="12">
                            <ve-pie :data="chartData1"></ve-pie>
                        </el-col>
                        <el-col :span="12">
                            <ve-pie :data="chartData2"></ve-pie>
                        </el-col>
                    </el-row>

                </el-col>
            </el-row>




        </el-main>

    </el-container>

</template>

<script>
    import {Message} from 'element-ui'
    export default {
        name: "detect_basic",
        data(){
            return{
                detect_record:{},
                detect_button_text:"开始检测",
                detect_button_status:"primary",
                detect_button_loading:false,
                detect_button_disabled:false,
                current_step:1,
                status:1,
                detect_loading:false,
                upload_loading:false,
                recordFormDisplay:true,
                uploadFileDisplay:false,
                detectFolderDisplay:false,
                ruleForm: {
                    name: '',
                    region: '',
                    type: '',
                    desc: ''
                },
                rules: {
                    name: [
                        { required: true, message: '请输入检测记录标题', trigger: 'blur' },
                        {  max: 30, message: '长度不超过30个字符', trigger: 'blur' }
                    ],
                    region: [
                        { required: true, message: '请选择检测类型', trigger: 'blur' }
                    ],
                    type: [
                        { required: true, message: '请进行功能选择', trigger: 'blur' }
                    ],
                    desc: [
                        { required: false, message: '请填写检测记录备注', trigger: 'blur' }
                    ]
                },
                record_id: 0,

                chartData1: {
                    columns: ['file_type', 'num'],
                    rows: [
                        { 'file_type': '正常文件', 'num': 0 },
                        { 'file_type': '异常文件', 'num': 0 },

                    ]
                },
                chartData2: {
                    columns: ['file_type', 'num'],
                    rows: [
                        { 'file_type': '正常文件', 'num': 0 },
                        { 'file_type': '轻度抄袭', 'num': 0 },
                        { 'file_type': '重度抄袭', 'num': 0 },
                        { 'file_type': '中度抄袭', 'num': 0 },




                    ]
                },

            }
        },
        methods: {
            submitForm(formName) {
                this.$refs[formName].validate((valid) => {
                    if (valid) {
                        Message.success("保存成功！");
                        this.set_current_step(2)
                    } else {
                        Message.success("填写错误！");
                        return false;
                    }
                });
            },
            resetForm(formName) {
                this.$refs[formName].resetFields();
            },

            // 上传文件个数超过定义的数量
            handleExceed (files, fileList) {
                Message.error({message: `当前限制选择 1 个文件，请删除后继续上传`});
            },
            //删除文件调用
            handleFileRemove(file, fileList){
                Message.success({message:file.name+' 删除成功！'})
            },
            //提交上传文件
            submitUploadFile(){
                this.$refs.upload.submit();
            },
            //文件上传成功调用
            uploadSuccess(response, file, fileList) {
                if(response.status === 500) {
                    Message.error(response.msg);
                    return;
                }

                Message.success({message:'上传成功！'});

                this.saveDetectRecord(response.file_id);


            },
            //文件上传失败调用
            uploadError(err, file, fileList){
                Message.error({message: `上传失败，请重新上传！`});

            },
            //保存检测记录
            saveDetectRecord(fileId){
                let _this  = this;
                let data = {
                    'name':_this.ruleForm.name,
                    'region':_this.ruleForm.region,
                    'type':_this.ruleForm.type,
                    'desc':_this.ruleForm.desc,
                    'fileid':fileId,
                    'user':{"id":this.current_user.id,"identity":this.current_user.identity}

                };

                this.postRequest('/saveDetectRecord/',data).then(resp => {
                    if (resp) {
                        this.record_id = resp.data.data.record_id ;
                        console.log(resp.data.data.record_id);
                        this.set_current_step(3);
                    }else{
                        Message.error("表单数据,请求失败!");
                    }
                });

            },
            //设置当前进行到哪一步
            set_current_step(step){
                this.current_step = step;
                this.recordFormDisplay = false;
                this.uploadFileDisplay = false;
                this.detectFolderDisplay = false;
                if(step === 1){
                    this.recordFormDisplay = true;

                }else if(step === 2){
                    this.uploadFileDisplay = true;

                }else if(step === 3){
                    this.detectFolderDisplay = true;
                }
            },
            //开始检测
            start_detect(status){
                // 开始检测
                if(status === 1) {
                    // this.detect_loading  = true;
                    this.detect_button_text = "检测中...";
                    this.detect_button_status = "warning";
                    this.detect_button_loading = true;
                    let record_id = this.record_id;
                    let data = {"record_id": record_id};
                    console.log("我执行了！");
                    this.postRequest("/start_detect/", data).then(resp => {
                        if (resp) {
                            this.detect_record = resp.data.data.record;
                            this.detect_button_loading = false;
                            this.detect_button_text = "再次检测";
                            this.detect_button_status = "success";
                            this.detect_button_disabled = false;
                            this.status = 2;
                            this.$store.commit('add_detect_record_to_detect_record_list', resp.data.data);
                            this.fill_data_to_graph();
                            console.log(resp)
                        } else {
                            Message.error("检测失败!");
                            this.detect_button_loading = false;
                            this.detect_button_text = "再次检测";
                            this.detect_button_status = "danger";
                            this.detect_button_disabled = false;
                        }
                    });
                    //再次检测
                }else if(status === 2){
                    //清空ruleForm
                    this.ruleForm = {
                            name: '',
                            region: '',
                            type: '',
                            desc: ''
                    };
                    //清空文件组件值
                    //this.$refs.upload.clearFiles();
                    //回到第一步
                    this.set_current_step(1);
                    this.detect_button_text = "开始检测";
                    this.detect_button_status = "primary";
                    this.status = 1;
                }

            },
            fill_data_to_graph(){
                //图一
                //正常文件个数
                this.chartData1['rows'][0]['num'] = this.detect_record['normal_file_num'];
                //异常文件个数
                this.chartData1['rows'][1]['num'] = this.detect_record['exception_file_num'];

                //图二
                //正常文件个数
                this.chartData2['rows'][0]['num'] = this.detect_record['normal_file_num'] - this.detect_record['mild_file_num'] - this.detect_record['moderate_file_num'] - this.detect_record['severe_file_num'];
                //轻度文件个数
                this.chartData2['rows'][1]['num'] = this.detect_record['mild_file_num'];
                //中度文件个数
                this.chartData2['rows'][3]['num'] = this.detect_record['moderate_file_num'];
                //重度文件个数
                this.chartData2['rows'][2]['num'] = this.detect_record['severe_file_num'];
                //图三
            }


        },
        computed: {
            current_user(){
                return this.$store.state.currentHr;
            },

        }
    }
</script>

<style scoped>
    .el-header, .el-footer {
        /*background-color: #B3C0D1;*/
        color: #E9EEF3;
        /*text-align: center;*/
        height: 60px;
    }
    .el-main {

        color: #333;


        height: 530px;
    }
    body > .el-container {
        margin-bottom: 40px;

    }

</style>