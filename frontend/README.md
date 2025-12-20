# AI Safety Platform - Frontend

React + TypeScript frontend with shadcn/ui for the AI Safety & Security Platform.

## Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Build for production**
   ```bash
   npm run build
   ```

## Features

- ✅ Dashboard with safety metrics
- ✅ Prompt scanning interface
- ✅ Output scanning interface
- ✅ Audit logs viewer
- ✅ Risk scores visualization
- ✅ Reports generation

## API Connection

The frontend connects to the backend API at `http://localhost:8000/api/v1` by default.

To change the API URL, create a `.env` file:
```
VITE_API_URL=http://localhost:8000/api/v1
```

