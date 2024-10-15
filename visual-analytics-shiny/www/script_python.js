document.addEventListener('DOMContentLoaded', function() {
  // Function to update SVG canvas size based on image dimensions
  function updateSVGSize() {
    var img = document.getElementById('map-img');
    var svg = document.getElementById('map-canvas');
    if (img && svg && img.naturalWidth && img.naturalHeight) {
      svg.setAttribute('viewBox', `0 0 ${img.naturalWidth} ${img.naturalHeight}`);
      svg.style.width = img.offsetWidth + 'px';
      svg.style.height = img.offsetHeight + 'px';
    }
  }

  var img = document.getElementById('map-img');
  if (img) {
    img.addEventListener('load', updateSVGSize);
    updateSVGSize();
  }
  window.addEventListener('resize', updateSVGSize);

  // Function to show a city annotation on the SVG map
  function showCity(x, y, label) {
    var svg = document.getElementById('map-canvas');
    if (!svg) return;
    var newCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    newCircle.setAttribute('cx', x);
    newCircle.setAttribute('cy', y);
    newCircle.setAttribute('r', 8);
    newCircle.setAttribute('fill', '#f5f5f5');
    svg.appendChild(newCircle);
    var newText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    newText.textContent = label;
    newText.setAttribute('x', x + 10);
    newText.setAttribute('y', y - 10);
    newText.setAttribute('font-size', '20');
    newText.setAttribute('fill', '#f5f5f5');
    newText.setAttribute('class', 'got-font');
    svg.appendChild(newText);
  }

  // Function to remove all annotations from the SVG map
  function removeAnnotations() {
    var svg = document.getElementById('map-canvas');
    while (svg && svg.lastChild) {
      svg.removeChild(svg.lastChild);
    }
  }

  // Custom message handler for showing cities
  Shiny.addCustomMessageHandler('show_city', function(message) {
    console.log(message);
    var x = message.x_coord;
    var y = message.y_coord;
    var location = message.location;
    showCity(x, y, location);
  });

  // Custom message handler for hiding annotations
  Shiny.addCustomMessageHandler('remove_annotations', function(message) {
    removeAnnotations();
  });

  // Custom message handler for toggling fit mode
  Shiny.addCustomMessageHandler('toggle_fit', function(message) {
    var fitMode = message.fit_mode;
    var buttonImg = message.button_img;
    var imgElement = document.getElementById('map-img');
    var buttonElement = document.getElementById('toggle_fit');

    if (imgElement) {
      if (fitMode === 'Height') {
        imgElement.style.width = 'auto';
        imgElement.style.height = '100%';
      } else {
        imgElement.style.width = '100%';
        imgElement.style.height = 'auto';
      }
      updateSVGSize();
    }

    if (buttonElement) {
      buttonElement.innerHTML = '<img src="' + buttonImg + '" height="30px">';
    }
  });
});
