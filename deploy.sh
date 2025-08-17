#!/bin/bash

echo "🚀 TechSouth Deployment Script"
echo "=============================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
cd src
python -c "from main import app, db; app.app_context().push(); db.create_all(); print('Database initialized!')"
cd ..

# Seed database with sample data
echo "Seeding database..."
python src/seed_data.py

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 To start your TechSouth website:"
echo "   Production: gunicorn --chdir src main:app --bind 0.0.0.0:5000"
echo "   Development: python src/main.py"
echo ""
echo "📱 Your website will be available at: http://localhost:5000"
echo "🎛️  Admin panel: http://localhost:5000/admin"
echo ""
echo "📚 See Permanent_Deployment_Guide.md for hosting platform deployment"
echo ""

