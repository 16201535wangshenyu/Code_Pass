<template>
    <div>
        <div>
            <div style="display: flex;justify-content: space-between">
                <div>
                    <el-input placeholder="请输入文件名进行搜索..." prefix-icon="el-icon-search"
                              clearable
                              style="width: 350px;margin-right: 10px" v-model="keyword">
                    </el-input>
                </div>
                <!--图表统计 文件编码格式-->
            </div>
        </div>
        <div style="margin-top: 15px">
            <el-table
                    :data="file_list.filter(data => !keyword || data.name.toLowerCase().includes(keyword.toLowerCase()))"
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
                <el-table-column type="expand">
                    <template slot-scope="props">
                        <el-table
                                :data="props.row.similarity_list"
                                height="250"
                                border
                                stripe
                                style="width: 100%">
                            <el-table-column
                                    prop="file2.path"
                                    label="匹配文件"
                                    width="362">
                            </el-table-column>
                            <el-table-column
                                    prop="attribute_similarity"
                                    sortable
                                    label="属性相似度"
                                    :formatter="similarityFormatter"
                                    width="110">
                            </el-table-column>
                            <el-table-column
                                    width="130"
                                    sortable
                                    :formatter="similarityFormatter"
                                    prop="sample_text_similarity"
                                    label="抽样文本相似度">
                            </el-table-column>
                            <el-table-column
                                    width="110"
                                    sortable
                                    :formatter="similarityFormatter"
                                    prop="text_similarity"
                                    label="文本相似度">
                            </el-table-column>
                            <el-table-column
                                    width="110"
                                    sortable
                                    :formatter="similarityFormatter"
                                    prop="struct_similarity"
                                    label="结构相似度">
                            </el-table-column>
                            <el-table-column
                                    width="100"
                                    sortable
                                    :formatter="similarityFormatter"
                                    prop="similarity"
                                    label="总相似度">
                            </el-table-column>
                            <el-table-column
                                    width="100"
                                    prop="is_max_similarity"
                                    :formatter="is_max_similarityFormatter"
                                    label="最大相似度">
                            </el-table-column>
                            <el-table-column
                                    width="170"
                                    fixed="right"
                                    label="操作">
                                <template slot-scope="scope">
                                    <el-button style="padding: 3px" size="mini" :disabled="btn_disabled(scope.row)" type="primary" @click="searchMatchText(scope.row)">查看匹配文本</el-button>
                                    <el-button @click="similarityBasicStatistic(scope.row)" style="padding: 3px" size="mini" type="success">图表统计</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </template>
                </el-table-column>
                <el-table-column
                        prop="name"
                        align="left"
                        label="名称"
                        width="200">
                </el-table-column>

                <el-table-column
                        prop="type"
                        width="120"
                        align="center"

                        label="文件类型">
                </el-table-column>
                <el-table-column
                        prop="encoding"
                        width="120"
                        align="center"
                        label="编码格式">
                </el-table-column>

                <el-table-column
                        prop="is_normal"
                        width="120"
                        align="center"
                        :filters="[{ text: '正常', value: true }, { text: '异常', value: false }]"
                        :filter-method="filter_is_normal_Tag"
                        filter-placement="bottom-end"
                        label="是否正常">
                    <template slot-scope="scope">
                        <el-tag
                                :type="scope.row.is_normal === true ? 'success' : 'warning'"
                                disable-transitions>{{scope.row.is_normal === true ? '正常文件' : '异常文件'}}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column
                        prop="copy_rank"
                        width="120"
                        align="center"
                        :filters="[{ text: '无抄袭', value: 0 }, { text: '轻度抄袭', value: 1 },{ text: '中度抄袭', value: 2 },{ text: '重度抄袭', value: 3 } ]"
                        :filter-method="filter_copy_rank_Tag"
                        filter-placement="bottom-end"
                        label="抄袭等级">
                    <template slot-scope="scope">
                        <el-tag
                                :type="tag_type(scope.row.copy_rank)"
                                disable-transitions>{{tag_text(scope.row.copy_rank)}}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column
                        prop="path"
                        width="332"
                        align="center"
                        label="文件路径">
                </el-table-column>
                <el-table-column

                        width="200"
                        label="操作">
                    <template slot-scope="scope">
                        <el-button @click="viewFileContent(scope.row)" style="padding: 3px" size="mini" type="success">查看文件内容</el-button>
                        <el-button @click="detectFeedback(scope.row)" style="padding: 3px" size="mini" type="warning">检测回馈</el-button>
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
        </div>
        <!--图表统计模块-->
        <el-dialog title="统计资料" :visible.sync="showBasicStatistic" stype="height:300px" width="50%">

            <el-row>
                <el-col :span="24">
                    <ve-pie :data="chartData2"></ve-pie>
                </el-col>

            </el-row>

        </el-dialog>
        <!--java文本查看器-->
        <el-dialog title="Java文本" :visible.sync="showJavaContent" stype="height: 460px" width="45%">
            <el-row>
                <MonacoEditor   v-model="code" :options="editorOptions" language="java"  />
            </el-row>
        </el-dialog>
        <!--java文本查看器-->
        <el-dialog title="Java文本" :visible.sync="showJavaSameContent" stype="height: 460px" width="90%">

            <el-row>
                <el-col :span="12">
                    <MonacoEditor  @editorDidMount="editorDidMount1" v-model="code1" ref="editor1"  :options="editorOptions" language="java"  />
                </el-col>
                <el-col :span="12">
                    <MonacoEditor  @editorDidMount="editorDidMount2" v-model="code2" ref="editor2"  :options="editorOptions" language="java"  />
                </el-col>
            </el-row>

        </el-dialog>
        <!-- 检测信息检测回馈模块-->
        <el-dialog
                title="代码检测反馈"
                :visible.sync="dialogVisible"
                width="30%">
            <div>
                <el-form :model="detect_feedback" :rules="rules" ref="feedbackForm">
                    <el-row>
                        <el-col :span="16">
                            <el-form-item label="期望抄袭等级:" prop="severe_sim">
                                <el-select v-model="detect_feedback.severe_sim" clearable placeholder="请选择抄袭等级">
                                    <el-option
                                            v-for="item in options"
                                            :key="item.value"
                                            :label="item.label"
                                            :value="item.value">
                                    </el-option>
                                </el-select>
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
</template>

