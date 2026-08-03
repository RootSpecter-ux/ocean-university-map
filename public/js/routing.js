// Campus A* & Dijkstra Pathfinding Navigation Engine

class CampusRouter {
  constructor(nodes, edges) {
    this.nodes = {};
    if (Array.isArray(nodes)) {
      nodes.forEach(n => { this.nodes[n.id] = n; });
    } else if (nodes && typeof nodes === 'object') {
      this.nodes = nodes;
    }
    this.edges = edges || [];
    this.adjacency = {};
    this.buildAdjacency();
  }

  buildAdjacency() {
    this.adjacency = {};
    Object.keys(this.nodes).forEach(id => {
      this.adjacency[id] = [];
    });

    // Auto-generate spatial proximity edges if no explicit edges provided in campus_data.json
    if (!Array.isArray(this.edges) || this.edges.length === 0) {
      const nodeKeys = Object.keys(this.nodes);
      for (let i = 0; i < nodeKeys.length; i++) {
        for (let j = i + 1; j < nodeKeys.length; j++) {
          const n1 = this.nodes[nodeKeys[i]];
          const n2 = this.nodes[nodeKeys[j]];
          if (n1 && n2 && n1.lat && n1.lon && n2.lat && n2.lon) {
            const dist = Math.round(this.haversine(n1.lat, n1.lon, n2.lat, n2.lon));
            this.adjacency[n1.id].push({ target: n2.id, distance: dist, isAccessible: true });
            this.adjacency[n2.id].push({ target: n1.id, distance: dist, isAccessible: true });
          }
        }
      }
      return;
    }

    this.edges.forEach(edge => {
      const from = edge.from || edge.source;
      const to = edge.to || edge.target;
      const dist = edge.weight || edge.distance || 10;
      const acc = edge.accessible !== false && edge.isAccessible !== false;

      if (this.nodes[from] && this.nodes[to]) {
        this.adjacency[from].push({
          target: to,
          distance: dist,
          isAccessible: acc
        });
        this.adjacency[to].push({
          target: from,
          distance: dist,
          isAccessible: acc
        });
      }
    });
  }

  haversine(lat1, lon1, lat2, lon2) {
    const R = 6371000;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }

