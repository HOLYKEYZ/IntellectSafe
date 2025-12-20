# PostgreSQL Setup Guide

## Windows Setup

### Option 1: Install PostgreSQL Locally

1. **Download PostgreSQL**
   - Visit: https://www.postgresql.org/download/windows/
   - Download the installer
   - Run the installer

2. **Installation Steps**
   - Choose installation directory (default: `C:\Program Files\PostgreSQL\16`)
   - Set password for `postgres` superuser (remember this!)
   - Port: 5432 (default)
   - Locale: Default

3. **Verify Installation**
   ```powershell
   psql --version
   ```

4. **Create Database**
   ```powershell
   # Connect to PostgreSQL
   psql -U postgres
   
   # Enter your password when prompted
   
   # Create database
   CREATE DATABASE ai_safety;
   
   # Create user (optional)
   CREATE USER ai_safety_user WITH PASSWORD 'your_password_here';
   GRANT ALL PRIVILEGES ON DATABASE ai_safety TO ai_safety_user;
   
   # Exit
   \q
   ```

5. **Update .env file**
   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ai_safety
   ```
   Or with custom user:
   ```env
   DATABASE_URL=postgresql://ai_safety_user:your_password@localhost:5432/ai_safety
   ```

### Option 2: Use Docker (Recommended)

1. **Install Docker Desktop**
   - Download: https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop

2. **Run PostgreSQL Container**
   ```powershell
   docker run --name ai-safety-db `
     -e POSTGRES_PASSWORD=your_password `
     -e POSTGRES_DB=ai_safety `
     -p 5432:5432 `
     -d postgres:16
   ```

3. **Update .env file**
   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ai_safety
   ```

### Option 3: Use Cloud Database (Free Tier)

**Render PostgreSQL (Free Tier)**
1. Sign up at https://render.com
2. Create PostgreSQL database
3. Copy connection string
4. Update .env file

**Supabase (Free Tier)**
1. Sign up at https://supabase.com
2. Create new project
3. Go to Settings > Database
4. Copy connection string
5. Update .env file

## Run Migrations

After setting up database:

```powershell
# Navigate to backend directory
cd backend

# Run migrations
alembic upgrade head
```

## Verify Connection

```powershell
# Test connection
python -c "from app.services.db import engine; engine.connect(); print('Connected!')"
```

## Troubleshooting

### Connection Refused
- Check PostgreSQL is running: `Get-Service postgresql*`
- Check port 5432 is not blocked by firewall
- Verify DATABASE_URL in .env

### Authentication Failed
- Check username and password in DATABASE_URL
- Verify user has permissions on database

### Module Not Found
- Make sure you're in the `backend` directory when running commands
- Or use: `python -m uvicorn app.main:app --reload`

