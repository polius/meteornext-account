const CompressionWebpackPlugin = require('compression-webpack-plugin')

module.exports = {
  transpileDependencies: [
    'vuetify'
  ],
  productionSourceMap: false,
  devServer: {
    disableHostCheck: true,
    headers: { 'Access-Control-Allow-Origin': '*' }
  },
  css: {
    loaderOptions: {
      sass: {
        additionalData: `@import "@/styles/variables.scss"`,
      }
    }
  },
  configureWebpack: {
    plugins: [
      new CompressionWebpackPlugin() // Remove "{ cache: false }" for Production
    ]
  }
}
