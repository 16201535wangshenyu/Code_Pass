<template>
    <div>
        <el-tabs v-model="activeName" type="card">
            <el-tab-pane label="权限组" name="permissmana"><PermissMana></PermissMana></el-tab-pane>
        </el-tabs>
    </div>
</template>

<script>
    import PermissMana from '../../../components/content/authority/PermissMana'
    export default {

        data(){
            return{
                activeName: 'permissmana'
            }
        },
        components:{
            PermissMana
        }

    }
</script>

<style scoped>

</style>