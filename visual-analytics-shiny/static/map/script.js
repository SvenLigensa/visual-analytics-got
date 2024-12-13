// Blue, Red, Green (subset of https://colorbrewer2.org/#type=qualitative&scheme=Set1&n=7)
const CHARACTER_COLORMAP = ['#377eb8','#e41a1c','#4daf4a'];
const LABEL_BACKGROUND_COLOR = 'hsl(202 100% 11%)';
const LABEL_TEXT_COLOR = 'hsl(202 100% 90%)';

const FONT_SIZE = 16;
const LABEL_WIDTH = 100;
const LABEL_HEIGHT = 18;
const FOCUS_LEFT_OFFSET = 150;
const FOCUS_HEIGHT = 100;

document.addEventListener('DOMContentLoaded', function() {
  Shiny.addCustomMessageHandler('remove_svg_elements', function(message) {
    const svg = document.getElementById('map-canvas');
    if (!svg) return;
    while (svg.firstChild) {
      svg.removeChild(svg.firstChild);
    }
  });

  Shiny.addCustomMessageHandler('show_legend', function(message) {
    showLegend(message.characters)
  });

  function showLegend(characters) {
    const previous_legend = document.getElementById('legend');
    if (previous_legend) previous_legend.remove()
    if (characters.length === 0) return    

    // Create the div element with the class 'legend'
    const legendDiv = document.createElement('div');
    legendDiv.id = 'legend';

    const legendHeader = document.createElement('p');
    legendHeader.textContent = "Legend";
    legendHeader.classList.add('got-font');
    legendDiv.appendChild(legendHeader);

    for (let i = 0; i < characters.length; i++) {
      const characterName = characters[i];
      const characterColor = CHARACTER_COLORMAP[i];

      const characterElement = document.createElement('p');
      characterElement.textContent = characterName;
      characterElement.style.color = characterColor;
      characterElement.classList.add('got-font');
      characterElement.style.fontSize = '12px';

      legendDiv.appendChild(characterElement);
    }

    const mapCard = document.getElementsByClassName('map-card')[0];
    if (mapCard) {
      mapCard.prepend(legendDiv);
    }
  }

  Shiny.addCustomMessageHandler('show_travel', function(message) {
    showTravel(message.character_num, Number(message.from_x), Number(message.from_y), Number(message.to_x), Number(message.to_y), Number(message.num_travels));
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

  function showTravel(color_num, from_x, from_y, to_x, to_y, num_travels) {
    const svg = document.getElementById('map-canvas');
    if (!svg) return;

    // Get the color for the character
    const color = CHARACTER_COLORMAP[color_num];

    // Calculate the midpoint coordinates
    const mid_x = (from_x + to_x) / 2;
    const mid_y = (from_y + to_y) / 2;

    // Define a unique marker id for each character
    const markerId = `arrow-${color_num}`;

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
    showLocationBubble(message.character_num, Number(message.x_coord), Number(message.y_coord), message.time);
  });

  function showLocationBubble(color_num, x, y, time) {

    color = CHARACTER_COLORMAP[color_num % 3];

    var svg = document.getElementById('map-canvas');
    if (!svg) return;
    var newCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    newCircle.setAttribute('cx', x);
    newCircle.setAttribute('cy', y);

    // Calculate the radius of the circle, when the area should be given by the time
    const radius = Math.sqrt(time / Math.PI);

    newCircle.setAttribute('r', radius);
    newCircle.setAttribute('fill', color);
    newCircle.setAttribute('stroke', 'black');
    newCircle.setAttribute('class', `x-${x}_y-${y}`);
    svg.appendChild(newCircle);
  }

  Shiny.addCustomMessageHandler('show_location_label', function(message) {
    showLocationLabel(message.sub_location, Number(message.x_coord), Number(message.y_coord), message.character_nums, message.character_times);
  });

  function showLocationLabel(label, x, y, character_nums, character_times) {
    var svg = document.getElementById('map-canvas');
    if (!svg) return;

    // Instead of only showing the label, create a box in which the label is shown
    var newTextBackground = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    newTextBackground.setAttribute('x', x - LABEL_WIDTH/2);
    newTextBackground.setAttribute('y', y - LABEL_HEIGHT/2);
    newTextBackground.setAttribute('width', LABEL_WIDTH);
    newTextBackground.setAttribute('height', LABEL_HEIGHT);
    newTextBackground.setAttribute('fill', LABEL_BACKGROUND_COLOR);
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
    newText.setAttribute('class', `got-font`);
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
      const overlayPlane = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      overlayPlane.setAttribute('x', '0');
      overlayPlane.setAttribute('y', '0');
      overlayPlane.setAttribute('width', '100%');
      overlayPlane.setAttribute('height', '100%');
      overlayPlane.setAttribute('fill', 'white');
      overlayPlane.setAttribute('opacity', '0.7');
      overlayPlane.setAttribute('class', 'overlay');
      overlayPlane.setAttribute('pointer-events', 'visiblePainted');
      svg.appendChild(overlayPlane);

      // Instead of only showing the label, create a box in which the label is shown
      var newTextBackground2 = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      newTextBackground2.setAttribute('x', x - FOCUS_LEFT_OFFSET - (LABEL_WIDTH/2));
      newTextBackground2.setAttribute('y', y - (FOCUS_HEIGHT/2) - LABEL_HEIGHT);
      newTextBackground2.setAttribute('width', LABEL_WIDTH);
      newTextBackground2.setAttribute('height', LABEL_HEIGHT);
      newTextBackground2.setAttribute('fill', LABEL_BACKGROUND_COLOR);
      newTextBackground2.setAttribute('class', `overlay x-${x}_y-${y}`);
      svg.appendChild(newTextBackground2);

      var fontSize = FONT_SIZE;
      var newText2 = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      newText2.textContent = label;
      newText2.setAttribute('font-size', fontSize);
      newText2.setAttribute('x', x - FOCUS_LEFT_OFFSET);
      newText2.setAttribute('y', y - FOCUS_HEIGHT/2 - LABEL_HEIGHT/2);
      newText2.setAttribute('text-anchor', 'middle');
      newText2.setAttribute('dominant-baseline', 'central');
      newText2.setAttribute('fill', LABEL_TEXT_COLOR);
      newText2.setAttribute('class', `overlay got-font x-${x}_y-${y}`);
      newText2.setAttribute('pointer-events', 'none');
      svg.appendChild(newText2);
      
      // Adjust the font size dynamically
      let bbox = newText2.getBBox();
      const maxWidth = LABEL_WIDTH;
      while (bbox.width > maxWidth && fontSize > 0) {
          fontSize -= 1;
          newText2.setAttribute('font-size', fontSize);
          bbox = newText2.getBBox();
      }

      var numberTextBackground = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      numberTextBackground.setAttribute('x', x - FOCUS_LEFT_OFFSET - (LABEL_WIDTH/2));
      numberTextBackground.setAttribute('y', y - (FOCUS_HEIGHT/2));
      numberTextBackground.setAttribute('width', FOCUS_HEIGHT);
      numberTextBackground.setAttribute('height', FOCUS_HEIGHT);
      numberTextBackground.setAttribute('fill', LABEL_BACKGROUND_COLOR);
      numberTextBackground.setAttribute('class', `overlay x-${x}_y-${y}`);
      svg.appendChild(numberTextBackground);

      for (let i = 0; i < character_times.length; i++) {
        var numberText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        numberText.textContent = character_times[i];
        numberText.setAttribute('font-size', 20);
        numberText.setAttribute('x', x - FOCUS_LEFT_OFFSET);
        numberText.setAttribute('y', y - 30 + (i * 30));
        numberText.setAttribute('text-anchor', 'middle');
        numberText.setAttribute('dominant-baseline', 'central');
        numberText.setAttribute('fill', CHARACTER_COLORMAP[character_nums[i]]);
        numberText.setAttribute('class', `overlay got-font x-${x}_y-${y}`);
        numberText.setAttribute('pointer-events', 'none');
        svg.appendChild(numberText);
      }

      const svgElements = document.querySelectorAll(`.x-${x}_y-${y}`);
      svgElements.forEach(svgElement => {
        const clone = svgElement.cloneNode(true);
        clone.classList.add("overlay");
        svg.appendChild(clone);

        clone.addEventListener('click', function () {
          const overlays = document.querySelectorAll('.overlay');
          overlays.forEach(overlay => {
            overlay.remove();
          });
        });
      });

      overlayPlane.addEventListener('click', function () {
        const overlays = document.querySelectorAll('.overlay');
        overlays.forEach(overlay => {
          overlay.remove();
        });
      });
    });
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
