library(shiny)
library(shinyjs)
library(bslib)

ui <- page_sidebar(
  titlePanel("Game of Thrones Analyzer"),
  useShinyjs(),

  # Links to external CSS and JS code
  tags$head(
    tags$link(rel = "stylesheet", type = "text/css", href = "styles.css"),
    tags$script(src = "script.js")  # Link to the external JS file
  ),
  
  layout_column_wrap(
    width = 1/2,
    heights_equal = "row",
    
    card(
      div(id = "map-container",
        tags$img(id = "map-img", src = "westeros.jpg"),
        tags$svg(id = "map-canvas"),
      )
    ),
    
    card(
      card_header("Dummy Card"),
      numericInput("x_coord", "X Coordinate", value = 0, min = 0, max = 1),
      numericInput("y_coord", "Y Coordinate", value = 0, min = 0, max = 1),
      numericInput("diameter", "Circle Diameter", value = 0.1, min = 0, max = 1),
      actionButton("draw_circle", "Draw Circle"),

      card_footer("Graphic coming soon...")
    )
  ),
  
  card(id = "bottom-card",
    div(class = "full-horizontal-choices",
        checkboxGroupInput(
          inputId = "season",
          label = "Select seasons and episodes of interest:",
          choices = c("Season 1", "Season 2", "Season 3", "Season 4", 
                      "Season 5", "Season 6", "Season 7", "Season 8"),
          inline = TRUE,
        ),
        # Placeholder for dynamically generated episode choices
        uiOutput("episode_ui"),
    ),
  )
)

server <- function(input, output, session) {

  # Draw circle when button is pressed
  observeEvent(input$draw_circle, {
    runjs(sprintf("drawCircle(%f, %f, %f, '#5e35b1');", 
                  input$x_coord, input$y_coord, input$diameter))
  })
  
  # Dynamically show episode checkboxGroupInput based on selected season
  observeEvent(input$season, {
    # If exactly one season is selected, show episode choices
    if (!is.null(input$season) && length(input$season) == 1) {
      output$episode_ui <- renderUI({
        div(class = "full-horizontal-choices",
            checkboxGroupInput(
              inputId = "episode",
              label = NULL,
              choices = paste0("Episode ", 1:10),  # Episodes 1-10
              inline = TRUE
            )
        )
      })
    } else {
      # If no season or multiple seasons are selected, hide the episode choices
      output$episode_ui <- renderUI({
        NULL
      })
    }
  })

}

shinyApp(ui = ui, server = server)
