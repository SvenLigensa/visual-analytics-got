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
      card_header("Selected season(s) and episode(s):"),
      verbatimTextOutput("selection_text")
    ),
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

  city_data <- read.csv("city_data.csv", stringsAsFactors = FALSE)

  locations <- city_data[["location"]]
  updateSelectizeInput(session, "location", choices = locations, server = TRUE)

  observeEvent(input$show, {
    selected_cities <- city_data[city_data$location %in% input$location, ]
    
    # Loop through the filtered city_data and run the JavaScript code only for selected cities
    for (i in 1:nrow(selected_cities)) {
      city <- selected_cities[i, ]
      runjs(sprintf("showCity(%f, %f, %f, '%s', %f, '%s');", 
                    city$point_x, city$point_y, city$diameter, city$color, city$font_size, city$location))
    }
  })
  
  observeEvent(input$hide, {
    runjs("hideAnnotations();")
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
