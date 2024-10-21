// Global variabels
const BASE_RADIUS = 5;
const FONT_SIZE = 10;

const CIRCLE_COLOR = 'hsla(246 70% 70% / 0.5)'; // 50% opacity
const POPOUT_BACKGROUND_COLOR = 'hsl(246 70% 70%)';
const TEXT_COLOR = 'hsl(360 0% 94%)';

document.addEventListener('DOMContentLoaded', function() {
  Shiny.addCustomMessageHandler('remove_svg_elements', function(message) {
    const svg = document.getElementById('map-canvas');
    if (!svg) return;
    var elements = null;
    if (message.type == 'circle') {
      elements = document.getElementsByTagName('circle');
    }
    if (message.type == 'line') {
      elements = document.getElementsByTagName('line');
    }
    if (message.type.startsWith('c-')) {
      elements = document.getElementsByClassName(message.type);
    }
    while (elements.length > 0) {
      svg.removeChild(elements[0]);
    }
  });

  Shiny.addCustomMessageHandler('show_location', function(message) {
    showLocation(message.character_id, message.sub_location, Number(message.x_coord), Number(message.y_coord), message.time, message.show_time);
  });

  Shiny.addCustomMessageHandler('show_travel', function(message) {
    showTravel(message.character_id, Number(message.from_x), Number(message.from_y), Number(message.to_x), Number(message.to_y), Number(message.num_travels));
  });

  function showLocation(character_id, label, x, y, time, show_time) {
    var svg = document.getElementById('map-canvas');
    if (!svg) return;
    var newCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    newCircle.setAttribute('cx', x);
    newCircle.setAttribute('cy', y);
    newCircle.setAttribute('r', show_time ? time/100: BASE_RADIUS);
    newCircle.setAttribute('fill', CIRCLE_COLOR);
    newCircle.setAttribute('class', `c-${character_id}`);
    svg.appendChild(newCircle);
  
    var newText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    newText.textContent = label;
    newText.setAttribute('font-size', FONT_SIZE);
    newText.setAttribute('x', x);
    newText.setAttribute('y', y);
    newText.setAttribute('text-anchor', 'middle')
    newText.setAttribute('dominant-baseline', 'central');
    newText.setAttribute('fill', TEXT_COLOR);
    newText.setAttribute('class', `got-font c-${character_id}`);
    newText.setAttribute('pointer-events', 'visiblePainted');  // Important to enable hover events
    svg.appendChild(newText);

    var popup;
    newText.addEventListener('mouseover', function () {
      var rect = newText.getBoundingClientRect();
      popup = document.createElement('div');
      popup.innerHTML = `<b>${label}</b><p>${character_id}: ${time} seconds</p>`;
      popup.style.position = 'absolute';
      popup.style.left = `${rect.left}px`;
      popup.style.top = `${rect.top - 30}px`;
      popup.style.backgroundColor = POPOUT_BACKGROUND_COLOR;
      popup.style.color = TEXT_COLOR;
      popup.style.padding = '5px';
      popup.style.borderRadius = '5px';
      popup.style.pointerEvents = 'none';
      popup.style.zIndex = 10;
      document.body.appendChild(popup);
    });

    newText.addEventListener('mouseout', function () {
      if (popup) {
        document.body.removeChild(popup);
        popup = null;
      }
    });
  }

  function showTravel(character_id, from_x, from_y, to_x, to_y, num_travels) {
    var svg = document.getElementById('map-canvas');
    if (!svg) return;
    var newLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    newLine.setAttribute('x1', from_x);
    newLine.setAttribute('y1', from_y);
    newLine.setAttribute('x2', to_x);
    newLine.setAttribute('y2', to_y);
    newLine.setAttribute('stroke', CIRCLE_COLOR);
    newLine.setAttribute('stroke-width', num_travels);
    newLine.setAttribute('class', `c-${character_id}`);
    svg.appendChild(newLine);
  }

  // Set the zoom of the map-container and map-img by setting the width of both to the desired value
  Shiny.addCustomMessageHandler('set_zoom', function(message) {
    var imgElement = document.getElementById('map-img');
    if (imgElement) {
      imgElement.style.width = '100%';
      imgElement.style.height = 'auto';
      updateSVGSize();
    }
    var mapContainerElement = document.getElementById('map-container');
    if (mapContainerElement) {
      mapContainerElement.style.width = message.zoom + '%';
      mapContainerElement.style.height = 'auto';
      updateSVGSize();
    }
  });

  // Custom message handler for toggling fit mode
  Shiny.addCustomMessageHandler('toggle_fit', function(message) {
    var fitMode = message.fit_mode;
    var imgElement = document.getElementById('map-img');

    if (imgElement) {
      if (fitMode === 'h') {
        imgElement.style.width = 'auto';
        imgElement.style.height = '100%';
      } else {
        imgElement.style.width = '100%';
        imgElement.style.height = 'auto';
      }
      updateSVGSize();
    }
  });

  // Update SVG canvas size based on image dimensions
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
});
