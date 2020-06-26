<template>
    <div >
        <div >
            <div>
                <div style="display: flex;justify-content: space-between">
                    <div>
                        <el-input placeholder="请输入检测记录标题进行搜索..." prefix-icon="el-icon-search"
                                  clearable
                                  style="width: 350px;margin-right: 10px" v-model="keyword">
                        </el-input>
                    </div>
                    <div>
                        <el-button type="primary" icon="el-icon-star-off" @click="detect_basic_statistic">
                            图表统计
                        </el-button>
                    </div>
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

            <div style="margin-top: 15px">


                <el-table
                        :data="record_list.filter(data => !keyword || data.title.toLowerCase().includes(keyword.toLowerCase()))"
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
                            prop="title"
                            fixed
                            align="left"
                            label="标题"
                            width="85">
                    </el-table-column>
                    <el-table-column
                            prop="func_type"
                            label="功能类型"
                            align="left"
                            width="90"
                            :filters="[{ text: '工程检测', value: '工程检测' }, { text: '文件检测', value: '文件检测' }]"
                            :filter-method="filter_func_type_Tag"
                            filter-placement="bottom-end"
                    >
                        <template slot-scope="scope">
                            <el-tag
                                    :type="scope.row.func_type === '工程检测' ? 'primary' : 'warning'"
                                    disable-transitions>{{scope.row.func_type}}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column
                            prop="degree"
                            label="检测程度"

                            align="left"
                            width="90"
                            :filters="[{ text: '简单检测', value: '1' }, { text: '普通检测', value: '2' },{ text: '深度检测', value: '3' }]"
                            :filter-method="filter_degree_Tag"
                            filter-placement="bottom-end"
                    >
                        <template slot-scope="scope">
                            <el-tag
                                    :type="tag_type(scope.row.degree)"
                                    disable-transitions>{{tag_text(scope.row.degree)}}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column
                            prop="start_time"
                            width="150"
                            align="center"
                            sortable
                            column-key="start_time"
                            :filters="date_filters"
                            :filter-method="filterHandler"
                            label="开始时间">
                        <template slot-scope="scope">
                            <span>{{ scope.row.start_time | FormatDate('yyyy-MM-dd hh:mm:ss') }}</span>
                        </template>
                    </el-table-column>

                    <el-table-column

                            width="150"
                            align="center"
                            label="结束时间">
                        <template slot-scope="scope">
                            <span>{{ scope.row.end_time | FormatDate('yyyy-MM-dd hh:mm:ss') }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                            prop="detect_time"
                            width="70"
                            label="检测时长">
                    </el-table-column>
                    <el-table-column
                            prop="file_num"
                            width="60"
                            label="总文件">
                    </el-table-column>
                    <el-table-column
                            prop="normal_file_num"
                            width="80"
                            label="正常文件">
                    </el-table-column>

                    <el-table-column
                            prop="exception_file_num"
                            width="80"
                            align="left"
                            label="异常文件">
                    </el-table-column>
                    <el-table-column
                            prop="mild_file_num"
                            width="100"
                            align="left"
                            label="轻度抄袭文件">
                    </el-table-column>
                    <el-table-column
                            prop="moderate_file_num"
                            width="100"
                            align="left"
                            label="中度抄袭文件">
                    </el-table-column>
                    <el-table-column
                            prop="severe_file_num"
                            width="100"
                            align="left"
                            label="重度抄袭文件">
                    </el-table-column>
                    <el-table-column
                            prop="remake"
                            width="600"
                            align="left"
                            label="备注">
                    </el-table-column>

                    <el-table-column
                            fixed="right"
                            width="260"
                            label="操作">
                        <template slot-scope="scope">
                            <el-button style="padding: 3px;margin-left: 13px" size="mini" type="primary" @click="searchFileGroupList(scope.row)">查看文件组列表</el-button>
                            <el-button @click="recordBasicStatistic(scope.row)" style="padding: 3px" size="mini" type="success">图表统计</el-button>
                            <!--<el-button @click="detectFeedback(scope.row)" style="padding: 3px" size="mini" type="warning">检测回馈</el-button>-->
                            <el-button @click="deleteRecord(scope.row)" style="padding: 3px" size="mini" type="danger">删除</el-button>

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
                <el-dialog title="统计资料" :visible.sync="showRecordBasicStatistic" stype="height:300px" width="60%">
                    <!--<ve-pie :data="chartData1"></ve-pie>-->
                    <!--<ve-pie :data="chartData2"></ve-pie>-->
                    <el-row>
                        <el-col :span="12">
                            <ve-pie :data="chartData3"></ve-pie>
                        </el-col>
                        <el-col :span="12">
                            <ve-pie :data="chartData4"></ve-pie>
                        </el-col>

                    </el-row>
                </el-dialog>
               <!-- 检测信息检测回馈模块-->
                <el-dialog
                        title="代码检测反馈"
                        :visible.sync="dialogVisible"
                        width="80%">
                    <div>
                        <el-form :model="detect_feedback" :rules="rules" ref="feedbackForm">
                            <el-row>
                                <el-col :span="8">
                                    <el-form-item label="轻度抄袭判定阈值:" prop="mild_sim">
                                        <el-input size="mini" style="width: 200px" prefix-icon="el-icon-edit" v-model="detect_feedback.mild_sim"
                                                  placeholder="请输入轻度抄袭判定阈值"
                                                  type="number"
                                                  max="1"
                                                  min="0"

                                        >

                                        </el-input>
                                    </el-form-item>
                                </el-col>
                                <el-col :span="8">
                                    <el-form-item label="中度抄袭判定阈值:" prop="moderate_sim">
                                        <el-input size="mini" style="width: 200px" prefix-icon="el-icon-edit" v-model="detect_feedback.moderate_sim"
                                                  placeholder="请输入中度抄袭判定阈值"></el-input>
                                    </el-form-item>
                                </el-col>
                                <el-col :span="8">
                                    <el-form-item label="重度抄袭判定阈值:" prop="severe_sim">
                                        <el-input size="mini" style="width: 200px" prefix-icon="el-icon-edit"
                                                  v-model="detect_feedback.severe_sim" placeholder="请输入重度抄袭判定阈值"></el-input>
                                    </el-form-item>
                                </el-col>
                            </el-row>
                        </el-form>
                    </div>
                    <span slot="footer" class="dialog-footer">
                        <el-button @click="dialogVisible = false">取 消</el-button>
                        <el-button type="primary" @click="doAddFeedBack">确 定</el-button>
                    </span>
                </el-dialog>
            </div>
        </div>
        <router-view :key="Math.random()" />
    </div>


</template>

<script>
    export default {
        name: "report_basic",
        data(){
            return{
                detect_feedback:{
                    record_id :"",
                    mild_sim : "",
                    moderate_sim :"",
                    severe_sim:"",
                },
                rules: {
                    mild_sim: [{required: true, message: '请输入轻度抄袭判定阈值', trigger: 'blur'}],
                    moderate_sim: [{required: true, message: '请输入中度抄袭判定阈值', trigger: 'blur'}],
                    severe_sim: [{required: true, message: '请输入重度抄袭判定阈值', trigger: 'blur'}],
                },
                dialogVisible:false,
                keyword:'',
                loading:false,
                start_time_filters:[],
                total: 0,
                size:10,
                page:1,

                date_filters:[{text: '2020-05', value: '2020-05'},{text: '2020-06', value: '2020-06'}],
                showBasicStatistic :false,
                showRecordBasicStatistic:false,
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
                        { 'degree': '简单检测', 'num': 0 },
                        { 'degree': '普通检测', 'num': 0 },
                        { 'degree': '深度检测', 'num': 0 },

                    ]
                },

                chartData3: {
                    columns: ['file_type', 'num'],
                    rows: [
                        { 'file_type': '正常文件', 'num': 0 },
                        { 'file_type': '异常文件', 'num': 0 },

                    ]
                },
                chartData4: {
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
        methods:{
            tag_type(data){
                if (data === "1"){
                    return "success";
                }else if(data === "2"){
                    return "warning";
                }else if(data === "3"){
                    return "danger";
                }
            },
            tag_text(data){
            // == '1' ? '简单检测' : ('2' ? '普通检测': ('3' ?'深度检测':""))
                if (data === "1"){
                    return "简单检测";
                }else if(data === "2"){
                    return "普通检测";
                }else if(data === "3"){
                    return "深度检测";
                }
            },

            //请求record_list列表
            requestRecordList(){
                this.loading = true;
                this.getRequest("/detect_record_info/?page="+this.page+"&"+"size="+this.size+"&user_id="+this.user.id+"&"+"identity="+this.user.identity).then(resp =>{

                    if(resp){
                            console.log(resp.data.data['record_list']);
                            //填充图标的数据
                            //图一
                            //工程检测个数
                            this.chartData1['rows'][0]['num'] = resp.data.data['project_detect_num'];
                            //文件检测个数
                            this.chartData1['rows'][1]['num'] = resp.data.data['file_detect_num'];
                            //图二
                            //简单检测个数
                            this.chartData2['rows'][0]['num'] = resp.data.data['simple_detect_num'];
                            //普通检测个数
                            this.chartData2['rows'][1]['num'] = resp.data.data['mid_detect_num'];
                            //深度检测个数
                            this.chartData2['rows'][2]['num'] = resp.data.data['deep_detect_num'];
                            this.total = resp.data.data['total'];
                            this.$store.commit('init_detect_record_list',resp.data.data['record_list']);
                            this.loading = false;
                        }
                    }

                );

            },
            //展示record_list图表统计
            detect_basic_statistic(){
                //填充图表的数据

                this.showBasicStatistic = true;

            },

            //做分页处理
            // initRecordList(){
            //     this.record_list_display = [];
            //     let _this = this;
            //     let page = this.page;
            //     let size = this.size;
            //     let record_list_display_index = 0;
            //     let start_index = (page-1)*size;
            //     for(let i= start_index;i<this.record_list.length,i<start_index+size;i++){
            //         this.record_list_display[record_list_display_index] = _this.record_list[i];
            //         record_list_display_index ++;
            //     }
            //     console.log(this.record_list_display)
            // },
            /**对degree字段进行格式转化**/
            degreeFormatter(row,column){
                if(row.degree === "1"){
                    return "简单检测"
                }else if(row.degree === "2"){
                    return "普通检测"
                }else if(row.degree === "3"){
                    return "深度检测"
                }

            },

            detectFeedback(data){
                this.emptyFeedBack();
                this.detect_feedback.record_id = data.id;
                this.dialogVisible = true;

            },
            doAddFeedBack(){
                let data = {
                    "record_id":this.detect_feedback.record_id,
                    "mild_sim":this.detect_feedback.mild_sim,
                    "moderate_sim":this.detect_feedback.moderate_sim,
                    "severe_sim":this.detect_feedback.severe_sim,

                };

                this.postRequest("/detect_feedback_info/",data).then(resp=>{
                    this.dialogVisible = false;

                });



            },
            emptyFeedBack(){
                this.detect_feedback = {
                    record_id :"",
                    mild_sim : "",
                    moderate_sim :"",
                    severe_sim:"",
                }
            },
            deleteRecord(data){
                this.$confirm('此操作将永久删除【' + data.title + '】, 是否继续?', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.deleteRequest("/detect_record_info/?ids=" + data.id).then(resp => {
                        if (resp) {
                            this.requestRecordList();
                            // this.initRecordList();
                        }
                    })
                }).catch(() => {
                    this.$message({
                        type: 'info',
                        message: '已取消删除'
                    });
                });

            },
            //展示图表统计
            recordBasicStatistic(data){
                //正常文件个数
                this.chartData3['rows'][0]['num'] = data['normal_file_num'];
                //异常文件个数
                this.chartData3['rows'][1]['num'] = data['exception_file_num'];
                //图二
                //正常文件个数
                this.chartData4['rows'][0]['num'] = data['normal_file_num'] - data['mild_file_num'] - data['moderate_file_num'] - data['severe_file_num'];
                //轻度文件个数
                this.chartData4['rows'][1]['num'] = data['mild_file_num'];
                //中度文件个数
                this.chartData4['rows'][3]['num'] = data['moderate_file_num'];
                //重度文件个数
                this.chartData4['rows'][2]['num'] = data['severe_file_num'];
                this.showRecordBasicStatistic = true;


            },
            searchFileGroupList(data){
                this.$store.commit('init_current_record_id',data['id']);
                // this.$store.commit('set_report_component_display',false);
                this.$router.push({path: '/report/group/file_group_basic'});
            },
            filter_func_type_Tag(value, row) {
                return row.func_type === value;
            },
            filter_degree_Tag(value, row) {
                return row.degree === value;
            },

            filterHandler(value, row, column) {
                const property = column['property'];
                console.log(row[property]);
                console.log(value);
                return (row[property]+"").includes(value+"");
            },
            sizeChange(currentSize) {
                this.size = currentSize;

                this.requestRecordList();
            },
            currentChange(currentPage) {
                this.page = currentPage;
                this.requestRecordList();
            },


        },

        // beforeRouteEnter (to, from, next) {
        //     console.log(to);
        //     console.log(from);
        //     // next(vm => {
        //     //     console.log(vm);
        //     //     console.log(to);
        //     //     console.log(from)
        //     //     // vm.report_component_display=true;
        //     //     // console.log(vm.report_component_display)
        //     // })
        //     // next();
        // },
        mounted(){
            this.requestRecordList();


        },
        // activated(){
        //     this.getCase()
        // },

        computed:{
            record_list(){
                return this.$store.state.detect_record_list;
            },
            user(){
                return this.$store.state.currentHr;
            },
            // report_component_display(){
            //     return this.$store.state.report_component_display;
            // }

        },

    }
</script>

<style scoped>
    /* 可以设置不同的进入和离开动画 */
    /* 设置持续时间和动画函数 */
    .slide-fade-enter-active {
        transition: all .8s ease;
    }

    .slide-fade-leave-active {
        transition: all .8s cubic-bezier(1.0, 0.5, 0.8, 1.0);
    }

    .slide-fade-enter, .slide-fade-leave-to
        /* .slide-fade-leave-active for below version 2.1.8 */
    {
        transform: translateX(10px);
        opacity: 0;
    }


</style>