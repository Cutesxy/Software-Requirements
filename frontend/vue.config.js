module.exports = {
  devServer: {
    port: 8080,
    open: true
  },
  css: {
    loaderOptions: {
      sass: {
        additionalData: `@import "@/styles/variables.scss";`
      }
    }
  }
}

