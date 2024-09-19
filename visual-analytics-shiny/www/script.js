document.addEventListener('DOMContentLoaded', function() {
  // Function to update SVG canvas size based on image dimensions
  window.updateSVGSize = function() {
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

  window.showCity = function(x, y, radius, color, fontSize, label) {
    var svg = document.getElementById('map-canvas');
    if (!svg) return;
    var newCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    newCircle.setAttribute('cx', x);
    newCircle.setAttribute('cy', y);
    newCircle.setAttribute('r', radius);
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

  window.hideAnnotations = function() {
    var svg = document.getElementById('map-canvas');
    while (svg && svg.lastChild) {
      svg.removeChild(svg.lastChild);
    }
  }
});
