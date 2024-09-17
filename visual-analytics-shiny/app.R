library(shiny)
library(shinyjs)
library(bslib)

ui <- page_sidebar(
  useShinyjs(),

  # Links to external CSS and JS code
  tags$head(
    tags$link(rel = "stylesheet", type = "text/css", href = "styles.css"),
    tags$script(src = "script.js")  # Link to the external JS file
  ),

  tags$div(
    class = "got-font",
    tags$h1("Game of Thrones Analyzer")
  ),

  sidebar = div(
    card(
      card_header("Interact with Map"),
      # numericInput("x_coord", "X Coordinate", value = 0, min = 0, max = 1),
      # numericInput("y_coord", "Y Coordinate", value = 0, min = 0, max = 1),
      # numericInput("diameter", "Circle Diameter", value = 0.1, min = 0, max = 1),
      actionButton("draw_circle", label = tagList("Draw Circle on ", em("Pentos")))
    ),
    card(
      card_header("Selected season(s) and episode(s):"),
      verbatimTextOutput("selection_text")
    )
  ),
  
  card(
    div(id = "map-container",
        tags$img(id = "map-img", src = "map_annotated.png"),
        tags$svg(id = "map-canvas"),
    )
  ),
  
  div(class = "full-horizontal-choices",
    checkboxGroupInput(
      inputId = "season",
      label = "Select seasons and episodes of interest:",
      choices = c("Season 1", "Season 2", "Season 3", "Season 4", 
                  "Season 5", "Season 6", "Season 7", "Season 8"),
      inline = TRUE,
    ),
    # Episode selection is always present but initially hidden
    div(
      id = "episode_selection",
      style = "display: none;",  # Hide it initially
      div(class = "full-horizontal-choices",
        checkboxGroupInput(
          inputId = "episode",
          label = NULL,
          choices = paste0("Episode ", 1:10),  # Episodes 1-10
          inline = TRUE
        )
      )
    )
  )
)

server <- function(input, output, session) {
  
  # Draw circle when button is pressed
  observeEvent(input$draw_circle, {
    # Image (2170, 1490)
    # Pentos (910, 816)
    runjs("drawCircle(910/2170, 861/1490, 0.01, '#67331e');")
  })
  
  # Show/hide episode selection based on selected season(s)
  observeEvent(input$season, ignoreNULL = FALSE, {
    if (!is.null(input$season) && length(input$season) == 1) {
      shinyjs::show(id = "episode_selection")
    } else {
      shinyjs::hide(id = "episode_selection")
      # Reset input$episode to NULL
      updateCheckboxGroupInput(session, "episode", selected = character(0))
    }
  })
  
  output$selection_text <- renderText({
    seasons <- input$season
    episodes <- input$episode
    
    if (is.null(seasons) || length(seasons) == 0) {
      season_text <- "None"
    } else {
      # Extract numbers from seasons
      season_nums <- gsub("Season ", "", seasons)
      season_text <- paste(season_nums, collapse = ", ")
    }
    
    if (is.null(episodes) || length(episodes) == 0) {
      episode_text <- "None"
    } else {
      # Extract numbers from episodes
      episode_nums <- gsub("Episode ", "", episodes)
      episode_text <- paste(episode_nums, collapse = ", ")
    }
    
    paste("Seasons:", season_text, "\nEpisodes:", episode_text)
  })
}

shinyApp(ui = ui, server = server)
