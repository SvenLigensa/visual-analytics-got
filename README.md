[![Deployment](https://img.shields.io/badge/shinyapps.io-deployed-green)](https://sven-ligensa.shinyapps.io/got-analytics/)

# Visual Analytics app for Game Of Thrones

Run the **Shiny Python** app locally by executing the `app.py` script from the root folder (`visual-analytics-got`).

## Run Locally

*Without* Docker:
- `$ shiny run --reload visual-analytics-shiny/app.py`

With *Docker* (Dockerfile set up following [this tutorial](https://hosting.analythium.io/containerizing-shiny-for-python-and-shinylive-applications/)):
1. `$ docker build -t visual-analytics-got .`
2. `$ docker run -p 8080:8080 visual-analytics-got`

## TODOs

- Improve the linechart to use `characters_time.csv` instead of `time.csv`
    - Then, remove `time.csv` and `X_process_time.py`
- Add tab for 'About' with background information about the project and Credits
