#!/bin/bash

# Healthcare Risk Monitoring Dashboard Launcher
# Easy startup script for the web application

echo "==============================================="
echo "🏥 HEALTHCARE RISK MONITORING DASHBOARD"
echo "==============================================="
echo ""
echo "Starting the dashboard application..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "⚠️  Flask is not installed. Installing..."
    pip install flask --quiet
    if [ $? -eq 0 ]; then
        echo "✅ Flask installed successfully"
    else
        echo "❌ Failed to install Flask"
        echo "Please run: pip install flask"
        exit 1
    fi
fi

# Check if pandas is installed
if ! python3 -c "import pandas" &> /dev/null; then
    echo "⚠️  Pandas is not installed. Installing..."
    pip install pandas --quiet
    if [ $? -eq 0 ]; then
        echo "✅ Pandas installed successfully"
    else
        echo "❌ Failed to install Pandas"
        echo "Please run: pip install pandas"
        exit 1
    fi
fi

# Check if the dashboard file exists
if [ ! -f "dashboard_app.py" ]; then
    echo "❌ Error: dashboard_app.py not found"
    echo "Please ensure the dashboard file is in the current directory"
    exit 1
fi

# Check if the dataset exists
if [ ! -f "diabetes_hypertension_dataset.csv" ]; then
    echo "⚠️  Warning: Dataset not found"
    echo "The dashboard will run with limited functionality"
    echo "To get full functionality, ensure diabetes_hypertension_dataset.csv is present"
    echo ""
fi

echo "✅ All checks passed!"
echo ""
echo "==============================================="
echo "🌐 DASHBOARD ACCESS INFORMATION"
echo "==============================================="
echo ""
echo "The dashboard will be available at:"
echo ""
echo "  📍 Local Access:    http://localhost:5000"
echo "  📍 Network Access:  http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "==============================================="
echo "📊 AVAILABLE FEATURES"
echo "==============================================="
echo ""
echo "  • Overview:         Real-time statistics"
echo "  • Population:       Demographics & risk factors"
echo "  • Predictions:      Individual risk assessment"
echo "  • Interventions:    Priority tracking"
echo "  • Analytics:        Outcomes & projections"
echo ""
echo "==============================================="
echo "🔌 API ENDPOINTS"
echo "==============================================="
echo ""
echo "  GET  /                 - Main dashboard"
echo "  GET  /api/metrics      - JSON statistics"
echo "  GET  /api/patients     - Patient list"
echo "  POST /api/predict      - Risk prediction"
echo "  GET  /api/trends       - Trend data"
echo "  GET  /api/export       - Export CSV"
echo ""
echo "==============================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "Starting Flask server..."
echo "-----------------------------------------------"

# Start the Flask application
python3 dashboard_app.py

# Handle script termination
echo ""
echo "==============================================="
echo "Dashboard stopped. Thank you for using the"
echo "Healthcare Risk Monitoring Dashboard!"
echo "==============================================="
