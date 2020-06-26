<!--折线图组件-->
<template>
    <div :id="id" style="width: 100%;height: 400px;">
    </div>
</template>
<script>
    let echarts = require('echarts');
    const axios = require('axios').create({
        baseURL: '',
        headers: {
            'Content-type': 'multipart/form-data'
        }
    });
    export default {
        name: "lineChart",
        props:{
            inpath:String,
            titletext:String,
            legdata:Array,
            xdata:Array,
            xname:String,
            yname:String
        },
        data() {
            return {
                msg: 'BarChart',
                id:Math.random().toString(36).substr(2),
                goods: {},
                options: {
                    title: { 
                        text: this.titletext,
                        left: 'center',
                        top: 20,
                        textStyle: {
                            color: '#666',
                            fontStyle: '' //标题字体
                        }
                    },
                    legend: {
                        name:'',
                        bottom:'0%',
                        data:this.legdata
                    },
                    dataset: {
                        dimensions: [],
                        source: [] //source取的全部数据
                    },
                    xAxis: {
                        type: 'category',
                        data: this.xdata,
                        name: this.xname
                    },
                    yAxis: {
                        type:'value',
                        name:this.yname,
                    },
                    label: {},
                    tooltip: {trigger:'item'},
                    series: [{
                        name:'',
                        data:[],
                        type:'line',
                        color:["#5CACEE"],
                        itemStyle: {
                                normal: {
                                    label: {
                                        show: true, //开启显示
                                        position: 'top', //在上方显示
                                        textStyle: { //数值样式
                                            color: 'gray',
                                            fontSize: 12
                                        }
                                    }
                                }
                            }
                    }]
                }
            }
        },
        mounted() {
            this.$nextTick(()=>{
                this.drawLine();
            })
        },
        created() {
            axios.post(this.inpath).then(res => {
                const data = JSON.parse(res.data);
                this.goods = data
                console.log("created"+this.goods);
            })
        },
        methods: {
            drawLine: function() {
                // 基于准备好的dom，初始化echarts实例
                let lineChart = echarts.init(document.getElementById(this.id));
                lineChart.setOption(this.options);
                lineChart.showLoading({
                    text: '',
                    color: '#5CACEE',
                    maskColor: 'rgba(255, 255, 255, 0.8)',
                    zlevel: 0
                });
                axios.post(this.inpath).then((resp)=>{

                    setTimeout(()=>{
                        let data = JSON.parse(JSON.stringify(resp.data));
                        console.log(JSON.parse(JSON.stringify(resp.data)));
                        lineChart.hideLoading();
                        this.options.dataset=data.dataset;
                        this.options.series=data.series;
                        lineChart.setOption(this.options);
                    },2000);
                });
            }
        }
    }
</script>