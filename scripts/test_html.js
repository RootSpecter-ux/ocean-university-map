const fs = require('fs');

const html = fs.readFileSync('index.html', 'utf-8');
console.log('index.html size:', html.length);
console.log('Has #map:', html.includes('id="map"'));
console.log('Has script tags:', html.includes('campus_data_fallback.js'));

const fallback = fs.readFileSync('js/campus_data_fallback.js', 'utf-8');
console.log('fallback size:', fallback.length);
console.log('Has window.FALLBACK_CAMPUS_DATA:', fallback.includes('window.FALLBACK_CAMPUS_DATA'));
console.log('Has window.FALLBACK_RAW_GEOJSON:', fallback.includes('window.FALLBACK_RAW_GEOJSON'));
