<template>
    <div>
        <div>
            <div style="display: flex;justify-content: space-between">
                <div>
                    <el-input placeholder="请输入用户名进行搜索，可以直接回车搜索..." prefix-icon="el-icon-search"
                              clearable
                              @clear="initUsers"
                              style="width: 350px;margin-right: 10px" v-model="keyword"
                              @keydown.enter.native="initUsers" >
                    </el-input>

                    <el-button icon="el-icon-search" type="primary" @click="initUsers">
                        搜索
                    </el-button>

                </div>
                <div>
                    <el-upload
                            :show-file-list="false"
                            :before-upload="beforeUpload"
                            :on-success="onSuccess"
                            :on-error="onError"
                            :disabled="importDataDisabled"
                            style="display: inline-flex;margin-right: 8px"
                            action="string"
                            :http-request="uploadExcel"
                    >
                        <el-button :disabled="importDataDisabled" type="success" :icon="importDataBtnIcon">
                            {{importDataBtnText}}
                        </el-button>
                    </el-upload>
                    <el-button type="success" @click="exportData" icon="el-icon-download">
                        导出数据
                    </el-button>
                    <el-button type="primary" icon="el-icon-plus" @click="showAddEmpView">
                        添加用户
                    </el-button>
                </div>
            </div>

        </div>
        <div style="margin-top: 10px">
            <el-table
                    :data="users"
                    stripe
                    border
                    v-loading="loading"
                    @selection-change="handleSelectionChange"
                    element-loading-text="正在加载..."
                    element-loading-spinner="el-icon-loading"
                    element-loading-background="rgba(0, 0, 0, 0.8)"
                    style="width: 100%">
                <el-table-column
                        type="selection"
                        width="55">
                </el-table-column>
                <el-table-column
                        prop="username"
                        fixed
                        align="left"
                        label="工号"
                        width="100">
                </el-table-column>
                <el-table-column
                        prop="name"
                        label="姓名"
                        align="left"
                        width="100">
                </el-table-column>
                <el-table-column
                        prop="telephone"
                        label="座机号码"
                        align="left"
                        width="150">
                </el-table-column>

                <el-table-column
                        prop="phone"
                        width="150"
                        align="left"
                        label="手机号码">
                </el-table-column>

                <el-table-column
                        prop="address"
                        width="360"
                        label="联系地址">
                </el-table-column>

                <el-table-column
                        prop="remark"
                        width="300"
                        label="备注">
                </el-table-column>

                <el-table-column
                        fixed="right"
                        width="200"
                        label="操作">
                    <template slot-scope="scope">
                        <el-button @click="showEditUserView(scope.row)" style="padding: 3px" size="mini">编辑</el-button>
                        <el-button style="padding: 3px" size="mini" type="primary" :disabled="true">查看高级资料</el-button>
                        <el-button @click="deleteEmp(scope.row)" style="padding: 3px" size="mini" type="danger">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>
            <el-button type="danger" size="mini" v-if="users.length>0" :disabled="multipleSelection.length===0"
                       @click="deleteManyUsers">批量删除
            </el-button>
            <div style="display: flex;justify-content: flex-end">

                <el-pagination
                        background
                        @current-change="currentChange"
                        @size-change="sizeChange"
                        layout="sizes, prev, pager, next, jumper, ->, total, slot"
                        :total="total">
                </el-pagination>
            </div>
        </div>
        <el-dialog
                :title="title"
                :visible.sync="dialogVisible"
                width="80%">
            <div>
                <el-form :model="person" :rules="rules" ref="empForm">
                    <el-row>
                        <el-col :span="6">
                            <el-form-item label="工号:" prop="username">
                                <el-input size="mini" style="width: 150px" prefix-icon="el-icon-edit" v-model="person.username"
                                          :disabled="true"
                                          placeholder="请输入用户工号"></el-input>
                            </el-form-item>
                        </el-col>
                        <el-col :span="6">
                            <el-form-item label="姓名:" prop="name">
                                <el-input size="mini" style="width: 150px" prefix-icon="el-icon-edit" v-model="person.name"
                                          placeholder="请输入用户姓名"></el-input>
                            </el-form-item>
                        </el-col>
                        <el-col :span="6">
                            <el-form-item label="座机号码:" prop="telephone">
                                <el-input size="mini" style="width: 200px" prefix-icon="el-icon-phone"
                                          v-model="person.telephone" placeholder="电话号码"></el-input>
                            </el-form-item>
                        </el-col>
                        <el-col :span="6">
                            <el-form-item label="手机号码:" prop="phone">
                                <el-input size="mini" style="width: 200px" prefix-icon="el-icon-phone"
                                          v-model="person.phone" placeholder="电话号码"></el-input>
                            </el-form-item>
                        </el-col>
                    </el-row>
                    <el-row>
                        <el-col :span="6">
                            <el-form-item label="联系地址:" prop="address">
                                <el-input size="mini" style="width: 200px" prefix-icon="el-icon-edit"
                                          v-model="person.address" placeholder="请输入联系地址"></el-input>
                            </el-form-item>
                        </el-col>
                        <el-col :span="6">
                            <el-form-item label="用户头像:" prop="userface">
                                <el-input size="mini" style="width: 200px" prefix-icon="el-icon-edit"

                                          v-model="person.userface" placeholder="请输入用户头像地址"></el-input>
                            </el-form-item>
                        </el-col>
                        <el-col :span="6">
                            <el-form-item label="密码:" prop="password">
                                <el-input size="mini" style="width: 200px" prefix-icon="el-icon-edit"
                                          v-model="person.password" placeholder="请输入用户初始密码"></el-input>
                            </el-form-item>
                        </el-col>
                        <el-col :span="6">
                            <el-form-item label="备注:" prop="remark">
                                <el-input size="mini" style="width: 200px" prefix-icon="el-icon-edit"
                                          v-model="person.remark" placeholder="请输入备注信息"></el-input>
                            </el-form-item>
                        </el-col>

                    </el-row>

                </el-form>
            </div>
            <span slot="footer" class="dialog-footer">
                <el-button @click="dialogVisible = false">取 消</el-button>
                <el-button type="primary" @click="doAddEmp">确 定</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
    export default {
        name: "teacher_adv",
        data(){
            return{
                searchValue: {
                    politicId: null,
                    nationId: null,
                    jobLevelId: null,
                    posId: null,
                    engageForm: null,
                    departmentId: null,
                    beginDateScope: null
                },
                title: '',
                importDataBtnText: '导入数据',
                importDataBtnIcon: 'el-icon-upload2',
                importDataDisabled: false,
                showAdvanceSearchView: false,
                users: [],
                loading: false,
                popVisible: false,
                popVisible2: false,
                dialogVisible: false,
                total: 0,
                page: 1,
                keyword: '',
                size: 10,
                multipleSelection:[],
                person: {
                    username:"",
                    name: "",
                    telephone:"",
                    phone:"",
                    address:"",
                    userface:"",
                    password:"",
                    remark:""
                },
                defaultProps: {
                    children: 'children',
                    label: 'name'
                },
                rules: {
                    username: [{required: true, message: '请输入工号', trigger: 'blur'}],
                    name: [{required: true, message: '请输入用户名', trigger: 'blur'}],
                    phone: [{required: true, message: '请输入手机号码', trigger: 'blur'}],
                    telephone: [{required: true, message: '请输入手机号码', trigger: 'blur'}],
                    address: [{required: true, message: '请输入用户地址', trigger: 'blur'}],
                    userface: [{required: true, message: '请输入用户头像接口', trigger: 'blur'}],
                    remark: [{required: false, message: '请输入用户备注', trigger: 'blur'}],
                    password: [{required: true, message: '请输入用户初始密码', trigger: 'blur'}],
                }
            }
        },
        mounted() {
            this.initUsers();
            // this.initEmps();
            // this.initData();
            // this.initPositions();
        },
        methods:{
            handleSelectionChange(val) {
                console.log(val);
                this.multipleSelection = val;
            },
            deleteManyUsers(){
                this.$confirm('此操作将删除[' + this.multipleSelection.length + ']条数据, 是否继续?', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    let ids = '';
                    for (let i = 0; i < this.multipleSelection.length; i++) {
                        ids += this.multipleSelection[i].id + ",";
                    }
                    this.doDelete(ids);
                }).catch(() => {
                });

            },
            onError(err, file, fileList) {
                this.importDataBtnText = '导入数据';
                this.importDataBtnIcon = 'el-icon-upload2';
                this.importDataDisabled = false;
            },
            onSuccess(response, file, fileList) {
                this.importDataBtnText = '导入数据';
                this.importDataBtnIcon = 'el-icon-upload2';
                this.importDataDisabled = false;
                console.log("导入成功！")
                // this.initUsers();
            },
            beforeUpload() {
                this.importDataBtnText = '正在导入';
                this.importDataBtnIcon = 'el-icon-loading';
                this.importDataDisabled = true;
            },
            //上传文件
            uploadExcel(param){
                const formData = new FormData();
                formData.append('file', param.file) ;// 要提交给后台的文件
                formData.append('identity', this.current_user.identity) ;// 这个接口必要的项目id
                formData.append('user_id', this.current_user.id); // 这个接口必要的其他的id
                this.postRequest("/user_info_upload/",formData,true).then(resp=>{
                    if(resp){
                        this.importDataBtnText = '导入数据';
                        this.importDataBtnIcon = 'el-icon-upload2';
                        this.importDataDisabled = false;
                        this.initUsers();
                    }
                });
            },

            exportData() {
                window.open('/code_pass/user_info_download/?identity='+this.current_user.identity+"&creator_id="+this.current_user.id, '_parent');
                // this.getRequest("/user_info_download/?identity="+this.current_user.identity+"&creator_id="+this.current_user.id);
            },
            showEditUserView(data) {
                this.title = '编辑员工信息';
                this.person = data;
                this.dialogVisible = true;
            },

            deleteEmp(data) {
                this.$confirm('此操作将永久删除【' + data.name + '】, 是否继续?', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.doDelete(data.id+"");
                }).catch(() => {
                    this.$message({
                        type: 'info',
                        message: '已取消删除'
                    });
                });
            },
            doDelete(ids){

                this.deleteRequest("/userinfo/?ids=" + ids).then(resp => {
                    if (resp) {
                        this.initUsers();
                    }
                })

            },

            doAddEmp() {
                if (this.person.id) {
                    //修改用户信息
                    this.$refs['empForm'].validate(valid => {
                        if (valid) {

                            let person = {
                                "id":this.person.id,
                                "username":this.person.username,
                                "name": this.person.name,
                                "telephone":this.person.telephone,
                                "phone":this.person.phone,
                                "address":this.person.address,
                                "userface":this.person.userface,
                                "password":this.person.password,
                                "remark":this.person.remark
                            };


                            this.putRequest("/userinfo/", person).then(resp => {
                                if (resp) {
                                    this.dialogVisible = false;
                                    this.initUsers();
                                }
                            })
                        }
                    });
                } else {
                    //增加用户信息
                    this.$refs['empForm'].validate(valid => {
                        if (valid) {
                            let data = {
                                "creator_id":this.current_user.id,
                                "identity":this.current_user.identity,
                                "username":this.person.username,
                                "name": this.person.name,
                                "telephone":this.person.telephone,
                                "phone":this.person.phone,
                                "address":this.person.address,
                                "userface":this.person.userface,
                                "password":this.person.password,
                                "remark":this.person.remark
                            };
                            console.log("增加用户信息");
                            this.postRequest("/userinfo/", data).then(resp => {
                                if (resp) {
                                    this.dialogVisible = false;
                                    this.initUsers();
                                }
                            })
                        }
                    });
                }
            },
            showAddEmpView() {
                this.emptyUser();
                this.title = '添加用户';
                this.getMaxWordID();
                this.dialogVisible = true;

            },

            getMaxWordID() {
                this.getRequest("/get_max_work_id/").then(resp => {
                    if (resp) {
                        this.person.username = resp.data['max_work_id'];
                    }
                })
            },
            sizeChange(currentSize) {
                this.size = currentSize;
                this.initUsers();
            },
            currentChange(currentPage) {
                this.page = currentPage;
                this.initUsers();
            },

            initUsers(){
                this.loading = true;
                this.getRequest("/userinfo/?page="+this.page+"&"+"size="+this.size+"&user_id="+this.current_user.id+"&"+"identity="+this.current_user.identity+"&"+"name="+this.keyword).then(resp =>{

                        if(resp){
                            this.total = resp.data.data['total'];
                            this.users = resp.data.data['user_list'];
                            this.loading = false;
                        }
                    }

                );
            },
            emptyUser(){
                this.person = {
                    username: "",
                    name: "",
                    telephone: "",
                    phone: "",
                    address: "",
                    userface: "",
                    remark: ""
                };
            }
        },
        computed:{
            current_user(){
                return this.$store.state.currentHr;
            }
        }
    }
</script>

<style scoped>

</style>