  getBearing(lat1, lon1, lat2, lon2) {
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const y = Math.sin(dLon) * Math.cos(lat2 * Math.PI / 180);
    const x = Math.cos(lat1 * Math.PI / 180) * Math.sin(lat2 * Math.PI / 180) -
              Math.sin(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.cos(dLon);
    return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
  }

  getDirectionText(bearing) {
    if (bearing >= 337.5 || bearing < 22.5) return "North";
    if (bearing >= 22.5 && bearing < 67.5) return "North-East";
    if (bearing >= 67.5 && bearing < 112.5) return "East";
    if (bearing >= 112.5 && bearing < 157.5) return "South-East";
    if (bearing >= 157.5 && bearing < 202.5) return "South";
    if (bearing >= 202.5 && bearing < 247.5) return "South-West";
    if (bearing >= 247.5 && bearing < 292.5) return "West";
    return "North-West";
  }

  findShortestPath(startId, destId, accessibleOnly = false) {
    if (!this.nodes[startId] || !this.nodes[destId]) return null;

    const openSet = new Set([startId]);
    const cameFrom = {};
    const gScore = {};
    const fScore = {};

    Object.keys(this.nodes).forEach(id => {
      gScore[id] = Infinity;
      fScore[id] = Infinity;
    });

    gScore[startId] = 0;
    fScore[startId] = this.haversine(
      this.nodes[startId].lat, this.nodes[startId].lon,
      this.nodes[destId].lat, this.nodes[destId].lon
    );

    while (openSet.size > 0) {
      let current = null;
      let lowestF = Infinity;
      for (const node of openSet) {
        if (fScore[node] < lowestF) {
          lowestF = fScore[node];
          current = node;
        }
      }

      if (current === destId) {
        const pathNodeIds = [current];
        while (cameFrom[current]) {
          current = cameFrom[current];
          pathNodeIds.unshift(current);
        }

        const coordinates = pathNodeIds.map(id => [this.nodes[id].lat, this.nodes[id].lon]);
        const totalDistance = Math.round(gScore[destId]);
        const totalSeconds = Math.round(totalDistance / 1.25);
        const mins = Math.floor(totalSeconds / 60);
        const secs = totalSeconds % 60;
        const timeFormatted = mins > 0 ? `${mins} min ${secs} sec` : `${secs} sec`;

        const steps = [];
        for (let i = 0; i < pathNodeIds.length - 1; i++) {
          const n1 = this.nodes[pathNodeIds[i]];
          const n2 = this.nodes[pathNodeIds[i + 1]];
          const d = Math.round(this.haversine(n1.lat, n1.lon, n2.lat, n2.lon));
          const brng = this.getBearing(n1.lat, n1.lon, n2.lat, n2.lon);
          const dirStr = this.getDirectionText(brng);

          let actionStr = `Head ${dirStr} towards ${n2.name}`;
          if (i === 0) {
            actionStr = `Start at ${n1.name}, walk ${dirStr} towards ${n2.name}`;
          } else if (i === pathNodeIds.length - 2) {
            actionStr = `Arrive at door of ${n2.name}`;
          }

          steps.push({
            stepNum: i + 1,
            instruction: actionStr,
            distanceMeters: d,
            targetName: n2.name
          });
        }

        return {
          pathNodeIds,
          coordinates,
          totalDistance,
          timeFormatted,
          steps
        };
      }

      openSet.delete(current);

      const neighbors = this.adjacency[current] || [];
      for (const neighbor of neighbors) {
        if (accessibleOnly && !neighbor.isAccessible) continue;

        const tentativeG = gScore[current] + neighbor.distance;
        if (tentativeG < gScore[neighbor.target]) {
          cameFrom[neighbor.target] = current;
          gScore[neighbor.target] = tentativeG;
          fScore[neighbor.target] = tentativeG + this.haversine(
            this.nodes[neighbor.target].lat, this.nodes[neighbor.target].lon,
            this.nodes[destId].lat, this.nodes[destId].lon
          );
          openSet.add(neighbor.target);
        }
      }
    }

    return null;
  }

  findNearestNode(lat, lon) {
    let nearest = null;
    let minDist = Infinity;
    Object.values(this.nodes).forEach(node => {
      const d = this.haversine(lat, lon, node.lat, node.lon);
      if (d < minDist) {
        minDist = d;
        nearest = node;
      }
    });
    return { node: nearest, distance: minDist };
  }

  findShortestPathFromLocation(userLat, userLon, destId, accessibleOnly = false) {
    const nearestResult = this.findNearestNode(userLat, userLon);
    if (!nearestResult || !nearestResult.node) return null;

    const startNodeId = nearestResult.node.id;
    const baseRoute = this.findShortestPath(startNodeId, destId, accessibleOnly);

    if (!baseRoute) return null;

    const liveCoords = [[userLat, userLon], ...baseRoute.coordinates];
    const initialSegmentDist = Math.round(this.haversine(userLat, userLon, nearestResult.node.lat, nearestResult.node.lon));
    const totalDistance = baseRoute.totalDistance + initialSegmentDist;

    const totalSeconds = Math.round(totalDistance / 1.25);
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    const timeFormatted = mins > 0 ? `${mins} min ${secs} sec` : `${secs} sec`;

    const liveSteps = [
      {
        stepNum: 1,
        instruction: `Start from your actual live location, walk towards ${nearestResult.node.name}`,
        distanceMeters: initialSegmentDist,
        targetName: nearestResult.node.name
      },
      ...baseRoute.steps.map(s => ({ ...s, stepNum: s.stepNum + 1 }))
    ];

    return {
      pathNodeIds: [startNodeId, ...baseRoute.pathNodeIds],
      coordinates: liveCoords,
      totalDistance,
      timeFormatted,
      steps: liveSteps
    };
  }
}

if (typeof window !== 'undefined') {
  window.CampusRouter = CampusRouter;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CampusRouter;
}
