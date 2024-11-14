document.addEventListener('DOMContentLoaded', function() {
  // Get SVG and update its dimensions
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
    
    console.log(width, height);

    return { width, height };
  }

  // Initial setup and window resize handler
  window.addEventListener('resize', () => {
    const dimensions = updateSVGSize();
    // Update the center force with new dimensions
    simulation.force("center", d3.forceCenter(dimensions.width / 2, dimensions.height / 2));
    // Restart simulation to apply new center force
    simulation.alpha(0.3).restart();
  });

  // Initial setup
  const dimensions = updateSVGSize();

  // Sample data
  const nodes = [
    {id:"Addam Marbrand"},
    {id:"Aegon Targaryen"},
    {id:"Aeron Greyjoy"},
  ];

  const links = [
    {source: "Addam Marbrand", target: "Aegon Targaryen", category:"killedBy"},
    {source: "Addam Marbrand", target: "Aeron Greyjoy", category:"siblings"}
  ];

  // Define link color according to the link cathegory
  function getLinkColor(category) {
    switch (category) {
      case "killedBy":
        return "red";
      case "siblings":
        return "blue";
      default:
        return "#999"; // default color
  }
}

  // Create force simulation with initial dimensions
  const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(200))
    .force("charge", d3.forceManyBody())
    .force("x", d3.forceX())
    .force("y", d3.forceY())
    .force("center", d3.forceCenter(dimensions.width / 2, dimensions.height / 2));

  // Get SVG element using d3
  const svg = d3.select('#network-canvas');

  // Add arrows to the links
  svg.append("defs")
    .selectAll("marker")
    .data(links)
    .join("marker")
    .attr("id", d => `arrow-${d}`)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 38)
    .attr("refY", 0)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path")
    .attr("fill", d => getLinkColor(d.category))
    .attr("d", 'M0,-5L10,0L0,5');

  // Draw links
  const link = svg.append("g")
    .selectAll("line")
    .attr("class", "link")
    .data(links)
    .join("line")
    .style("stroke", "#999")
    .style("stroke-width", 1)
    .style("stroke", d => getLinkColor(d.category))
    .attr("marker-end", d => `url(#arrowhead-${d.source.id.replace(/\s+/g, '')}-${d.target.id.replace(/\s+/g, '')}-${d.category}`); // set unique ID for each links

  // Add arrows to the links
  svg.append("defs")
    .selectAll("line")
    .append("marker")
    .data(links)
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


  // Draw nodes
  const node = svg.append("g")
    .selectAll("circle")
    .data(nodes)
    .join("circle")
    .attr("r", 10)
    .style("fill", "#999")
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));

  // Add titles for nodes
  node.append("title")
    .text(d => d.id);

  // Add labels for nodes (this is where the node name is added)
  const label = svg.append("g")
    .selectAll("text")
    .data(nodes)
    .join("text")
    .attr("x", d => d.x)  // Set initial position
    .attr("y", d => d.y)  // Set initial position
    .attr("dy", -10)      // Position the text a bit above the node
    .attr("text-anchor", "middle")
    .style("font-size", "12px")
    .style("fill", "#333")
    .text(d => d.id);  // Display the node's name

  // Update positions on each tick
  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y)
      //.attr("marker-end", "url(#arrowhead)");

    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);

      label
      .attr("x", d => d.x)  // Update label's position
      .attr("y", d => d.y);
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

  // Add Shiny message handler to clear SVG
  Shiny.addCustomMessageHandler('remove_network_elements', function(message) {
    const svg = document.getElementById('network-canvas');
    if (!svg) return;
    while (svg.firstChild) {
      svg.removeChild(svg.firstChild);
    }
  });
});
