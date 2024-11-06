// Global variabels
const BASE_RADIUS = 5;
const FONT_SIZE = 14;
const LABEL_WIDTH = 100;
const LABEL_HEIGHT = 18;

// Colormap from https://colorbrewer2.org/#type=qualitative&scheme=Pastel1&n=5
const CHARACTER_COLORMAP = ['#fbb4ae','#b3cde3','#ccebc5','#decbe4','#fed9a6'];

const LABEL_BACKGROUND_COLOR = 'hsl(202 100% 11%)';
const LABEL_TEXT_COLOR = 'hsl(202 100% 90%)';

const CIRCLE_COLOR_FULL = 'hsl(246 70% 70%)';
const CIRCLE_COLOR = 'hsla(246 70% 70% / 0.8)'; // Last value is opacity
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

  Shiny.addCustomMessageHandler('show_travel', function(message) {
    showTravel(message.character_id, Number(message.from_x), Number(message.from_y), Number(message.to_x), Number(message.to_y), Number(message.num_travels));
  });

  Shiny.addCustomMessageHandler('show_location_bubble', function(message) {
    showLocation(message.character_id, message.sub_location, Number(message.x_coord), Number(message.y_coord), message.time, message.show_time);
  });

  function showLocation(character_id, label, x, y, time, show_time) {
    var svg = document.getElementById('map-canvas');
    if (!svg) return;
    var newCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    newCircle.setAttribute('cx', x);
    newCircle.setAttribute('cy', y);

    // Calculate the radius of the circle, when the area should be given by the time
    const radius = Math.sqrt(time / Math.PI);

    newCircle.setAttribute('r', show_time ? radius : BASE_RADIUS);
    newCircle.setAttribute('fill', CIRCLE_COLOR);
    // Give the circle a black border
    newCircle.setAttribute('stroke', 'black');
    newCircle.setAttribute('class', `c-${character_id}`);
    svg.appendChild(newCircle);
  }

  Shiny.addCustomMessageHandler('show_location_label', function(message) {
    showLocationLabel(message.character_id, message.sub_location, Number(message.x_coord), Number(message.y_coord), message.time);
  });

  function showLocationLabel(character_id, label, x, y, time) {
    var svg = document.getElementById('map-canvas');
    if (!svg) return;

    // Instead of only showing the label, create a box in which the label is shown
    var newTextBackground = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    newTextBackground.setAttribute('x', x - LABEL_WIDTH/2);
    newTextBackground.setAttribute('y', y - LABEL_HEIGHT/2);
    newTextBackground.setAttribute('width', LABEL_WIDTH);
    newTextBackground.setAttribute('height', LABEL_HEIGHT);
    newTextBackground.setAttribute('fill', LABEL_BACKGROUND_COLOR);
    newTextBackground.setAttribute('class', `got-font c-${character_id}`);
    svg.appendChild(newTextBackground);

    // Create the text element inside the box
    // Dynamically adjust the font size based on the length of the label
    var fontSize = FONT_SIZE;
    var newText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    newText.textContent = label;
    newText.setAttribute('font-size', fontSize);
    newText.setAttribute('x', x);
    newText.setAttribute('y', y);
    newText.setAttribute('text-anchor', 'middle')
    newText.setAttribute('dominant-baseline', 'central');
    newText.setAttribute('fill', LABEL_TEXT_COLOR);
    newText.setAttribute('class', `got-font c-${character_id}`);
    newText.setAttribute('pointer-events', 'visiblePainted');  // Important to enable hover events
    svg.appendChild(newText);
    
    // Adjust the font size dynamically
    let bbox = newText.getBBox();
    const maxWidth = LABEL_WIDTH;
    while (bbox.width > maxWidth && fontSize > 0) {
        fontSize -= 1;  // Decrease font size
        newText.setAttribute('font-size', fontSize);
        bbox = newText.getBBox();  // Update bounding box to check new width
    }

    // Overlay plane creation on click event
    newText.addEventListener('click', function () {
      var overlayPlane = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      overlayPlane.setAttribute('x', '0');
      overlayPlane.setAttribute('y', '0');
      overlayPlane.setAttribute('width', '100%');
      overlayPlane.setAttribute('height', '100%');
      overlayPlane.setAttribute('fill', 'white');
      overlayPlane.setAttribute('opacity', '0.5');
      overlayPlane.setAttribute('class', 'overlay');
      overlayPlane.setAttribute('pointer-events', 'visiblePainted');

      // Add click event to remove highlight
      overlayPlane.addEventListener('click', function () {
        const overlays = document.querySelectorAll('.overlay');
        overlays.forEach(function(overlay) {
          overlay.remove();
        });
      });

      svg.appendChild(overlayPlane);
    });

    // var popup;
    // newText.addEventListener('mouseover', function () {
    //   var rect = newText.getBoundingClientRect();
    //   popup = document.createElement('div');
    //   popup.innerHTML = `<b>${label}</b><p>${character_id}: ${time} seconds</p>`;
    //   popup.style.position = 'absolute';
    //   popup.style.left = `${rect.left}px`;
    //   popup.style.top = `${rect.top - 30}px`;
    //   popup.style.backgroundColor = POPOUT_BACKGROUND_COLOR;
    //   popup.style.color = TEXT_COLOR;
    //   popup.style.padding = '5px';
    //   popup.style.borderRadius = '5px';
    //   popup.style.pointerEvents = 'none';
    //   popup.style.zIndex = 10;
    //   document.body.appendChild(popup);
    // });

    // newText.addEventListener('mouseout', function () {
    //   if (popup) {
    //     document.body.removeChild(popup);
    //     popup = null;
    //   }
    // });
  }

  function showTravel(character_id, from_x, from_y, to_x, to_y, num_travels) {
    var svg = document.getElementById('map-canvas');
    if (!svg) return;

    // Calculate the midpoint coordinates
    const mid_x = (from_x + to_x) / 2;
    const mid_y = (from_y + to_y) / 2;

    // Create the first line segment (from start to midpoint) with an arrow head
    var line1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line1.setAttribute('x1', from_x);
    line1.setAttribute('y1', from_y);
    line1.setAttribute('x2', mid_x);
    line1.setAttribute('y2', mid_y);
    line1.setAttribute('stroke', CIRCLE_COLOR_FULL);
    line1.setAttribute('stroke-width', 2);
    line1.setAttribute('class', `c-${character_id}`);
    line1.setAttribute('marker-end', 'url(#arrow)');  // Attach arrow to the midpoint

    // Create the second line segment (from midpoint to end)
    var line2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line2.setAttribute('x1', mid_x);
    line2.setAttribute('y1', mid_y);
    line2.setAttribute('x2', to_x);
    line2.setAttribute('y2', to_y);
    line2.setAttribute('stroke', CIRCLE_COLOR_FULL);
    line2.setAttribute('stroke-width', 2);
    line2.setAttribute('class', `c-${character_id}`);

    // Define the arrow marker
    var arrow = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    arrow.setAttribute('id', 'arrow');
    arrow.setAttribute('viewBox', '0 0 10 10');
    arrow.setAttribute('refX', '10');  // Adjust as needed for positioning
    arrow.setAttribute('refY', '5');
    arrow.setAttribute('markerWidth', '10');
    arrow.setAttribute('markerHeight', '10');
    arrow.setAttribute('orient', 'auto-start-reverse');

    var arrowPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    arrowPath.setAttribute('d', 'M 0 0 L 10 5 L 0 10 z');
    arrowPath.setAttribute('fill', CIRCLE_COLOR_FULL);
    arrow.appendChild(arrowPath);

    svg.appendChild(arrow);

    // Add the two line segments to the SVG
    svg.appendChild(line1);
    svg.appendChild(line2);
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

  Shiny.addCustomMessageHandler('set_map_opacity', function(message) {
    var imgElement = document.getElementById('map-img');
    if (imgElement) {
      imgElement.style.opacity = message.opacity;
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
