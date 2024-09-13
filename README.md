[![GitHub Pages Link](https://img.shields.io/badge/Website-GitHub_Pages-2196f3)](https://svenligensa.github.io/visual-analytics-got/)
[![Build and Deploy Shiny App](https://github.com/SvenLigensa/visual-analytics-got/actions/workflows/build-and-deploy.yml/badge.svg)](https://github.com/SvenLigensa/visual-analytics-got/actions/workflows/build-and-deploy.yml)

# Visual Analytics app for Game Of Thrones

## Deployment

This app is deployed on GitHub pages by following [this tutorial](https://medium.com/@rami.krispin/deploy-shiny-app-on-github-pages-b4cbd433bdc).

- Initially, the packages `shinylive` and `httpuv` need to be installed: `install.packages(c("shinylive", "httpuv"))`.
- Then, after changing the Shiny app, the changes are propagated to the `docs` directory with the following command: `shinylive::export(appdir = "visual-analytics-shiny", destdir = "docs")`
- Optionally, to test it locally, run: `httpuv::runStaticServer("docs/", port=8008)`
