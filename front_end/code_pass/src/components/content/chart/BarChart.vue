<!--柱状图组件-->
<template>
    <div :id="id" style="width: 100%;height: 400px;">
    </div>
</template>

<script>
    var echarts = require('echarts');
    const axios = require('axios').create({
        baseURL: '',
        headers: {
            'Content-type': 'multipart/form-data'
        }
    });
    export default {
        name: 'barChart',
        props: {
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
                id: Math.random().toString(36).substr(2),
                goods: {},
                options: {
                    // color: ['#83d0d5', '#f1cb48', '#188ae2', '#E8830B', '#7460ae', '#fc4b6c', '#31ce77', '#eae0bc', '#e732cb', '#9dce8a'],
                    title: {
                        text: this.titletext,
                        left: 'center',
                        top: 20,
                        textStyle: {
                            color: '#666',
                            fontStyle: '' //标题字体
                        }
                    }, //{text: '异步数据加载示例'},
                    tooltip: {
                        trigger: 'item'
                    },
                    xAxis: {
                        type: 'category',
                        data: this.xdata,
                        name: this.xname,
                        nameLocation: 'end',
                        minInterval: 1,
                        axisLabel: {
                            interval: 0
                        }
                    },
                    yAxis: {
                        type: 'value',
                        name: this.yname
                    },
                    dataset: {
                        dimensions: [],
                        source: [] //source取的全部数据
                    },
                    legend: {
                        orient: 'horizontal',
                        bottom:'0%',
                        data: this.legdata,
                    },
                    series: [{
                        name: '',
                        type: 'bar',
                        color: ['#5CACEE'],
                        data: [], //纵坐标数据
                      maxBarWidth:30,
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
                    }],
                }
            }
        },
        mounted() {
            this.$nextTick(() => {
                this.drawLine();
            })
        },
        created() {
            console.log("bar柱状图");
            axios.post(this.inpath).then(res => {
                const data = res.data;
                this.goods = data
                console.log("柱状图");
                console.log(this.goods);
            })
        },
        methods: {
            drawLine() {
                // 基于准备好的dom，初始化echarts实例
                let barChart = echarts.init(document.getElementById(this.id))
                // 绘制图表
                barChart.setOption(this.options);
                //显示加载动画
                barChart.showLoading({
                    text: '',
                    color: '#5CACEE',
                    maskColor: 'rgba(255, 255, 255, 0.8)',
                    zlevel: 0
                });
                axios.post(this.inpath).then((res) => {
                    setTimeout(() => { //未来让加载动画效果明显,这里加入了setTimeout,实现3s延时
                        console.log(JSON.parse(JSON.stringify(res.data)));
                        const data = JSON.parse(JSON.stringify(res.data));
                        console.log(this.titletext);
                        console.log(data)
                        // const list = data.series.map(good => {
                        //     let list = good.data;
                        //     console.log("柱状图的list：")
                        //     console.log(...list);
                        //     return [...list]
                        // })
                        this.options.dataset=data.dataset;
                        this.options.series=data.series;
                        barChart.hideLoading(); //隐藏加载动画
                        barChart.setOption(this.options);
                    }, 1000);

                })
            }
        }
    }
</script>
