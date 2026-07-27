const fs = require('fs');
const path = require('path');

// Load routing logic
const CampusRouter = require('../public/js/routing.js');

const campusDataPath = path.join(__dirname, '..', 'public', 'data', 'campus_data.json');
const campusData = JSON.parse(fs.readFileSync(campusDataPath, 'utf-8'));

console.log(`Starting automated route validation tests...`);
console.log(`Total Locations: ${campusData.locations.length}`);
console.log(`Graph Nodes: ${campusData.graph.nodes.length}`);
console.log(`Graph Edges: ${campusData.graph.edges.length}\n`);

const router = new CampusRouter(campusData.graph.nodes, campusData.graph.edges);
const startGate = 'security_room';

let passed = 0;
let failed = 0;

campusData.locations.forEach(loc => {
  if (loc.id === startGate) return;

  const route = router.findShortestPath(startGate, loc.id, false);
  if (route && route.coordinates.length > 0 && route.totalDistance > 0) {
    passed++;
    console.log(`✔ Route to [${loc.name}] -> Distance: ${route.totalDistance}m, Time: ${route.timeFormatted}, Steps: ${route.steps.length}`);
  } else {
    failed++;
    console.error(`❌ FAILED: No path found from ${startGate} to [${loc.name}]`);
  }
});

console.log(`\n===================================`);
console.log(`TEST SUMMARY: ${passed} PASSED, ${failed} FAILED out of ${campusData.locations.length - 1} target routes.`);
console.log(`===================================\n`);

if (failed > 0) {
  process.exit(1);
} else {
  process.exit(0);
}
