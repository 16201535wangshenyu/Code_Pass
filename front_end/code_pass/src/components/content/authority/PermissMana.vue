<template>
    <div
            v-loading="globalLoading"
            element-loading-text="正在添加..."
            element-loading-spinner="el-icon-loading"
            element-loading-background="rgba(0, 0, 0, 0.8)"
    >
        <div class="permissManaTool">
            <el-input size="small" placeholder="请输入角色英文名" v-model="role.name">
                <template slot="prepend">ROLE_</template>
            </el-input>
            <el-input size="small" placeholder="请输入角色中文名" v-model="role.nameZh"
                      @keydown.enter.native="doAddRole">

            </el-input>
            <el-button type="primary" size="small" icon="el-icon-plus" @click="doAddRole">添加角色</el-button>
        </div>
        <div class="permissManaMain">
            <el-collapse v-model="activeName"
                         v-loading="loading"
                         element-loading-text="正在加载..."
                         element-loading-spinner="el-icon-loading"
                         element-loading-background="rgba(0, 0, 0, 0.8)"
                         accordion
                         @change="change">
                <el-collapse-item :title="r.nameZh" :name="r.id" v-for="(r,index) in roles" :key="index">
                    <el-card class="box-card">
                        <div slot="header" class="clearfix">
                            <span>可访问的资源</span>
                            <el-button style="float: right; padding: 3px 0;color: #ff0000;" icon="el-icon-delete"
                                       type="text" @click="deleteRole(r)">

                            </el-button>
                        </div>
                        <div>
                            <el-tree
                                    show-checkbox
                                    node-key="id"
                                    ref="tree"
                                    :key="index"
                                    :default-checked-keys="selectedMenus"
                                    :data="allmenus" :props="defaultProps">

                            </el-tree>
                            <div style="display: flex;justify-content: flex-end">
                                <el-button @click="cancelUpdate">取消修改</el-button>
                                <el-button type="primary" @click="doUpdate(r.id,index)">确认修改</el-button>
                            </div>
                        </div>
                    </el-card>
                </el-collapse-item>
            </el-collapse>
        </div>
    </div>
</template>

<script>
    import {Message} from 'element-ui'
    export default {
        name: "PermissMana",
        data() {
            return {
                role: {
                    name: '',
                    nameZh: ''
                },
                allmenus: [],
                activeName: -1,
                selectedMenus: [],
                roles: [],
                loading: false,
                globalLoading: false,
                // data: [{
                //     id: 1,
                //     label: '一级 1',
                //     children: [{
                //         id: 4,
                //         label: '二级 1-1',
                //         children: [{
                //             id: 9,
                //             label: '三级 1-1-1'
                //         }, {
                //             id: 10,
                //             label: '三级 1-1-2'
                //         }]
                //     }]
                // },
                //     {
                //     id: 2,
                //     label: '一级 2',
                //     children: [{
                //         id: 5,
                //         label: '二级 2-1'
                //     }, {
                //         id: 6,
                //         label: '二级 2-2'
                //     }]
                // },
                //     {
                //     id: 3,
                //     label: '一级 3',
                //     children: [{
                //         id: 7,
                //         label: '二级 3-1'
                //     }, {
                //         id: 8,
                //         label: '二级 3-2'
                //     }]
                // }],
                defaultProps: {
                    children: 'children',
                    label: 'name'
                }
            }
        },
        mounted() {
            this.initRoles();
        },
        methods: {
            deleteRole(role) {
                this.$confirm('此操作将永久删除【' + role.nameZh + '】角色, 是否继续?', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.deleteRequest("/role_info/?role_id=" + role.id).then(resp => {
                        if (resp) {
                            this.initRoles();
                        }
                    })
                }).catch(() => {
                    this.$message({
                        type: 'info',
                        message: '已取消删除'
                    });
                });
            },
            doAddRole() {
                if (this.role.name && this.role.nameZh) {
                    this.globalLoading = true;
                    let data = {
                        "user_id":this.current_user.id,
                        "identity":this.current_user.identity,
                        "name":this.role.name,
                        "nameZh":this.role.nameZh
                    };
                    this.postRequest("/role_info/", data).then(resp => {
                        this.globalLoading = false;
                            if (resp) {
                                this.role.name = '';
                                this.role.nameZh = '';
                                this.initRoles();

                            }
                    });
                } else {
                    Message.error('数据不可以为空');
                }
            },

            cancelUpdate() {
                this.activeName = -1;
            },
            doUpdate(rid, index) {
                let tree = this.$refs.tree[index];
                let selectedKeys = tree.getCheckedKeys(true);
                let url = '/role_info/';
                let data={
                    "mids":selectedKeys,
                    "role_id":rid
                };
                // let url = '/role_info/?role_id=' + rid;
                // selectedKeys.forEach(key => {
                //     url += '&mids=' + key;
                // });
                this.putRequest(url,data).then(resp => {
                    if (resp) {
                        this.activeName = -1;
                    }
                })
            },

            change(rid) {
                if (rid) {
                    this.initAllMenus();
                    this.initSelectedMenus(rid);
                }
            },

            initSelectedMenus(rid) {
                this.getRequest("/get_menu_id_set_by_role/?role_id=" + rid).then(resp => {
                    if (resp) {
                        let data = JSON.parse(resp.data.data);
                        this.selectedMenus = data['menu_id_set'];
                    }
                })
            },
            initAllMenus() {
                this.getRequest("/menus_info/?user_id="+this.current_user.id+"&"+"identity="+this.current_user.identity).then(resp => {
                    if (resp) {
                        this.allmenus = resp.data.data;
                    }
                })
            },
            initRoles() {
                this.loading = true;
                this.getRequest("/role_info/?user_id="+this.current_user.id+"&"+"identity="+this.current_user.identity).then(resp => {
                    this.loading = false;
                    if (resp) {
                        this.roles = resp.data.data;
                    }
                })
            },
        },
        computed:{
            current_user(){
                return this.$store.state.currentHr;
            }
        }
    }
</script>

<style>
    .permissManaTool {
        display: flex;
        justify-content: flex-start;
    }

    .permissManaTool .el-input {
        width: 300px;
        margin-right: 6px;
    }

    .permissManaMain {
        margin-top: 10px;
        width: 700px;
    }
</style>