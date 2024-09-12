# Visual Analytics app for Game Of Thrones

## Deployment

This app is deployed on GitHub pages by following [this tutorial](https://medium.com/@rami.krispin/deploy-shiny-app-on-github-pages-b4cbd433bdc).
The main steps to be executed in the R shell are:
1. `install.packages(c("shinylive", "httpuv"))`
2. `shinylive::export(appdir = "visual-analytics-shiny", destdir = "docs")`
3. `httpuv::runStaticServer("docs/", port=8008)`
