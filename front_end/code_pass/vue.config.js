
let proxyObj = {};
// const CompressionPlugin = require("compression-webpack-plugin");
const MonacoEditorPlugin = require('monaco-editor-webpack-plugin');

proxyObj['/code_pass'] = {
    ws: false,
    target: 'http://localhost:8080',
    changeOrigin: true,
    timeout:60*60*1000,
    pathRewrite: {
        '^/': ''
    }
};

module.exports = {
    devServer: {
        open: false,
        host: 'localhost',
        port: 9000,
        proxy: proxyObj,
    },
    configureWebpack: {

        plugins: [
            new MonacoEditorPlugin({
                // https://github.com/Microsoft/monaco-editor-webpack-plugin#options
                // Include a subset of languages support
                // Some language extensions like typescript are so huge that may impact build performance
                // e.g. Build full languages support with webpack 4.0 takes over 80 seconds
                // Languages are loaded on demand at runtime
                languages: ['java', 'c']
            })
        ],
    },
    // configureWebpack: config => {
    //
    //     // 解决vue接口联调跨域问题
    //     config.devServer = {
    //         open: false,
    //         host: 'localhost',
    //         port: 9000,
    //         proxy: proxyObj,
    //
    //     };
    //
    //
    //     // 将vux-ui合并到config中
    //     require('monaco-editor-webpack-plugin').merge(config, {
    //         options: {languages: ['java', 'c']},
    //         plugins: ['monaco-editor-webpack'],
    //     });
    // },



    // transpileDependencies: [
    //     'vue-echarts',
    //     'resize-detector'
    // ]
    // configureWebpack: config => {
    //     if (process.env.NODE_ENV === 'production') {
    //         return {
    //             plugins: [
    //                 new CompressionPlugin({
    //                     test: /\.js$|\.html$|\.css/,
    //                     threshold: 1024,
    //                     deleteOriginalAssets: false
    //                 })
    //             ]
    //         }
    //     }
    // }
};