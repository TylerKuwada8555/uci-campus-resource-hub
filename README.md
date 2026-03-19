
## Getting Started

This project has:

- an Angular frontend
- a FastAPI backend

You need both running for the full app.

### Prerequisites

- Node.js >= 18
- npm >= 9
- Python 3

### Setup

```bash
git clone https://github.com/TylerKuwada8555/uci-campus-resource-hub.git
cd uci-campus-resource-hub
npm install
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

### One-Time Backend Data Build

Run this only if `api/resources.db`, `api/resources.index`, or `api/ids.npy` do not exist:

```bash
cd api
python3 resource_import.py
python3 build_index.py
cd ..
```

### Run the App

Terminal 1:

```bash
source .venv/bin/activate
cd api
python3 -m uvicorn db:app --reload
```

Terminal 2:

```bash
npm start
```

Open [http://localhost:4200](http://localhost:4200).

## Notes

- The backend runs on [http://localhost:8000](http://localhost:8000).
- Login/onboarding is frontend-only and uses browser `localStorage` with the key `campus_hub_user`.
- If that saved profile already exists, the app will go straight to the home page.
- To test onboarding again, log out, clear `campus_hub_user`, or use an incognito window.
