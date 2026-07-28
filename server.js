const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Prevent browser caching for data files
app.use('/data', (req, res, next) => {
  res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, private');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  next();
});

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.static(__dirname));

// Data File Routes
app.get('/data/campus_data.json', (req, res) => {
  const p1 = path.join(__dirname, 'public', 'data', 'campus_data.json');
  if (fs.existsSync(p1)) return res.sendFile(p1);
  res.sendFile(path.join(__dirname, 'campus_data.json'));
});

app.get('/data/Drawing.geojson', (req, res) => {
  const p1 = path.join(__dirname, 'public', 'data', 'Drawing.geojson');
  if (fs.existsSync(p1)) return res.sendFile(p1);
  res.sendFile(path.join(__dirname, 'Drawing.geojson'));
});
const DATA_FILE = path.join(__dirname, 'public', 'data', 'campus_data.json');
const ANNOUNCEMENTS_FILE = path.join(__dirname, 'public', 'data', 'announcements.json');
const ANALYTICS_FILE = path.join(__dirname, 'public', 'data', 'analytics.json');

// Initialize store files if missing
if (!fs.existsSync(ANNOUNCEMENTS_FILE)) {
  fs.writeFileSync(ANNOUNCEMENTS_FILE, JSON.stringify([
    {
      id: "ann_1",
      locationId: "mtl_hall_02",
      title: "Semester Examination in Progress",
      message: "Quiet zone in effect around MTL Hall 02 between 9:00 AM - 12:00 PM.",
      type: "warning",
      date: new Date().toISOString()
    },
    {
      id: "ann_2",
      locationId: "canteen",
      title: "Special Lunch Buffet Available Today",
      message: "Student canteen serving traditional lunch menu from 11:30 AM onwards.",
      type: "info",
      date: new Date().toISOString()
    }
  ], null, 2));
}

if (!fs.existsSync(ANALYTICS_FILE)) {
  fs.writeFileSync(ANALYTICS_FILE, JSON.stringify({
    totalScans: 148,
    gateScans: {
      "security_room": 124,
      "regional_center_mattakkuliya": 24
    },
    popularDestinations: {
      "mtl_hall_01": 42,
      "it_lab": 35,
      "canteen": 29,
      "auditorium": 22,
      "class_room_02": 15
    },
    recentScans: [
      { gate: "security_room", timestamp: new Date().toISOString() }
    ]
  }, null, 2));
}

// Routes
app.get('/api/campus-data', (req, res) => {
  try {
    const raw = fs.readFileSync(DATA_FILE, 'utf-8');
    res.json(JSON.parse(raw));
  } catch (err) {
    res.status(500).json({ error: 'Failed to read campus data' });
  }
});

app.get('/api/announcements', (req, res) => {
  try {
    const raw = fs.readFileSync(ANNOUNCEMENTS_FILE, 'utf-8');
    res.json(JSON.parse(raw));
  } catch (err) {
    res.json([]);
  }
});

app.post('/api/announcements', (req, res) => {
  try {
    const { locationId, title, message, type } = req.body;
    const raw = fs.readFileSync(ANNOUNCEMENTS_FILE, 'utf-8');
    const anns = JSON.parse(raw);
    const newAnn = {
      id: 'ann_' + Date.now(),
      locationId,
      title,
      message,
      type: type || 'info',
      date: new Date().toISOString()
    };
    anns.unshift(newAnn);
    fs.writeFileSync(ANNOUNCEMENTS_FILE, JSON.stringify(anns, null, 2));
    res.json({ success: true, announcement: newAnn });
  } catch (err) {
    res.status(500).json({ error: 'Failed to save announcement' });
  }
});

app.delete('/api/announcements/:id', (req, res) => {
  try {
    const { id } = req.params;
    const raw = fs.readFileSync(ANNOUNCEMENTS_FILE, 'utf-8');
    let anns = JSON.parse(raw);
    anns = anns.filter(a => a.id !== id);
    fs.writeFileSync(ANNOUNCEMENTS_FILE, JSON.stringify(anns, null, 2));
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: 'Failed to delete announcement' });
  }
});

app.post('/api/analytics/scan', (req, res) => {
  try {
    const { gate, dest } = req.body;
    const raw = fs.readFileSync(ANALYTICS_FILE, 'utf-8');
    const analytics = JSON.parse(raw);
    
    analytics.totalScans = (analytics.totalScans || 0) + 1;
    if (gate) {
      analytics.gateScans[gate] = (analytics.gateScans[gate] || 0) + 1;
    }
    if (dest) {
      analytics.popularDestinations[dest] = (analytics.popularDestinations[dest] || 0) + 1;
    }
    analytics.recentScans.unshift({
      gate: gate || 'direct',
      dest: dest || null,
      timestamp: new Date().toISOString()
    });
    if (analytics.recentScans.length > 50) analytics.recentScans.pop();
    
    fs.writeFileSync(ANALYTICS_FILE, JSON.stringify(analytics, null, 2));
    res.json({ success: true, totalScans: analytics.totalScans });
  } catch (err) {
    res.status(500).json({ error: 'Failed to update analytics' });
  }
});

app.get('/api/analytics', (req, res) => {
  try {
    const raw = fs.readFileSync(ANALYTICS_FILE, 'utf-8');
    res.json(JSON.parse(raw));
  } catch (err) {
    res.status(500).json({ error: 'Failed to read analytics' });
  }
});

// Fallback to index.html for SPA routing
app.use((req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Campus Navigation Server running on http://localhost:${PORT}`);
  });
}

module.exports = app;
