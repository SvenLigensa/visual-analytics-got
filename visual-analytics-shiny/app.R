library(shiny)
library(shinyjs)
library(shinyWidgets)
library(bslib)

ui <- page_sidebar(
  useShinyjs(),

  # Links to external CSS and JS code
  tags$head(
    tags$link(rel = "stylesheet", type = "text/css", href = "styles.css"),
    tags$script(src = "script.js")
  ),

  tags$div(
    class = "got-font",
    tags$h1("Game of Thrones Analyzer")
  ),

  sidebar = div(
    card(
      card_header(h4("Show locations")),
      selectizeInput(
        inputId = "location",
        label = "Select locations:",
        choices = c(),
        multiple = TRUE,
        options = list(
          placeholder = 'Type to search...',
          maxOptions = 5
        )
      ),
      actionButton("show", label = tagList("Show")),
      actionButton("hide", label = tagList("Hide"))
    ),
  ),
  
  card(
    div(id = "map-container",
        tags$img(id = "map-img", src = "map.png"),
        tags$svg(id = "map-canvas"),
    )
  ),
)

server <- function(input, output, session) {

  city_data <- read.csv("city_data.csv", stringsAsFactors = FALSE)

  locations <- city_data[["location"]]
  updateSelectizeInput(session, "location", choices = locations, server = TRUE)

  observeEvent(input$show, {
    selected_cities <- city_data[city_data$location %in% input$location, ]

    for (i in 1:nrow(selected_cities)) {
      city <- selected_cities[i, ]
      runjs(sprintf("showCity(%f, %f, %f, '%s', %f, '%s');", 
                    city$point_x, city$point_y, city$diameter, city$color, city$font_size, city$location))
    }
  })
  
  observeEvent(input$hide, {
    runjs("hideAnnotations();")
  })
}

shinyApp(ui = ui, server = server)
