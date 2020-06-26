import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter);

const routes = [
    {
        path: '/',
        name: 'Login',
        component: ()=> import(/* webpackChunkName: "about" */ '../views/Login')
    },
    {
        path: '/home',
        name: 'Home',
        component: ()=> import(/* webpackChunkName: "about" */ '../views/Home'),
        children: [
            // {
            //     path: '/chat',
            //     name: '在线聊天',
            //     component: FriendChat,
            //     hidden: true
            // },
            {
                path: '/personinfo',
                name: '个人中心',
                component: ()=> import(/* webpackChunkName: "about" */ '../views/admin/personal/personal'),
                hidden: true
            },
            // {
            //     path:"/teacher/basic",
            //     name:"基本资料",
            //     component:()=>import('../views/admin/teacher/teacher_basic'),
            //     hidden:true
            //
            // },
            // {
            //     path:"/teacher/adv",
            //     name:"高级资料",
            //     component:()=>import('../views/admin/teacher/teacher_adv'),
            //     hidden:true
            //
            // },
            // {
            //     path:"/code_detect/basic",
            //     name:"代码检测",
            //     component:()=>import('../views/admin/codedetection/detect_basic'),
            //     hidden:true
            //
            // },
            // {
            //     path:"/code_detect/result",
            //     name:"检测结果",
            //     component:()=>import('../views/admin/codedetection/detec_result'),
            //     hidden:true
            //
            // },
            // {
            //     path:"/code_detect/feedback",
            //     name:"检测回馈",
            //     component:()=>import('../views/admin/codedetection/detect_feedback'),
            //     hidden:true
            //
            // },
            {
                path:"/report/main",
                name:"基本资料",
                component:()=>import('../views/admin/report/report_main'),
                hidden:true,
                redirect: "/report/basic",
                children: [
                    {
                        path:"/report/group/file_group_basic",
                        name:"文件组资料",
                        component:()=>import('../views/admin/report/group/file_group_basic'),
                        hidden:true,
                    },
                    {
                      path:"/report/basic",
                      name:"基本资料",
                      component:()=>import('../views/admin/report/report_basic') ,
                      hidden:true,
                    },
                    {
                        path:"/report/group/file/file_basic",
                        name:"文件资料",
                        component:()=>import('../views/admin/report/group/file/file_basic'),
                        hidden:true,
                    }
                    ]

            },
            // {
            //     path:"/auth/role",
            //     name:"角色管理",
            //     component:()=>import('../views/admin/authority/auth_role'),
            //     hidden:true
            //
            // },
            // {
            //     path:"/auth/user",
            //     name:"用户管理",
            //     component:()=>import('../views/admin/authority/auth_user'),
            //     hidden:true
            //
            // },

        ]

    }
    // {
    //   path: '/about',
    //   name: 'About',
    //
    //   // component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
    // }
];

const router = new VueRouter({
    routes,
    mode:'history',
});

export default router