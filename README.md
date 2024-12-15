[![Deployment](https://img.shields.io/badge/shinyapps.io-deployed-green)](https://sven-ligensa.shinyapps.io/got-analytics/)

# Visual Analytics app for Game Of Thrones

Please read the [report](visual-analytics-shiny/static/Report.pdf) for details on the background of this project.

## Run Locally

*Without* Docker:
1. Install requirements: `$ pip install -r visual-analytics-shiny/requirements.txt`
2. Run the app locally by executing the `app.py` script from the root folder (`visual-analytics-got`): `$ shiny run --reload visual-analytics-shiny/app.py`

With *Docker* (Dockerfile set up following [this tutorial](https://hosting.analythium.io/containerizing-shiny-for-python-and-shinylive-applications/)):
1. `$ docker build -t visual-analytics-got .`
2. `$ docker run -p 8080:8080 visual-analytics-got`
