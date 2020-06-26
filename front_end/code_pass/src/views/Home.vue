<template>
  <div>
    <el-container class="home-container">
            <el-header class="home-header">
              <span class="home_title">代码抄袭检测系统</span>
              <div style="display: flex;align-items: center;margin-right: 7px">

                <!--<el-button icon="el-icon-bell" type="text" style="margin-right: 8px;color: #000000;" size="normal" @click="goChat"></el-button>-->
                <el-badge style="margin-right: 30px" :is-dot="this.$store.state.nfDot">
                  <i class="fa fa-bell-o" @click="goChat" style="cursor: pointer"></i>
                </el-badge>

                   <el-dropdown @command="handleCommand">
                    <span class="el-dropdown-link home_userinfo" style="display: flex;align-items: center">
                      {{user.name}}
                      <i><img v-if="user.userface!=''" :src="user.userface"
                              style="width: 40px;height: 40px;margin-right: 5px;margin-left: 5px;border-radius: 40px"/></i>
                    </span>
                  <el-dropdown-menu slot="dropdown">
                    <el-dropdown-item command="userinfo">个人中心</el-dropdown-item>
                    <el-dropdown-item command="setting">设置</el-dropdown-item>
                    <el-dropdown-item command="logout" divided>注销</el-dropdown-item>
                  </el-dropdown-menu>
                </el-dropdown>

              </div>
            </el-header>



            <el-container>
              <el-aside width="180px" class="home-aside">
                <div style="display: flex;justify-content: flex-start;width: 180px;text-align: left;">
                  <el-menu style="background: #ececec;width: 180px;" unique-opened router>

                    <template v-for="(item,index) in this.routes" v-if="!item.hidden">
                      <el-submenu :key="index" :index="index+''">
                        <template slot="title">
                          <i :class="item.iconCls" style="color: #20a0ff;width: 14px;margin-right:6px"></i>
                          <span slot="title">{{item.name}}</span>
                        </template>
                        <el-menu-item width="180px"
                                      style="padding-left: 30px;padding-right:0px;margin-left: 0px;width: 170px;text-align: left"
                                      v-for="child in item.children"
                                      :index="child.path"
                                      :key="child.path">{{child.name}}
                        </el-menu-item>
                      </el-submenu>
                    </template>

                  </el-menu>
                </div>
              </el-aside>

                <!--<el-main>-->
                    <!--<el-breadcrumb separator-class="el-icon-arrow-right" v-if="this.$router.currentRoute.path!='/home'">-->
                        <!--<el-breadcrumb-item :to="{ path: '/home' }">首页</el-breadcrumb-item>-->
                        <!--<el-breadcrumb-item>{{this.$router.currentRoute.name}}</el-breadcrumb-item>-->
                    <!--</el-breadcrumb>-->
                    <!--<div class="homeWelcome" v-if="this.$router.currentRoute.path=='/home'">-->
                        <!--欢迎来到微人事！-->
                    <!--</div>-->

                    <!--<router-view class="homeRouterView"/>-->
                <!--</el-main>-->

                <el-main>
                      <el-breadcrumb separator-class="el-icon-arrow-right">
                        <el-breadcrumb-item :to="{ path: '/home'}" :replace="true">首页</el-breadcrumb-item>
                        <!--<el-breadcrumb-item v-text="this.$router.currentRoute.parent.parent.name"></el-breadcrumb-item>-->
                        <!--<el-breadcrumb-item v-text="this.$router.currentRoute.parent.name"></el-breadcrumb-item>-->

                          <el-breadcrumb-item v-if="this.$router.currentRoute.path ==='/report/group/file/file_basic'" :to="{ path: '/report/basic' }" :replace="true">基本资料</el-breadcrumb-item>
                          <el-breadcrumb-item  v-if="this.$router.currentRoute.path ==='/report/group/file/file_basic'" :to="{ path: '/report/group/file_group_basic' }" :replace="true">文件组资料</el-breadcrumb-item>

                          <el-breadcrumb-item  v-if="this.$router.currentRoute.path ==='/report/group/file_group_basic'" :to="{path:'/report/basic'}" :replace="true">基本资料</el-breadcrumb-item>

                          <el-breadcrumb-item v-text="this.$router.currentRoute.name"></el-breadcrumb-item>
                      </el-breadcrumb>

                    <div class="homeWelcome" v-if="this.$router.currentRoute.path==='/home'">
                        <el-carousel :interval="4000" type="card" height="200px">
                            <el-carousel-item v-for="item in 6" :key="item">
                                <!--<h3 class="medium">{{ item }}</h3>-->
                            </el-carousel-item>
                        </el-carousel>
                        <el-collapse  accordion>
                            <el-collapse-item   name="1">
                                <template slot="title">
                                    <i class="el-icon-notebook-2"></i><span style="margin-left: 5px">附件：代码抄袭检测系统-用户手册</span>
                                </template>
                                <div>
                                    <el-link href="/code_pass/notice_file_download/?file_id=1" icon="el-icon-notebook-2" style="margin-left: 10px">代码抄袭检测系统-用户手册</el-link>
                                </div>
                            </el-collapse-item>
                            <el-collapse-item  name="2">
                                <template slot="title">
                                    <i class="el-icon-notebook-2"></i><span style="margin-left: 5px">附件：代码抄袭检测系统-权限控制说明</span>
                                </template>
                                <div>
                                    <el-link href="/code_pass/notice_file_download/?file_id=2" icon="el-icon-notebook-2" style="margin-left: 10px">代码抄袭检测系统-权限控制说明</el-link>

                                </div>
                            </el-collapse-item>
                            <el-collapse-item  name="3">
                                <template slot="title">
                                    <i class="el-icon-notebook-2"></i><span style="margin-left: 5px">附件：代码抄袭检测系统-功能说明</span>
                                </template>
                                <div>
                                    <el-link href="/code_pass/notice_file_download/?file_id=3" icon="el-icon-notebook-2" style="margin-left: 10px">代码抄袭检测系统-功能说明</el-link>

                                </div>
                            </el-collapse-item>
                            <el-collapse-item  name="4">
                                <template slot="title">
                                    <i class="el-icon-notebook-2"></i><span style="margin-left: 5px">附件：代码抄袭检测系统-通知公告</span>
                                </template>
                                <div>
                                    <el-link href="/code_pass/notice_file_download/?file_id=4" icon="el-icon-notebook-2" style="margin-left: 10px">代码抄袭检测系统-通知公告</el-link>

                                </div>
                            </el-collapse-item>
                        </el-collapse>
                    </div>

                    <keep-alive >
                        <router-view class="homeRouterView" v-if="$route.meta.keepAlive"/>
                    </keep-alive>

                    <router-view class="homeRouterView" v-if="!$route.meta.keepAlive"/>


                </el-main>

            </el-container>
    </el-container>
  </div>
