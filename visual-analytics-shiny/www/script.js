$(document).on('shiny:inputchanged', function(event) {
  if (event.name === 'season') {
    $('input[name="season"]').each(function() {
      var checkboxValue = $(this).val();
      if ($(this).is(':checked')) {
        $('label:contains(' + checkboxValue + ')').addClass('selected');
      } else {
        $('label:contains(' + checkboxValue + ')').removeClass('selected');
      }
    });
  }
  
  if (event.name === 'episode') {
    $('input[name="episode"]').each(function() {
      var checkboxValue = $(this).val();
      if ($(this).is(':checked')) {
        $('label:contains(' + checkboxValue + ')').addClass('selected');
      } else {
        $('label:contains(' + checkboxValue + ')').removeClass('selected');
      }
    });
  }
});

// Function to update SVG canvas size based on image dimensions
function updateSVGSize() {
  var img = document.getElementById('map-img');
  var svg = document.getElementById('map-canvas');
  if (img.complete) {
    svg.setAttribute('viewBox', `0 0 ${img.naturalWidth} ${img.naturalHeight}`);
  }
} 
// Call updateSVGSize when window resizes
window.addEventListener('resize', updateSVGSize);
// Ensure SVG is synced with the image dimensions on image load
document.getElementById('map-img').addEventListener('load', updateSVGSize);

function showCity(x, y, diameter, color, fontSize, label) {
  // Image dimensions: (2170, 1490)
  
  var svg = document.getElementById('map-canvas');
  var viewBox = svg.viewBox.baseVal;
  
  var newCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  newCircle.setAttribute('cx', x);
  newCircle.setAttribute('cy', y);
  newCircle.setAttribute('r', 1/2 * diameter * Math.min(viewBox.width, viewBox.height));
  newCircle.setAttribute('fill', color);
  svg.appendChild(newCircle);
  
  var newText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  newText.textContent = label;
  newText.setAttribute('x', x + 10);
  newText.setAttribute('y', y - 10);
  newText.setAttribute('font-size', fontSize);
  newText.setAttribute('fill', color);
  newText.setAttribute('class', 'got-font');
  svg.appendChild(newText);
}

function hideAnnotations() {
  var svg = document.getElementById('map-canvas');
  // Remove all circles...
  var circles = svg.getElementsByTagName('circle');
  while (circles.length > 0) {
    circles[0].parentNode.removeChild(circles[0]);
  }
  // ... and text
  var texts = svg.getElementsByTagName('text');
  while (texts.length > 0) {
    texts[0].parentNode.removeChild(texts[0]);
  }
}
