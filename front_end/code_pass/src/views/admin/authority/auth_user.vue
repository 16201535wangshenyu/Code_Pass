<template>
    <div style="margin-top: 10px" v-loading="fullloading">
        <div style="margin-bottom: 10px;display: flex;justify-content: center;align-items: center">
            <el-input
                    placeholder="默认展示部分用户，可以通过用户名搜索更多用户..."
                    prefix-icon="el-icon-search"
                    size="small"
                    style="width: 400px;margin-right: 10px"
                    v-model="keywords">
            </el-input>
            <el-button size="small" type="primary" icon="el-icon-search" @click="searchClick">搜索</el-button>
        </div>
        <div style="display: flex;justify-content: space-around;flex-wrap: wrap;text-align: left">
            <el-card style="width: 300px;height:300px;margin-bottom: 20px" v-for="(item,index) in users" :key="item.id"
                     v-loading="cardLoading[index]">
                <div slot="header" class="clearfix">
                    <span>{{item.name}}</span>
                    <el-button type="text"
                               style="color: #f6061b;margin: 0px;float: right; padding: 3px 0;width: 15px;height:15px"
                               icon="el-icon-delete" @click="deleteHr(item.id)"></el-button>
                </div>
                <div>
                    <div style="width: 100%;display: flex;justify-content: center">
                        <img :src="item.userface" alt="item.name" style="width: 70px;height: 70px;border-radius: 70px">
                    </div>
                    <div style="margin-top: 20px">
                        <div><span class="user-info">工号:{{item.username}}</span></div>
                        <div><span class="user-info">用户名:{{item.name}}</span></div>
                        <div><span class="user-info">手机号码:{{item.phone}}</span></div>
                        <div><span class="user-info">地址:{{item.address}}</span></div>
                        <div class="user-info" style="display: flex;align-items: center;margin-bottom: 3px">
                            用户状态:
                            <!--!item.disabled-->
                            <el-switch
                                    style="display: inline;margin-left: 5px"
                                    :value="!item.disabled"
                                    active-color="#13ce66"
                                    active-text="启用"
                                    inactive-color="#aaaaaa"
                                    inactive-text="禁用"
                                    @change="switchChange(!item.disabled,item.id,index)"
                            >
                            </el-switch>
                        </div>
                        <div class="user-info">
                            用户角色:
                            <el-tag
                                    v-for="role in item.role_list"
                                    :key="role.id"
                                    type="success"
                                    size="mini"
                                    style="margin-right: 5px"
                                    :disable-transitions="false">{{role.nameZh}}
                            </el-tag>

                            <el-popover
                                    v-loading="eploading[index]"
                                    placement="right"
                                    title="角色列表"
                                    width="200"
                                    @hide="updateUserRoles(item.id,index)"

                                    trigger="click">
                                <el-select v-model="selRoles" multiple placeholder="请选择角色">
                                    <el-option
                                            v-for="ar in allRoles"
                                            :key="ar.id"
                                            :label="ar.nameZh"
                                            :value="ar.id">
                                    </el-option>
                                </el-select>
                                <el-button type="text" icon="el-icon-more" style="color: #09c0f6;padding-top: 0px" slot="reference"
                                           @click="loadSelRoles(item.role_list,index)" :disabled="moreBtnState"></el-button>
                                <!--                <i class="el-icon-more" style="color: #09c0f6;cursor: pointer" slot="reference"
                                                   @click="loadSelRoles(item.roles,index)" disabled="true"></i>-->
                            </el-popover>

                        </div>
                        <div><span class="user-info">备注:{{item.remark}}</span></div>
                    </div>
                </div>
            </el-card>
        </div>
    </div>
</template>

<script>
    export default {
        data(){
            return {
                keywords: '',
                fullloading: false,
                users: [],
                cardLoading: [],
                eploading: [],
                allRoles: [],
                moreBtnState:false,
                selRoles: [],
                selRolesBak: []
            }
        },
        mounted: function () {
            this.initCards();
            this.loadAllRoles();
        },
        methods: {
            searchClick(){
                this.initCards();
                this.loadAllRoles();
            },
            updateUserRoles(userId, index){
                this.moreBtnState = false;
                let _this = this;
                if (this.selRolesBak.length === this.selRoles.length) {
                    for (let i = 0; i < this.selRoles.length; i++) {
                        for (let j = 0; j < this.selRolesBak.length; j++) {
                            if (this.selRoles[i] === this.selRolesBak[j]) {
                                this.selRolesBak.splice(j, 1);
                                break;
                            }
                        }
                    }
                    if (this.selRolesBak.length === 0) {
                        return;
                    }
                }
                this.eploading.splice(index, 1, true);
                // console.log("修改用户角色数据");
                // console.log(userId);
                // console.log(this.selRoles);
                console.log(this.selRoles);
                this.putRequest("/user_role_info/", {
                    "user_id": userId,
                    "role_ids": this.selRoles
                }).then(resp=> {
                    _this.eploading.splice(index, 1, false);
                    if (resp ) {
                        _this.refreshHr(userId, index);
                    }
                });
            },
            refreshHr(hrId, index){
                let _this = this;
                _this.cardLoading.splice(index, 1, true);
                this.getRequest("/user_info_by_id/?user_id=" + hrId).then(resp=> {
                    _this.cardLoading.splice(index, 1, false);
                    _this.users.splice(index, 1, resp.data.data);
                })
            },
            loadSelRoles(userRoles, index){
                this.moreBtnState = true;
                this.selRoles = [];
                this.selRolesBak = [];
                userRoles.forEach(role=> {
                    this.selRoles.push(role.id);
                    this.selRolesBak.push(role.id)
                })
            },
            loadAllRoles(){
                let _this = this;
                this.getRequest("/role_info/?user_id="+this.current_user.id+"&"+"identity="+this.current_user.identity).then(resp=> {
                    _this.fullloading = false;
                    if (resp) {
                        console.log("加载的所有的角色");
                        console.log(resp.data);
                        _this.allRoles = resp.data.data;
                    }
                })
            },
            switchChange(newValue, hrId, index){
                let _this = this;
                _this.cardLoading.splice(index, 1, true);
                this.putRequest("/disabled_user/", {
                    "disabled": newValue,
                    "user_id": hrId,
                }).then(resp=> {
                    _this.cardLoading.splice(index, 1, false);
                    if (resp ) {
                        _this.refreshHr(hrId, index);
                    }
                })
            },
            initCards(){
                this.fullloading = true;
                let _this = this;
                let searchWords = this.keywords;
                // if (this.keywords === '') {
                //     searchWords = 'all';
                // } else {
                //     searchWords = this.keywords;
                // }

                this.getRequest("/userinfo/?page="+1+"&"+"size="+8+"&user_id="+this.current_user.id+"&"+"identity="+this.current_user.identity+"&"+"name="+searchWords).then(resp =>{
                    if (resp) {
                        _this.users = resp.data.data['user_list'];
                        console.log(_this.users);

                        let length = resp.data.data.length;
                        _this.cardLoading = Array.apply(null, Array(length)).map(function (item, i) {
                            return false;
                        });
                        _this.eploading = Array.apply(null, Array(length)).map(function (item, i) {
                            return false;
                        });
                    }
                })
            },
            deleteHr(hrId){
                let _this = this;
                this.fullloading = true;

                this.deleteRequest("/userinfo/?ids=" + hrId).then(resp=> {
                    _this.fullloading = false;
                    if (resp ) {
                        _this.initCards();
                        _this.loadAllRoles();

                    }
                })
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
    .user-info {
        font-size: 12px;
        color: #09c0f6;
    }

</style>