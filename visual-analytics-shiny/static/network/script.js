document.addEventListener('DOMContentLoaded', function() {

  Shiny.addCustomMessageHandler('show_network', function(message) {
    nodes = message.nodes;
    links = message.links;
    showNetwork(nodes, links);
  });

  function updateSVGSize() {
    const svg = d3.select('#network-canvas');
    const container = document.querySelector('.network-card');
    if (!container) return;
    
    // Get the actual dimensions of the container
    const rect = container.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    
    svg
      .attr('width', width)
      .attr('height', height)
      // Add viewBox to ensure proper scaling
      .attr('viewBox', `0 0 ${width} ${height}`)
      // Ensure SVG fills container
      .style('width', '100%')
      .style('height', '100%');

    return { width, height };
  }

  // TODO: Add colors for each category
  function getLinkColor(category) {
    switch (category) {
      case "killed":
        return "red";
      case "siblings":
        return "blue";
      default:
        return "#999"; // default color
    }
  }

  function showNetwork(nodes, links) {
    const dimensions = updateSVGSize();
    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(30))
      .force("charge", d3.forceManyBody().strength(-40))
      .force("collision", d3.forceCollide().radius(20))
      .force("x", d3.forceX().strength(0.0005))
      .force("y", d3.forceY().strength(0.0005))
      .force("center", d3.forceCenter(dimensions.width / 2, dimensions.height / 2));
  
    window.addEventListener('resize', () => {
      const dimensions = updateSVGSize();
      simulation.force("center", d3.forceCenter(dimensions.width / 2, dimensions.height / 2));
      simulation.alpha(0.05).restart();
    });

    const svg = d3.select('#network-canvas');
    svg.selectAll("*").remove();

    // Create arrow markers
    svg.append("defs")
    .selectAll("marker")
    .data(links)
    .join("marker")
    .attr("id", d => `arrowhead-${d.source.id.replace(/\s+/g, '')}-${d.target.id.replace(/\s+/g, '')}-${d.category}`)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 20)
    .attr("refY", 0)
    .attr("orient", "auto")
    .attr("markerWidth", 8)
    .attr("markerHeight", 8)
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("fill", d => getLinkColor(d.category));

    const link = svg.append("g")
      .selectAll("line")
      .attr("class", "link")
      .data(links)
      .join("line")
      .style("stroke", d => getLinkColor(d.category))
      .style("stroke-width", 1)
      .attr("marker-end", d => `url(#arrowhead-${d.source.id.replace(/\s+/g, '')}-${d.target.id.replace(/\s+/g, '')}-${d.category})`);

    const node = svg.append("g")
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
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("transform", d => `translate(${d.x},${d.y})`);
    });

    // Show images, if available
    node.filter(d => d.characterImageThumb)
      .append("image")
      .attr("xlink:href", d => d.characterImageThumb)
      .attr("width", 20)
      .attr("height", 20)
      .attr("x", -10)
      .attr("y", -10);

    // Show circles, if no image is available
    node.filter(d => !d.characterImageThumb)
      .append("circle")
      .attr("r", 8)
      .attr("fill", "#999");

    // Add titles for nodes
    node.append("title")
      .text(d => d.id);

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