</template>
<script>
  export default {
      data(){
          return {
              isDot: false,

          }
      },


    mounted: function () {
      this.devMsg();
      console.log(this.$router)
      // this.loadNF();
    },

    methods: {
      loadNF(){
        let _this = this;
        // this.getRequest("/chat/sysmsgs").then(resp=> {
        //   var isDot = false;
        //   resp.data.forEach(msg=> {
        //     if (msg.state == 0) {
        //       isDot = true;
        //     }
        //   });
        //   _this.$store.commit('toggleNFDot', isDot);
        // })
      },
      goChat(){
        this.$router.push({path: '/chat'});
      },
      devMsg(){
        this.$alert('目前网站暂未搭建完善！！', '友情提示', {
          confirmButtonText: '确定',
        });
      },
      handleCommand(cmd){
        var _this = this;
        if (cmd === 'logout') {
          this.$confirm('注销登录, 是否继续?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            _this.getRequest("/logout");
              window.sessionStorage.removeItem("user");
              // this.$store.commit('initRoutes', []);
              this.$router.replace("/");
          }).catch(() => {
            _this.$message({
              type: 'info',
              message: '取消'
            });
          });
        }else if (cmd === 'userinfo') {
            this.$router.push('/personinfo');
        }
      }
    },

    computed: {
      user(){
        return this.$store.state.currentHr;

      },

      routes(){
          // let routess = [
          //     {
          //         "iconCls":"fa fa-user-circle-o",
          //         "name":"用户资料",
          //         "children":[
          //             {"name":"基本资料","path":"/teacher/basic"},
          //             {"name":"高级资料","path":"/teacher/adv"},
          //             ]
          //     },
          //     {
          //         "iconCls":"fa fa-cubes",
          //         "name":"代码检测",
          //         "children":[
          //             {"name":"代码检测","path":"/code_detect/basic"},
          //             {"name":"检测回馈","path":"/code_detect/feedback"},
          //         ]
          //     },
          //     {
          //         "iconCls":"fa fa-book",
          //         "name":"检测报告",
          //         "children":[
          //             {   "name":"基本资料","path":"/report/main",
          //                 // "children":{}
          //                 // "name":"基本资料","path":"/report/basic",
          //                 // "children":{"name":"文件组资料","path":""}
          //             },
          //
          //         ]
          //     },
          //     {
          //         "iconCls":"fa fa-windows",
          //         "name":"权限管理",
          //         "children":[
          //             {"name":"角色管理","path":"/auth/role"},
          //             {"name":"用户管理","path":"/auth/user"},
          //         ]
          //     },
          // ];

        // return routess
          console.log(this.$store.state.routes);
        return this.$store.state.routes
      }
    }
  }
</script>
<style>
    .homeRouterView {
        margin-top: 10px;
    }
    .homeWelcome {

        font-size: 30px;
        font-family: 华文行楷;
        color: #409eff;
        padding-top: 50px;
    }
  .home-container {
    height: 100%;
    position: absolute;
    top: 0px;
    left: 0px;
    width: 100%;
  }

  .home-header {
    background-color: #20a0ff;
    color: #333;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-sizing: content-box;
    padding: 0px;
  }

  .home-aside {
    background-color: #ECECEC;
  }

  .home-main {
    background-color: #fff;
    color: #000;

    margin: 0px;
    padding: 0px;;
  }

  .home_title {
    color: #fff;
    font-size: 22px;
    display: inline;
    margin-left: 8px;
  }

  .home_userinfo {
    color: #fff;
    cursor: pointer;
  }

  .home_userinfoContainer {
    display: inline;
    margin-right: 20px;
  }

  .el-submenu .el-menu-item {
    width: 180px;
    min-width: 175px;
  }
    .el-carousel__item h3 {
        color: #475669;
        font-size: 14px;
        opacity: 0.75;
        line-height: 200px;
        margin: 0;
    }

    .el-carousel__item:nth-child(2n) {
        background-color: #99a9bf;
    }

    .el-carousel__item:nth-child(2n+1) {
        background-color: #d3dce6;
    }
</style>