<script>
    // import JavaEditor from '../../../../../components/content/editor/java/Page';
    import MonacoEditor from 'vue-monaco';
    export default {
        name: "file_basic",
        components: {MonacoEditor},
        data(){
            return{
                options:[
                    {
                        label:"无抄袭",
                        value:0,
                    },
                    {
                        label:"轻度抄袭",
                        value:1,
                    },
                    {
                        label:"中度抄袭",
                        value:2,
                    },
                    {
                        label:"重度抄袭",
                        value:3,
                    },
                ],

                editorOptions: {

                    dimension:{
                        height:460,
                        width:670
                    },
                    selectOnLineNumbers: true,
                    readOnly: true, // 只读
                    cursorStyle: 'line', // 光标样式
                    automaticLayout: false, // 自动布局
                    glyphMargin: true, // 字形边缘
                    useTabStops: false,
                    autoIndent: true // 自动布局

                },
                detect_feedback:{
                    file_id :"",

                    severe_sim:"",
                },
                text:"",
                code:"",
                code1:"",
                code2:"",
                matches:[],
                dialogVisible: false,
                //判断similarity的file1与file2有没有进行了交换
                is_change:false,
                file_list:[],
                keyword:'',
                size:10,
                page:1,
                total:0,
                loading:false,
                showBasicStatistic:false,
                showJavaContent:false,
                showJavaSameContent:false,

                chartData2: {
                    columns: ['similarity_type', 'value'],
                    rows: [
                        { 'similarity_type': '文本相似度', 'value': 0 },
                        { 'similarity_type': '属性相似度', 'value': 0 },
                        { 'similarity_type': '结构相似度', 'value': 0 },


                    ]
                },
                rules: {
                    severe_sim: [{required: true, message: '请选择期望抄袭等级', trigger: 'blur'}],
                },
            }
        },
        methods:{
            tag_type(data){
                if (data === 0){
                    return "success";
                }else if(data ===1){
                    return "primary";
                }else if(data ===2){
                    return "warning";
                }else if(data ===3){
                    return "danger";
                }

            },
            tag_text(data){
            /*=== 0 ? '无抄袭' : (1 ? '轻度抄袭':( 2 ? '中度抄袭' :'重度抄袭'))*/
                if (data === 0){
                    return "无抄袭";
                }else if(data ===1){
                    return "轻度抄袭";
                }else if(data ===2){
                    return "中度抄袭";
                }else if(data ===3){
                    return "重度抄袭";
                }

            },
            btn_disabled(data){
                return data['matches_list'].length === 0;

            },
            editorDidMount1(editor){

                if (editor.getModel()!==undefined){
                    editor.getModel().setValue(this.code1)
                }
                let _this = this;
                let start_line = 0;
                let start_pos = 0;
                let end_line = 0;
                let end_pos = 0;
                let ISelection = [];
                if(this.is_change === true){
                    for(let i = 0; i < _this.matches.length; i++) {
                        start_line = _this.matches[i]['text2_start_line'];
                        start_pos = _this.matches[i]['text2_start_pos'];
                        end_line = _this.matches[i]['text2_end_line'];
                        end_pos = _this.matches[i]['text2_end_pos'];
                        ISelection[i] = {
                            selectionStartLineNumber:start_line,
                            selectionStartColumn:start_pos-1,
                            positionLineNumber:end_line,
                            positionColumn:end_pos,
                        };

                    }
                }else{
                    for(let i = 0; i < _this.matches.length; i++) {
                        start_line = _this.matches[i]['text1_start_line'];
                        start_pos = _this.matches[i]['text1_start_pos'];
                        end_line = _this.matches[i]['text1_end_line'];
                        end_pos = _this.matches[i]['text1_end_pos'];
                        ISelection[i] = {
                            selectionStartLineNumber:start_line,
                            selectionStartColumn:start_pos-1,
                            positionLineNumber:end_line,
                            positionColumn:end_pos,
                        };
                    }
                }
                // console.log(ISelection);
                editor.setSelections(ISelection);
            },
            editorDidMount2(editor){

                if (editor.getModel()!==undefined){
                    editor.getModel().setValue(this.code2)
                }

                let _this = this;
                let start_line = 0;
                let start_pos = 0;
                let end_line = 0;
                let end_pos = 0;
                let ISelection = [];
                if(this.is_change === true){
                    for(let i = 0; i < _this.matches.length; i++) {
                        start_line = _this.matches[i]['text1_start_line'];
                        start_pos = _this.matches[i]['text1_start_pos'];
                        end_line = _this.matches[i]['text1_end_line'];
                        end_pos = _this.matches[i]['text1_end_pos'];
                        ISelection[i] = {
                            selectionStartLineNumber:start_line,
                            selectionStartColumn:start_pos-1,
                            positionLineNumber:end_line,
                            positionColumn:end_pos,
                        };
                    }

                }else{
                    for(let i = 0; i < _this.matches.length; i++) {
                        start_line = _this.matches[i]['text2_start_line'];
                        start_pos = _this.matches[i]['text2_start_pos'];
                        end_line = _this.matches[i]['text2_end_line'];
                        end_pos = _this.matches[i]['text2_end_pos'];
                        ISelection[i] = {
                            selectionStartLineNumber:start_line,
                            selectionStartColumn:start_pos-1,
                            positionLineNumber:end_line,
                            positionColumn:end_pos,
                        };
                    }
                }
                editor.setSelections(ISelection);
            },
            //

            requestFileList(){
                this.loading = true;
                this.getRequest("/file_info/?page="+this.page+"&"+"size="+this.size+"&group_id="+this.group_id).then(resp=>{
                    if(resp){
                        this.total = resp.data.data['total'];
                        this.file_list = resp.data.data['file_list'];
                        // console.log(this.file_list);
                        this.loading = false;
                    }
                });
            },
            similarityFormatter(row, column, cellValue, index){
                if (cellValue === null){
                    return "--";
                }else {
                    let percent = (cellValue*100).toFixed(2);
                    percent+="%";
                    return percent;
                }


            },
            is_max_similarityFormatter(row, column, cellValue, index){
                if(cellValue === true){
                    return "是";
                }else
                    return "否";

            },
            filter_is_normal_Tag(value, row){
                return row.is_normal === value;
            },
            filter_copy_rank_Tag(value, row){
                return row.copy_rank === value;
            },
            searchMatchText(data){
                this.code1 = data['file1']['content'];
                this.code2 = data['file2']['content'];
                this.matches = data['matches_list'];
                this.is_change = data['is_change'];

                if (this.$refs.editor1 !== undefined && this.$refs.editor2 !== undefined ){
                    this.editorDidMount1(this.$refs.editor1.getEditor());
                    this.editorDidMount2(this.$refs.editor2.getEditor());
                    this.showJavaSameContent = true;


                }
                this.showJavaSameContent = true;



            },
            viewFileContent(data){
                this.code = data['content'];
                this.showJavaContent = true;
            },

            similarityBasicStatistic(data){

                //异常文件个数
                this.chartData2['rows'][0]['value'] = data['text_similarity']==="undefined"?data['sample_text_similarity']:data['text_similarity'];
                this.chartData2['rows'][1]['value'] = data['attribute_similarity'];
                this.chartData2['rows'][2]['value'] = data['struct_similarity'];
                //图二
                this.showBasicStatistic = true;

            },
            sizeChange(currentSize) {
                this.size = currentSize;
                this.requestFileList();
            },
            currentChange(currentPage) {
                this.page = currentPage;
                this.requestFileList();
            },
            detectFeedback(data){
                this.emptyFeedBack();
                this.detect_feedback.file_id = data.id;
                this.dialogVisible = true;

            },
            doAddFeedBack(){
                let data = {
                    "file_id":this.detect_feedback.file_id,
                    "severe_sim":this.detect_feedback.severe_sim,
                };
                this.$refs.feedbackForm.validate((valid) => {
                    if(valid){

                        this.postRequest("/detect_feedback_info/",data).then(resp=>{
                            this.dialogVisible = false;

                        });

                    }else{
                        return false;
                    }


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
        },
        computed:{
            group_id(){
                return this.$store.state.current_group_id
            },

        },
        mounted(){
            this.requestFileList();

        },
    }
</script>

<style scoped>
    /*.editor {*/
        /*width: 100%;*/
        /*height: 460px;*/

    /*}*/

</style>