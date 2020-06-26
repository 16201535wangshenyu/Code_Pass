<template>
    <div class="echarts-box" ref="ref" :id="id">
    </div>
</template>
<script>
    var echarts = require('echarts');
    const axios = require('axios');
    export default {
        name: 'nightingaleChart',
        props: [
            'inpath',"titletext","dataname"
        ],
        data() {
            return {
                id: Math.random().toString(36).substr(2),
                
                options: {
                    backgroundColor: '#ffffff',
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
                        name: '',
                        data: []
                    },
                    tooltip: {
                        trigger: 'item'
                    },
                    //视觉映射组件，将数据映射到视觉元素上
                    visualMap: {
                        show: false,
                        min: -200,
                        max: 600,
                        inRange: {
                            colorLightness: [0.2, 0.8]
                        }
                    },
                    //数据
                    series: [{
                        name: this.dataname,
                        type: 'pie',
                        radius: '55%',
                        center: ['50%', '50%'],
                        data: [{
                            value: 20,
                            name: ''
                        }].sort(function(a, b) {
                            return a.value - b.value;
                        }),
                        roseType: 'angle', //角度和半径展现百分比，'area'只用半径展现
                        label: { //饼图图形的文本标签
                            normal: { //下同，normal指在普通情况下样式，而非高亮时样式
                                textStyle: {
                                    color: 'rgba(100, 100, 100, 1)'
                                }
                            }
                        },
                        labelLine: { //引导线样式
                            normal: {
                                lineStyle: {
                                    color: 'rgba(100, 100, 100, 1)'
                                },
                            }
                        },
                        itemStyle: {
                            normal: {
                               color: '#f1fdff',
                                shadowBlur: 50,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            },
                            // emphasis: {
                            //     shadowBlur: 200,
                            //     shadowColor: 'rgba(0, 0, 0, 0.5)'
                            // }
                        },
                        animationType: 'scale', //初始动画效果，scale是缩放，expansion是展开
                        animationEasing: 'elasticOut', //初始动画缓动效果
                        animationDelay: function(idx) { //数据更新动画时长，idx限定了每个数据块从无到有的速度
                            return Math.random() * 200;
                        }
                    }]
                }
            }
        },
        mounted: function() {
            this.$nextTick(() => {
                this.drawNightingale();
            })
        },
        created: function() {
            axios.post(this.inpath).then(res => {
                console.log(this.titletext);
                console.log(res.data);
                const data = res.data;
                this.goods = data
                console.log("create:" + this.goods);
            })
        },
        methods: {
            drawNightingale: function() {
                let nightingaleCHart = echarts.init(document.getElementById(this.id));
                nightingaleCHart.setOption(this.options);
                nightingaleCHart.showLoading({
                    text: '',
                    color: '#5CACEE',
                    maskColor: 'rgba(255, 255, 255, 0.8)',
                    zlevel: 0
                });
                console.log("南丁格尔图：")
                axios.post(this.inpath).then((resp) => {
                     console.log(JSON.parse(JSON.stringify(resp.data)));
                    setTimeout(() => {
                        let data = resp.data;
                        console.log("mounted:" + data)
                        let list = data.series.map(good => {
                            let list = good.data;
                            console.log("南丁格尔图：");
                            console.log(...list);
                            return [...list];
                        });
                        console.log(Array.from(...list));
                        nightingaleCHart.hideLoading();
                        nightingaleCHart.setOption({
                            series: {
                                data: Array.from(...list)
                            }
                        });
                    }, 2000);
                });
            }
        }
    }
</script>
<style scoped>
    .echarts-box {
        width: 100%;
        height: 400px;
    }
</style>