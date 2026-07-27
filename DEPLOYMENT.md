# Free Deployment Guide for University Campus Navigation System

This app can be hosted **100% FREELY** with zero server costs so all university newcomers can access it via QR code scanning!

---

## 🏆 Option 1: Vercel (RECOMMENDED - 100% Free Forever)

Vercel provides ultra-fast global CDN edge hosting with automatic HTTPS SSL certificates.

### ⚡ Method A: Direct Command Line (Fastest - 1 Minute)
1. Open terminal inside the project folder (`c:\Users\HP\OneDrive\Desktop\Map`).
2. Run:
   ```bash
   npx vercel
   ```
3. Follow the 3 prompt questions:
   - *Set up and deploy?* `Y`
   - *Which scope?* `Your Account`
   - *Link to existing project?* `N`
4. **Done!** Vercel gives you a free HTTPS URL: `https://university-campus-map.vercel.app`

---

### ⚡ Method B: GitHub Auto-Deploy (Continuous Updates)
1. Push this project code to a public or private **GitHub Repository**.
2. Go to [vercel.com](https://vercel.com) and click **"Add New Project"**.
3. Import your GitHub repository.
4. Click **"Deploy"**. Any future commit automatically updates the live website!

---

## 🥈 Option 2: Netlify (100% Free - Drag & Drop)
1. Go to [netlify.com](https://netlify.com) and log in.
2. Go to **Sites** ➔ Drag and drop the `public/` folder into Netlify!
3. Netlify immediately generates a live URL: `https://university-map.netlify.app`.

---

## 🥉 Option 3: GitHub Pages (100% Free)
1. Push your repository to GitHub.
2. Go to **Repository Settings** ➔ **Pages**.
3. Set Branch to `main` and folder to `/public`.
4. Your website is live at `https://<your-username>.github.io/<repo-name>/`.
