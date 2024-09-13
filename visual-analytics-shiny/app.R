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
  
  sidebar = div(
    h4("Selected season(s) and episode(s):"),
    verbatimTextOutput("selection_text")
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
       ),
  )
)

server <- function(input, output, session) {
  
  # Draw circle when button is pressed
  observeEvent(input$draw_circle, {
    runjs(sprintf("drawCircle(%f, %f, %f, '#5e35b1');", 
                  input$x_coord, input$y_coord, input$diameter))
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
