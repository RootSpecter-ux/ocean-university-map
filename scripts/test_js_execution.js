const fs = require('fs');
const path = require('path');

global.window = global;

// Test campus_data_fallback.js
const fallbackPath = path.join(__dirname, '..', 'js', 'campus_data_fallback.js');
const fallbackContent = fs.readFileSync(fallbackPath, 'utf-8');

eval(fallbackContent);

console.log('window.FALLBACK_CAMPUS_DATA loaded:', typeof window.FALLBACK_CAMPUS_DATA !== 'undefined');
console.log('Locations count:', window.FALLBACK_CAMPUS_DATA.locations.length);
console.log('Graph nodes count:', window.FALLBACK_CAMPUS_DATA.graph.nodes.length);
console.log('Graph edges count:', window.FALLBACK_CAMPUS_DATA.graph.edges.length);
console.log('window.FALLBACK_RAW_GEOJSON loaded:', typeof window.FALLBACK_RAW_GEOJSON !== 'undefined');
console.log('GeoJSON features count:', window.FALLBACK_RAW_GEOJSON.features.length);

// Test CampusRouter
const routingPath = path.join(__dirname, '..', 'js', 'routing.js');
const routingContent = fs.readFileSync(routingPath, 'utf-8');

eval(routingContent);

const router = new CampusRouter(window.FALLBACK_CAMPUS_DATA.graph.nodes, window.FALLBACK_CAMPUS_DATA.graph.edges);
const route = router.findShortestPath('security_room', 'auditorium', false);

console.log('\nSample Route Security Room -> Auditorium:');
console.log('Distance:', route.totalDistance, 'm');
console.log('Time:', route.timeFormatted);
console.log('Steps count:', route.steps.length);
