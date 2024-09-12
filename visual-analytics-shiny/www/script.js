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

// Draw circle based on the resized image dimensions
function drawCircle(x, y, diameter, color) {
  var svg = document.getElementById('map-canvas');
  var viewBox = svg.viewBox.baseVal;
  var newCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  newCircle.setAttribute('cx', x * viewBox.width);
  newCircle.setAttribute('cy', y * viewBox.height);
  newCircle.setAttribute('r', 1/2 * diameter * Math.min(viewBox.width, viewBox.height));
  newCircle.setAttribute('fill', color);
  svg.appendChild(newCircle);
}
