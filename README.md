# 🏫 Campus Hub — UCI Services & Resources

A personalized campus resource discovery app for UC Irvine students. Built with **Angular 21**, **Tailwind CSS v4**, and **TypeScript**.

The app recommends UCI services (academic advising, basic needs, health, career, financial aid, etc.) based on each student's **major**, **year**, and **international status**.

---

## ✨ Features

- 🔐 **Simulated Login** — UCI NetID sign-in flow
- 📝 **Onboarding** — 3-step form to collect student profile (name, major, year, international status)
- 🎯 **Personalized Ranking** — Resources are ranked by relevance to the student's profile
- 🔍 **Search & Filter** — Keyword search + category chip filters
- 🏷️ **Smart Badges** — Auto-generated tags like "Open Now", "Essential", "Deadline Approaching"
- 🌙 **Dark Glassmorphism UI** — Premium design with animations and smooth transitions
- 💾 **Persistent State** — Profile data saved to localStorage across sessions

---

## 📸 Screenshots

| Login | Onboarding | Home |
|-------|------------|------|
| Glassmorphism card with UCI branding | 3-step profile collection wizard | Ranked resource grid with badges |

---

## 🗂️ Project Structure

```
src/
├── app/
│   ├── models/
│   │   └── user.model.ts             # UserProfile & Resource interfaces
│   ├── services/
│   │   ├── auth.service.ts           # Auth state management (signals + localStorage)
│   │   └── resource.service.ts       # Resource loading, ranking, search, badges
│   ├── components/
│   │   └── resource-card/            # Reusable resource card component
│   ├── pages/
│   │   ├── login/                    # Login page
│   │   ├── onboarding/              # Multi-step onboarding form
│   │   └── home/                    # Main dashboard with resource grid
│   ├── app.routes.ts                 # Route definitions + auth guard
│   ├── app.config.ts                 # App providers
│   └── app.component.ts             # Root component
├── styles.css                        # Global styles + Tailwind import
└── index.html                        # Entry HTML with meta tags & fonts
data/
└── uci_resources.json                # Mock dataset of 33 UCI resources
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** ≥ 18 (LTS recommended, e.g. v20 or v22)
- **npm** ≥ 9

> Check your versions:
> ```bash
> node -v
> npm -v
> ```

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/TylerKuwada8555/uci-campus-resource-hub.git
   cd uci-campus-resource-hub
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Start the dev server**

   ```bash
   npm start
   ```

4. **Open in browser**

   Navigate to **[http://localhost:4200](http://localhost:4200)**

That's it! The app will auto-reload when you edit source files.

---

## 🛠️ Available Scripts

| Command | Description |
|---------|-------------|
| `npm start` | Start dev server at `localhost:4200` |
| `npm run build` | Build for production (output in `dist/`) |
| `npm test` | Run unit tests with Vitest |
| `npm run watch` | Build in watch mode |

---

## 🧩 Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| [Angular](https://angular.dev) | 21.x | Frontend framework (standalone components) |
| [Tailwind CSS](https://tailwindcss.com) | 4.x | Utility-first CSS styling |
| [TypeScript](https://www.typescriptlang.org) | 5.9 | Type-safe JavaScript |
| [PostCSS](https://postcss.org) | 8.x | CSS processing pipeline |

---

## 📖 How It Works

### User Flow

```
Login → Onboarding (if new user) → Home Dashboard
  └── Returning user skips onboarding ──┘
```

### Ranking Logic

Resources are scored based on profile match:

| Factor | Points | Example |
|--------|--------|---------|
| Major match | +30 | CS student → ICS Academic Advising ranks higher |
| Year relevance | +15 | Freshman → orientation resources boost |
| International status | +40 | International → visa & immigration services boost |
| Category boost | +10 | Basic needs always get a baseline boost |

---

## 📄 License

This project is for educational purposes as part of a UCI course project.
