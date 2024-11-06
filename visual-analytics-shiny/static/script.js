// Global variabels
const BASE_RADIUS = 5;
const FONT_SIZE = 14;
const LABEL_WIDTH = 100;
const LABEL_HEIGHT = 18;

// Colormap from https://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=3
const CHARACTER_COLORMAP = ['#1b9e77','#d95f02','#7570b3'];

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
    while (svg.firstChild) {
      svg.removeChild(svg.firstChild);
    }
  });

  Shiny.addCustomMessageHandler('show_travel', function(message) {
    showTravel(message.character_id, Number(message.from_x), Number(message.from_y), Number(message.to_x), Number(message.to_y), Number(message.num_travels));
  });

// Helper function to create SVG elements with attributes
function createSvgElement(tag, attrs, children = []) {
  const elem = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const [key, value] of Object.entries(attrs)) {
    elem.setAttribute(key, value);
  }
  children.forEach(child => elem.appendChild(child));
  return elem;
}

function showTravel(character_id, from_x, from_y, to_x, to_y, num_travels) {
  const svg = document.getElementById('map-canvas');
  if (!svg) return;

  // Get the color for the character
  const color = CHARACTER_COLORMAP[character_id];
  console.log(character_id, color);

  // Calculate the midpoint coordinates
  const mid_x = (from_x + to_x) / 2;
  const mid_y = (from_y + to_y) / 2;

  // Define a unique marker id for each character
  const markerId = `arrow-${character_id}`;

  // Check if the marker for this character already exists
  if (!document.getElementById(markerId)) {
    const arrowPath = createSvgElement('path', {
      d: 'M 0 0 L 10 5 L 0 10 z',
      fill: color,
    });

    const arrowMarker = createSvgElement('marker', {
      id: markerId,
      viewBox: '0 0 10 10',
      refX: '10',
      refY: '5',
      markerWidth: '10',
      markerHeight: '10',
      orient: 'auto-start-reverse',
      class: `x-${to_x}_y-${to_y} x-${from_x}_y-${from_y}`,
    }, [arrowPath]);

    svg.appendChild(arrowMarker);
  }

  const lineAttrs = {
    stroke: color,
    'stroke-width': 2 * num_travels,
    class: `x-${to_x}_y-${to_y} x-${from_x}_y-${from_y}`,
  };

  const line1 = createSvgElement('line', {
    ...lineAttrs,
    x1: from_x,
    y1: from_y,
    x2: mid_x,
    y2: mid_y,
    'marker-end': `url(#${markerId})`,
  });

  const line2 = createSvgElement('line', {
    ...lineAttrs,
    x1: mid_x,
    y1: mid_y,
    x2: to_x,
    y2: to_y,
  });

  svg.appendChild(line1);
  svg.appendChild(line2);
}

  Shiny.addCustomMessageHandler('show_location_bubble', function(message) {
    showLocation(message.character_id, message.sub_location, Number(message.x_coord), Number(message.y_coord), message.time, message.show_time);
  });

  function showLocation(character_id, label, x, y, time, show_time) {

    color = CHARACTER_COLORMAP[character_id % 3];

    var svg = document.getElementById('map-canvas');
    if (!svg) return;
    var newCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    newCircle.setAttribute('cx', x);
    newCircle.setAttribute('cy', y);

    // Calculate the radius of the circle, when the area should be given by the time
    const radius = Math.sqrt(time / Math.PI);

    newCircle.setAttribute('r', show_time ? radius : BASE_RADIUS);
    newCircle.setAttribute('fill', color);
    // Give the circle a black border
    newCircle.setAttribute('stroke', 'black');
    newCircle.setAttribute('class', `x-${x}_y-${y}`);
    svg.appendChild(newCircle);
  }

  Shiny.addCustomMessageHandler('show_location_label', function(message) {
    showLocationLabel(message.sub_location, Number(message.x_coord), Number(message.y_coord));
  });

  function showLocationLabel(label, x, y) {
    var svg = document.getElementById('map-canvas');
    if (!svg) return;

    // Instead of only showing the label, create a box in which the label is shown
    var newTextBackground = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    newTextBackground.setAttribute('x', x - LABEL_WIDTH/2);
    newTextBackground.setAttribute('y', y - LABEL_HEIGHT/2);
    newTextBackground.setAttribute('width', LABEL_WIDTH);
    newTextBackground.setAttribute('height', LABEL_HEIGHT);
    newTextBackground.setAttribute('fill', LABEL_BACKGROUND_COLOR);
    newTextBackground.setAttribute('class', `x-${x}_y-${y}`);
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
    newText.setAttribute('class', `got-font x-${x}_y-${y}`);
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

    newText.addEventListener('click', function () {
      var overlayPlane = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      overlayPlane.setAttribute('x', '0');
      overlayPlane.setAttribute('y', '0');
      overlayPlane.setAttribute('width', '100%');
      overlayPlane.setAttribute('height', '100%');
      overlayPlane.setAttribute('fill', 'white');
      overlayPlane.setAttribute('opacity', '0.7');
      overlayPlane.setAttribute('class', 'overlay');
      overlayPlane.setAttribute('pointer-events', 'visiblePainted');
      svg.appendChild(overlayPlane);

      const svgElements = document.querySelectorAll(`.x-${x}_y-${y}`);
      svgElements.forEach(svgElement => {
        const clone = svgElement.cloneNode(true);
        clone.classList.add("overlay");
        svg.appendChild(clone);

        clone.addEventListener('click', function () {
          const overlays = document.querySelectorAll('.overlay');
          overlays.forEach(function(overlay) {
            overlay.remove();
          });
        });
      });

      overlayPlane.addEventListener('click', function () {
        const overlays = document.querySelectorAll('.overlay');
        overlays.forEach(function(overlay) {
          overlay.remove();
        });
      });
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
