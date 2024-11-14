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
    { id: "Node 1" },
    { id: "Node 2" },
    { id: "Node 3" },
    { id: "Node 4" }
  ];

  const links = [
    { source: "Node 1", target: "Node 2" },
    { source: "Node 2", target: "Node 3" },
    { source: "Node 3", target: "Node 4" },
    { source: "Node 4", target: "Node 1" }
  ];

  // Create force simulation with initial dimensions
  const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id))
    .force("charge", d3.forceManyBody().strength(-100))
    .force("center", d3.forceCenter(dimensions.width / 2, dimensions.height / 2));

  // Get SVG element using d3
  const svg = d3.select('#network-canvas');

  // Draw links
  const link = svg.append("g")
    .selectAll("line")
    .data(links)
    .join("line")
    .style("stroke", "#999")
    .style("stroke-width", 1);

  // Draw nodes
  const node = svg.append("g")
    .selectAll("circle")
    .data(nodes)
    .join("circle")
    .attr("r", 5)
    .style("fill", "#69b3a2")
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));

  // Add titles for nodes
  node.append("title")
    .text(d => d.id);

  // Update positions on each tick
  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);
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
