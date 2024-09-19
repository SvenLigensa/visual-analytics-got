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
  
  div(
    class = "content-container",
    card(
      class = "map-card",
      actionButton(
        inputId = "toggle_fit",
        label = tags$img(src = "fit_h.png", height = "40px"), # https://www.flaticon.com/free-icon/fit_2012194
        class = "fit-toggle-button"
      ),
      div(id = "map-container",
          div(class = "map-wrapper",
              tags$img(id = "map-img", src = "map.png"),
              tags$svg(id = "map-canvas"),
          )
      )
    )
  )
)

server <- function(input, output, session) {

  city_data <- read.csv("city_data.csv", stringsAsFactors = FALSE)

  locations <- city_data[["location"]]
  updateSelectizeInput(session, "location", choices = locations, server = TRUE)

  # Initialize fit_mode reactiveVal
  fit_mode <- reactiveVal("Width")
  
  # Observe the toggle_fit button
  observeEvent(input$toggle_fit, {
    if (fit_mode() == "Width") {
      fit_mode("Height")
      updateActionButton(
        session = session,
        inputId = "toggle_fit",
        label = HTML('<img src="fit_w.png" height="40px">')
      )
      addClass("map-container", "fit-height")
      removeClass("map-container", "fit-width")
    } else {
      fit_mode("Width")
      updateActionButton(
        session = session,
        inputId = "toggle_fit",
        label = HTML('<img src="fit_h.png" height="40px">')
      )
      addClass("map-container", "fit-width")
      removeClass("map-container", "fit-height")
    }
    # Trigger the updateSVGSize function to adjust the SVG
    runjs("updateSVGSize();")
  })

  observeEvent(input$show, {
    selected_cities <- city_data[city_data$location %in% input$location, ]

    for (i in 1:nrow(selected_cities)) {
      city <- selected_cities[i, ]
      runjs(sprintf("showCity(%f, %f, %f, '%s', %f, '%s');", 
                    city$point_x, city$point_y, city$radius, city$color, city$font_size, city$location))
    }
  })
  
  observeEvent(input$hide, {
    runjs("hideAnnotations();")
  })
}

shinyApp(ui = ui, server = server)
