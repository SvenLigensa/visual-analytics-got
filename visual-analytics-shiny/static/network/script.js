const IMG_SIZE = 40;
const IMG_PADDING = IMG_SIZE * 2/3;
const LINK_DISTANCE = 50;

const DUMMY_COLOR = "#4a4e69";
const LINK_COLORS = {
  "parent": "#264653",
  "siblings": "#F4A261",
  "killed": "#E76F51",
  "serves": "#E9C46A",
  "married": "#2A9D8F",
  "allies": "#E9C46A",
  "guardianOf": "#22333b",
};

document.addEventListener('DOMContentLoaded', function() {

  Shiny.addCustomMessageHandler('show_network', function(message) {
    nodes = message.nodes;
    links = message.links;
    showNetwork(nodes, links);
  });

  function updateSVGSize() {
    const svg = d3.select('#network-canvas');
    const container = document.querySelector('.full-size-div');
    if (!container) return;
    const rect = container.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    svg
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .style('width', '100%')
      .style('height', '100%');

    return { width, height };
  }

  function showNetwork(nodes, links) {
    const svg = d3.select('#network-canvas');
    svg.selectAll("*").remove();
    const dimensions = updateSVGSize();

    // Add a container group for zoom
    const g = svg.append("g")
        .attr("class", "zoom-container");

    // Add zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.2, 4])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
        });

    svg.call(zoom);

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(LINK_DISTANCE))
      .force("charge", d3.forceManyBody().strength(-IMG_PADDING * 2))
      .force("collision", d3.forceCollide().radius(IMG_PADDING))
      .force("x", d3.forceX().strength(0.0005))
      .force("y", d3.forceY().strength(0.0005))
      .force("center", d3.forceCenter(dimensions.width / 2, dimensions.height / 2));
  
    window.addEventListener('resize', () => {
      const dimensions = updateSVGSize();
      simulation.force("center", d3.forceCenter(dimensions.width / 2, dimensions.height / 2));
      simulation.alpha(0.05).restart();
    });

    // Create arrow markers
    svg.append("defs")
      .selectAll("marker")
      .data(links.filter(d => ["killed", "serves", "parent", "guardianOf"].includes(d.category)))
      .join("marker")
      .attr("id", d => `arrowhead-${d.source.id.replace(/\s+/g, '')}-${d.target.id.replace(/\s+/g, '')}-${d.category}`)
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", d => d.source === d.target ? 12 : 20)
      .attr("refY", 0)
      .attr("orient", "auto")
      .attr("markerWidth", 10)
      .attr("markerHeight", 10)
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", d => LINK_COLORS[d.category]);

    const link = g.append("g")
      .selectAll("path")
      .attr("class", "link")
      .data(links)
      .join("path")
      .style("stroke", d => LINK_COLORS[d.category])
      .style("stroke-width", 2)
      .style("fill", "none")
      .attr("marker-end", d => ["killed", "serves", "parent", "guardianOf"].includes(d.category) ? 
        `url(#arrowhead-${d.source.id.replace(/\s+/g, '')}-${d.target.id.replace(/\s+/g, '')}-${d.category})` : 
        null);

    // Add titles for nodes
    link.append("title")
      .text(d => {
        const relationshipType = d.category.charAt(0).toUpperCase() + d.category.slice(1);
        const arrow = ["killed", "serves", "parent", "guardianOf"].includes(d.category) ? "→" : "↔";
        return `${relationshipType}: ${d.source.id} ${arrow} ${d.target.id}`;
      });

    const node = g.append("g")
      .selectAll("g")
      .data(nodes)
      .join("g");

    // Add drag behavior to the groups
    node.call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));

    // Update the tick function to move the groups
    simulation.on("tick", () => {
      link.attr("d", d => {
        // Handle self-referential links
        if (d.source === d.target) {
          const x = d.source.x;
          const y = d.source.y;
          const size = IMG_SIZE + 10;
          return `M ${x},${y} 
                  C ${x + size},${y - size}
                    ${x + size},${y + size}
                    ${x + 15},${y}`;
        }
        // Normal straight line for different nodes
        return `M ${d.source.x},${d.source.y} L ${d.target.x},${d.target.y}`;
      });

      node.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    // Check if the image is available
    // By making a request to the image URL
    // And checking if we get 404 error
    const image_available = (url) => {
      return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(true);
        img.onerror = () => resolve(false);
        img.src = url;
      });
    };

    // First create all nodes that don't have images
    node.filter(d => !d.characterImageThumb)
      .append("circle")
      .attr("r", 8)
      .attr("fill", DUMMY_COLOR);

    // Then handle nodes with potential images
    node.filter(d => d.characterImageThumb).each(function(d) {
      const element = d3.select(this);
      image_available(d.characterImageThumb).then(available => {
        if (available) {
          element.append("image")
            .attr("xlink:href", d.characterImageThumb)
            .attr("width", IMG_SIZE)
            .attr("height", IMG_SIZE)
            .attr("x", -IMG_SIZE / 2)
            .attr("y", -IMG_SIZE / 2);
        } else {
          element.append("circle")
            .attr("r", 8)
            .attr("fill", DUMMY_COLOR);
        }
      });
    });

    // Add titles for nodes
    node.append("title")
      .text(d => d.id);

    // Add click handler to nodes
    node.on("click", function(event, d) {
      // Prevent click from triggering drag
      event.stopPropagation();
      
      // Send message to Shiny with clicked node's id
      Shiny.setInputValue("network_node_click", d.id);
    });

    // Drag functions
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }
    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  }
});
