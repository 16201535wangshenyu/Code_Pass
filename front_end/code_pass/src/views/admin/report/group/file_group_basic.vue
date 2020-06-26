<template>
    <div >
        <div>
            <div style="display: flex;justify-content: space-between">
                <div>
                    <el-input placeholder="请输入文件组名进行搜索..." prefix-icon="el-icon-search"
                              clearable
                              style="width: 350px;margin-right: 10px" v-model="keyword">
                    </el-input>
                </div>
            </div>
        </div>
        <div style="margin-top: 15px">
            <el-table
                    :data="group_list.filter(data => !keyword || data.name.toLowerCase().includes(keyword.toLowerCase()))"
                    stripe
                    border
                    v-loading="loading"
                    element-loading-text="正在加载..."
                    element-loading-spinner="el-icon-loading"
                    element-loading-background="rgba(0, 0, 0, 0.8)"
                    style="width: 100%">
                <el-table-column
                        type="selection"
                        width="55">
                </el-table-column>
                <el-table-column
                        prop="name"
                        fixed
                        align="left"
                        label="名称"
                        width="150">
                </el-table-column>

                <el-table-column
                        prop="file_num"
                        width="150"
                        align="center"
                        sortable
                        label="总文件(个)">
                </el-table-column>
                <el-table-column
                        prop="normal_file_num"
                        width="150"
                        align="center"
                        sortable
                        label="正常文件(个)">
                </el-table-column>

                <el-table-column
                        prop="exception_file_num"
                        width="150"
                        align="center"
                        sortable
                        label="异常文件(个)">
                </el-table-column>
                <el-table-column
                        prop="mild_file_num"
                        width="150"
                        align="center"
                        sortable
                        label="轻度抄袭文件(个)">
                </el-table-column>
                <el-table-column
                        prop="moderate_file_num"
                        width="150"
                        sortable
                        align="center"
                        label="中度抄袭文件(个)">
                </el-table-column>
                <el-table-column
                        prop="severe_file_num"
                        width="150"
                        sortable
                        align="center"
                        label="重度抄袭文件(个)">
                </el-table-column>

                <el-table-column
                        fixed="right"
                        width="200"
                        label="操作">
                    <template slot-scope="scope">
                        <el-button style="padding: 3px" size="mini" type="primary" @click="searchFileList(scope.row)">查看文件列表</el-button>
                        <el-button @click="groupBasicStatistic(scope.row)" style="padding: 3px" size="mini" type="success">图表统计</el-button>
                    </template>
                </el-table-column>
            </el-table>
            <div style="display: flex;justify-content: flex-end">
                <el-pagination
                        background
                        @current-change="currentChange"
                        @size-change="sizeChange"
                        layout="sizes, prev, pager, next, jumper, ->, total, slot"
                        :total="total">
                </el-pagination>
            </div>
            <!--图表统计模块-->
            <el-dialog title="统计资料" :visible.sync="showBasicStatistic" stype="height:300px" width="60%">
                <!--<ve-pie :data="chartData1"></ve-pie>-->
                <!--<ve-pie :data="chartData2"></ve-pie>-->
                <el-row>
                    <el-col :span="12">
                        <ve-pie :data="chartData1"></ve-pie>
                    </el-col>
                    <el-col :span="12">
                        <ve-pie :data="chartData2"></ve-pie>
                    </el-col>

                </el-row>

            </el-dialog>
        </div>
    </div>
</template>

<script>
    export default {
        name: "file_group_basic",
        data(){
            return{
                group_list:[],
                keyword:'',
                size:10,
                page:1,
                total:0,
                loading:false,
                showBasicStatistic:false,
                chartData1: {
                    columns: ['func_type', 'num'],
                    rows: [
                        { 'func_type': '工程检测', 'num': 20 },
                        { 'func_type': '文件检测', 'num': 10 },

                    ]
                },
                chartData2: {
                    columns: ['degree', 'num'],
                    rows: [
                        { 'degree': '正常文件', 'num': 0 },
                        { 'degree': '轻度抄袭', 'num': 0 },
                        { 'degree': '重度抄袭', 'num': 0 },
                        { 'degree': '中度抄袭', 'num': 0 },

                    ]
                },
            }
        },
        methods:{
            requestGroupList(){
                this.loading = true;
                this.getRequest("/file_group_info/?page="+this.page+"&"+"size="+this.size+"&record_id="+this.record_id).then(resp=>{
                    if(resp){
                        this.total = resp.data.data['total'];
                        this.group_list = resp.data.data['file_group_list'];
                        this.loading = false;
                    }
                });
            },
            searchFileList(data){
                this.$store.commit('init_current_group_id',data['id']);
                this.$router.replace('/report/group/file/file_basic');

            },
            groupBasicStatistic(data){
                let normal_file_num = data['normal_file_num']==="undefined"?0:data['normal_file_num'];
                let exception_file_num = data['exception_file_num']==="undefined"?0:data['exception_file_num'];
                let mild_file_num = data['mild_file_num']==="undefined"?0:data['mild_file_num'];
                let moderate_file_num = data['moderate_file_num']==="undefined"?0:data['moderate_file_num'];
                let severe_file_num = data['severe_file_num']==="undefined"?0:data['severe_file_num'];
                console.log(moderate_file_num);
                console.log(severe_file_num);
                console.log(mild_file_num);
                console.log(normal_file_num);
                console.log(exception_file_num);
                //正常文件个数
                this.chartData1['rows'][0]['num'] = normal_file_num;
                //异常文件个数
                this.chartData1['rows'][1]['num'] = exception_file_num;
                //图二
                //正常文件个数
                this.chartData2['rows'][0]['num'] = normal_file_num - mild_file_num - moderate_file_num - severe_file_num;
                //轻度文件个数
                this.chartData2['rows'][1]['num'] = mild_file_num;
                //中度文件个数
                this.chartData2['rows'][3]['num'] = moderate_file_num;
                //重度文件个数
                this.chartData2['rows'][2]['num'] = severe_file_num;
                this.showBasicStatistic = true;

            },
            sizeChange(currentSize) {
                this.size = currentSize;
                this.requestGroupList();
            },
            currentChange(currentPage) {
                this.page = currentPage;
                this.requestGroupList();
            },
        },
        computed:{
            record_id(){
                return this.$store.state.current_record_id
            }
        },
        mounted(){
            this.requestGroupList();

        },
        // beforeRouteLeave(to, from, next){
        //     if(to.path == '/report/basic')
        //         this.$store.commit('set_report_component_display',true);
        //     // next();
        // },

    }
</script>

<style scoped>

</style>