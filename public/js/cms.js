// Admin CMS & Analytics Manager
const CMS = {
  announcements: [],
  analytics: null,

  async init() {
    await this.fetchAnnouncements();
    await this.fetchAnalytics();
  },

  async fetchAnnouncements() {
    try {
      const res = await fetch('/api/announcements');
      if (res.ok) {
        this.announcements = await res.json();
      }
    } catch (e) {
      console.warn('Backend server API offline, using offline CMS cache');
      this.announcements = [
        {
          id: "ann_1",
          locationId: "mtl_hall_02",
          title: "Semester Examination in Progress",
          message: "Quiet zone in effect around MTL Hall 02 between 9:00 AM - 12:00 PM.",
          type: "warning"
        }
      ];
    }
  },

  async fetchAnalytics() {
    try {
      const res = await fetch('/api/analytics');
      if (res.ok) {
        this.analytics = await res.json();
      }
    } catch (e) {
      this.analytics = { totalScans: 148, popularDestinations: { "mtl_hall_01": 42 } };
    }
  },

  async logScan(gate, dest) {
    try {
      await fetch('/api/analytics/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gate, dest })
      });
    } catch (e) {
      // offline mode
    }
  },

  async createAnnouncement(locationId, title, message, type = 'info') {
    try {
      const res = await fetch('/api/announcements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ locationId, title, message, type })
      });
      if (res.ok) {
        await this.fetchAnnouncements();
        return true;
      }
    } catch (e) {
      console.error('Failed to create announcement', e);
    }
    return false;
  },

  getAnnouncementsForLocation(locationId) {
    return this.announcements.filter(a => a.locationId === locationId || a.locationId === 'all');
  },

  generateQRURL(gateId) {
    const origin = window.location.origin;
    return `${origin}/?from=${encodeURIComponent(gateId)}`;
  }
};

window.CMS = CMS;
