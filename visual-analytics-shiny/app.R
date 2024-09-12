library(shiny)
library(bslib)

# Define UI
ui <- page_sidebar(
  titlePanel("Game of Thrones Analyzer"),
  
  # Updated CSS to align checkboxes horizontally and center text
  tags$head(
    tags$style(HTML("
      /* The image spans the whole height of the screen (with some fixed padding) */
      .full-screen-img {
        height: calc(100vh - 100px);
        object-fit: contain;
        display: block;
        margin-left: auto;
        margin-right: auto;
      }
      /* The checkboxes span the whole width and are aligned horizontally */
      .season-choices .shiny-options-group {
        width: 100%;
        display: flex;
        flex-wrap: nowrap;
        gap: 0; /* Ensure no gap between buttons */
      }
      /* Hide the default checkbox input */
      .season-choices .shiny-options-group input[type='checkbox'] {
        display: none;
      }
      .season-choices .shiny-options-group label {
          display: flex !important;
          align-items: center;
          justify-content: center;
          min-width: min-content;  /* Don't shrink below the width of the text */
          border: 1px solid #2b2b2b;
          background-color: #e8eaf6;
          padding: 0 !important; /* Remove the padding in front of the text to be able to center it properly */
          font-family: sans-serif; /* Todo: https://fontmeme.com/fonts/game-of-thrones-font/ */
          width: 100%;
          height: 30px;
          white-space: nowrap;
          cursor: pointer;
          margin: 0;
          border-left: none;
          border-right: none;
      }
      .season-choices .shiny-options-group label:first-child {
          border-left: 1px solid #2b2b2b;
      }
      .season-choices .shiny-options-group label:last-child {
          border-right: 1px solid #2b2b2b;
      }
      /* Color of button gets darker on hover */
      .season-choices .shiny-options-group label:hover {
        background-color: #9fa8da;
      }
      /* Color of button gets darker when selected */
      .season-choices .shiny-options-group label.selected {
        background-color: #9fa8da;
      }
    "))
  ),
  
  # JavaScript to dynamically toggle the "selected" class based on checkbox value
  tags$script(HTML("
    $(document).on('shiny:inputchanged', function(event) {
      if (event.name === 'season') {
        $('input[name=\"season\"]').each(function() {
          var checkboxValue = $(this).val();
          if ($(this).is(':checked')) {
            // console.log('Checkbox with value:', checkboxValue, 'checked, adding selected class');
            $('label:contains(' + checkboxValue + ')').addClass('selected');
          } else {
            // console.log('Checkbox with value:', checkboxValue, 'unchecked, removing selected class');
            $('label:contains(' + checkboxValue + ')').removeClass('selected');
          }
        });
      }
    });
  ")),
  
  # Display the JPG image with the new class for full-screen height
  sidebar = sidebar(
    tags$img(src = "westeros.jpg", class = "full-screen-img")
  ),
  
  card(
    # card_header(""),
    div(class = "season-choices",
        checkboxGroupInput(
          inputId = "season",
          label = "Select season and episode:",
          choices = c("Season 1", "Season 2", "Season 3", "Season 4", 
                      "Season 5", "Season 6", "Season 7", "Season 8"),
          inline = TRUE,
        )
    ),
    textOutput("selected_seasons"),
    card_footer("Interactive App by Sven Ligensa"),
  )
)
# Define server logic
server <- function(input, output, session) {
  
  # Render the selected checkboxes as text
  # output$selected_seasons <- renderText({
  #   selected <- input$season
  #   if (length(selected) > 0) {
  #     paste("You have selected:", paste(selected, collapse = ", "))
  #   } else {
  #     "No season selected."
  #   }
  # })

}

# Run the application 
shinyApp(ui = ui, server = server)
