
- https://medium.com/@rami.krispin/deploy-shiny-app-on-github-pages-b4cbd433bdc
    1. `install.packages(c("shinylive", "httpuv"))`
    2. `shinylive::export(appdir = "visual-analytics-shiny", destdir = "docs")`
    3. `httpuv::runStaticServer("docs/", port=8008)`
