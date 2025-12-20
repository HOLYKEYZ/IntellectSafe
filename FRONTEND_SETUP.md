# Frontend Setup Instructions

## Prerequisites

1. **Node.js** (v18 or higher)
   - Download from: https://nodejs.org/
   - Verify installation: `node --version` and `npm --version`

## Setup Steps

1. **Navigate to frontend directory**
   ```powershell
   cd frontend
   ```

2. **Install dependencies**
   ```powershell
   npm install
   ```

3. **Start development server**
   ```powershell
   npm run dev
   ```

4. **Access the dashboard**
   - Open browser: http://localhost:3000
   - The frontend will proxy API requests to http://localhost:8000

## Building for Production

```powershell
npm run build
```

The built files will be in the `dist` directory.

## Troubleshooting

### Module not found errors
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

### API connection errors
- Make sure backend is running on port 8000
- Check CORS settings in backend
- Verify API URL in `src/lib/api.ts`

### Port already in use
- Change port in `vite.config.ts` or use: `npm run dev -- --port 3001`

