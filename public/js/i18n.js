// Multi-Language i18n Translation Engine
const i18n = {
  currentLang: 'en',
  
  translations: {
    en: {
      appName: "Ocean University of Sri Lanka",
      welcomeTitle: "Welcome to the Ocean University of Sri Lanka",
      appSub: "Interactive Zero-App Campus Navigation System",
      searchPlaceholder: "Search classrooms, halls, labs, canteen...",
      allCategories: "All Places",
      academic: "Academic & Halls",
      labs: "Labs & Workshops",
      admin: "Administrative",
      sports: "Sports & Rec",
      facilities: "Facilities & Dining",
      amenities: "Amenities",
      scannedBanner: "📍 Scanned from {gate}. Starting point locked.",
      routeSummary: "Walking Route",
      distance: "Distance",
      estTime: "Est. Walk Time",
      wheelchairOnly: "Wheelchair Accessible Paths Only",
      navigateHere: "Navigate Here",
      viewFloorPlan: "Indoor Floor Plan",
      selectStart: "Select Start Point",
      selectDest: "Select Destination",
      startFromGate: "Main Gate (Security Room)",
      adminCMS: "Admin Portal",
      announcements: "Announcements",
      close: "Close",
      groundFloor: "Ground Floor",
      firstFloor: "1st Floor",
      secondFloor: "2nd Floor",
      roomCode: "Room Code",
      capacity: "Capacity",
      activeNotice: "Notice"
    },
    si: {
      appName: "ශ්‍රී ලංකා සාගර විශ්වවිද්‍යාලය",
      welcomeTitle: "ශ්‍රී ලංකා සාගර විශ්වවිද්‍යාලයට සාදරයෙන් පිළිගනිමු",
      appSub: "ක්ෂණික අන්තර්ක්‍රියාකාරී සිතියම් පද්ධතිය",
      searchPlaceholder: "දේශන ශාලා, රසායනාගාර, ආපනශාලා සොයන්න...",
      allCategories: "සියලු ස්ථාන",
      academic: "දේශන ශාලා හා අධ්‍යයන",
      labs: "රසායනාගාර හා වැඩපල",
      admin: "පරිපාලන අංශ",
      sports: "ක්‍රීඩා අංශ",
      facilities: "පහසුකම් හා ආපනශාලා",
      amenities: "අත්‍යවශ්‍ය පහසුකම්",
      scannedBanner: "📍 {gate} සිට ඇතුළු විය. ආරම්භක ස්ථානය තහවුරුයි.",
      routeSummary: "පාගමන් මාර්ගය",
      distance: "දුර ප්‍රමාණය",
      estTime: "ගතවන කාලය",
      wheelchairOnly: "රෝද පුටු ප්‍රවේශිත මාර්ග පමණි",
      navigateHere: "මෙහි යන්න",
      viewFloorPlan: "අභ්‍යන්තර මහල් සැලැස්ම",
      selectStart: "ආරම්භක ස්ථානය",
      selectDest: "ගමනාන්තය තෝරන්න",
      startFromGate: "ප්‍රධාන ද්වාරය (ආරක්ෂක කුටිය)",
      adminCMS: "පරිපාලන පුවරුව",
      announcements: "නිවේදන",
      close: "වසා දමන්න",
      groundFloor: "බිම් මහල",
      firstFloor: "1 වන මහල",
      secondFloor: "2 වන මහල",
      roomCode: "කාමර අංකය",
      capacity: "ධාරිතාව",
      activeNotice: "විශේෂ නිවේදනය"
    },
    ta: {
      appName: "இலங்கை சமுத்திர பல்கலைக்கழகம்",
      welcomeTitle: "இலங்கை சமுத்திர பல்கலைக்கழகத்திற்கு நல்வரவு",
      appSub: "உடனடி ஊடாடும் வரைபட அமைப்பு",
      searchPlaceholder: "வகுப்பறைகள், ஆய்வகங்கள், உணவகங்களைத் தேடுங்கள்...",
      allCategories: "அனைத்து இடங்களும்",
      academic: "கல்வி மற்றும் அரங்குகள்",
      labs: "ஆய்வகங்கள் & பட்டறைகள்",
      admin: "நிர்வாகப் பிரிவுகள்",
      sports: "விளையாட்டு",
      facilities: "வசதிகள் & உணவகம்",
      amenities: "அத்தியாவசிய வசதிகள்",
      scannedBanner: "📍 {gate} இலிருந்து ஸ்கேன் செய்யப்பட்டது. தொடக்க இடம் உறுதி செய்யப்பட்டது.",
      routeSummary: "நடைபாதை பாதை",
      distance: "தூரம்",
      estTime: "நடக்கும் நேரம்",
      wheelchairOnly: "சக்கர நாற்காலி பாதை மட்டும்",
      navigateHere: "இங்கே செல்லவும்",
      viewFloorPlan: "உள் தள திட்டம்",
      selectStart: "தொடக்க இடத்தைத் தேர்ந்தெடுக்கவும்",
      selectDest: "இலக்கைத் தேர்ந்தெடுக்கவும்",
      startFromGate: "பிரதான வாயில் (பாதுகாப்பு அறை)",
      adminCMS: "நிர்வாக போர்டல்",
      announcements: "அறிவிப்புகள்",
      close: "மூடு",
      groundFloor: "தரை தளம்",
      firstFloor: "1 ஆம் தளம்",
      secondFloor: "2 ஆம் தளம்",
      roomCode: "அறை குறியீடு",
      capacity: "கொள்ளளவு",
      activeNotice: "அறிவிப்பு"
    }
  },

  setLanguage(lang) {
    if (this.translations[lang]) {
      this.currentLang = lang;
      // Sync all language dropdowns across the page
      document.querySelectorAll('#lang-select, .lang-selector, .lang-select-global').forEach(sel => {
        sel.value = lang;
      });
      this.updateDOM();
    }
  },

  t(key, params = {}) {
    let str = this.translations[this.currentLang][key] || this.translations['en'][key] || key;
    for (const [p, val] of Object.entries(params)) {
      str = str.replace(`{${p}}`, val);
    }
    return str;
  },

  updateDOM() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      el.textContent = this.t(key);
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      el.placeholder = this.t(key);
    });
  }
};

window.i18n = i18n;
