# SmartShelf

SmartShelf is an intelligent product management system designed to help stock managers track perishable products and prevent waste by providing data-driven insights and recommendations.

## Features

- **Dashboard**: View key metrics including total savings, active promotions, transferred products, and alerts
- **Product Management**: Track inventory across multiple store locations
- **Expiration Tracking**: Automated alerts for products nearing expiration
- **AI-Powered Recommendations**: Get actionable insights to reduce waste and optimize inventory
- **Chat Assistant**: Natural language interface for inventory management queries
- **Agentic Chat**: Advanced AI capabilities using OpenAI function calling for precise data access and recommendations
- **ML Predictor Integration**: Machine learning models to predict product expiration risk and recommend actions
- **Multi-store Support**: Manage inventory across different locations with transfer recommendations
- **Promotion Management**: Create and track promotions to reduce waste of near-expiry products
- **Data Visualization**: Interactive charts and graphs for inventory trends and predictions

## Project Structure

The project is organized into three main components:

- `/frontend` - Astro.js web application with React components
- `/backend` - FastAPI server providing REST API endpoints
- `/predictor` - ML models for product expiration prediction and recommendation generation

### Frontend (Astro.js + React)

Built with Astro.js and React, the frontend provides an intuitive user interface for inventory management.

**Tech Stack:**
- Astro.js 4.x with React components
- Tailwind CSS for styling
- HeadlessUI and HeroIcons for UI components
- TypeScript for type safety
- Axios for API communication

**Key Components:**
- Dashboard with key performance indicators and data visualizations
- Product management interface
- Interactive chat interface for natural language queries
- Responsive design for desktop and mobile access

**Chat Widget Implementation:**
The chat interface is implemented in `ChatWidget.jsx`, providing:
- Real-time conversation with the AI assistant
- User-friendly UI with loading indicators and error handling
- Message history management
- Integration with the backend chat API through the chat service

**Directory Structure:**
```
frontend/
├── src/                    # Source code
│   ├── assets/             # Static assets and images
│   ├── components/         # Reusable UI components
│   │   ├── ChatWidget.jsx  # Interactive chat interface component
│   │   ├── Dashboard.jsx   # Main dashboard component
│   │   ├── AlertTable.jsx  # Expiration alerts display
│   │   └── ...             # Other UI components
│   ├── layouts/            # Page layout templates
│   ├── pages/              # Application pages/routes
│   ├── services/           # API service integrations
│   │   └── api.js          # API client with chat integration
│   └── styles/             # Global styles and Tailwind config
├── public/                 # Static assets served as-is
├── astro.config.mjs        # Astro configuration
├── package.json            # Node.js dependencies
└── tailwind.config.mjs     # Tailwind CSS configuration
```

### Backend (FastAPI)

A FastAPI application that serves as the API layer between the frontend and the predictor.

**Tech Stack:**
- FastAPI framework
- Pydantic for data validation
- OpenAI function calling API for agentic capabilities
- SQLAlchemy for database interactions
- PostgreSQL database
- Python 3.11+

**Chat Implementation:**
- `/api/chat` endpoint for processing user messages
- Agentic capabilities using OpenAI function calling
- Function definitions for inventory queries, recommendations, and product information
- ML model integration for product risk prediction and recommendation generation
- Fallback mechanisms when AI services are unavailable

**Key Features:**
- RESTful API endpoints for all application functionality
- Product management with expiration tracking
- Recommendation generation
- Agentic chat interface for natural language queries and data exploration
- Extensive API documentation via Swagger/OpenAPI

**Directory Structure:**
```
backend/
├── app/                    # Main application code
│   ├── models/             # Pydantic models and database schemas
│   │   ├── agentic.py      # AI agent definitions with chat functions
│   │   ├── predictor.py    # ML model integration for chat predictions
│   │   ├── product.py      # Product data models
│   │   ├── db_models.py    # Database models
│   │   └── schemas.py      # API schemas
│   ├── routers/            # API routes organized by domain
│   │   ├── chat.py         # Chat endpoint implementation
│   │   ├── products.py     # Product endpoints
│   │   └── recommendations.py  # ML-powered recommendations
│   ├── database.py         # Database connection and session management
│   ├── __init__.py         # Package initialization
│   └── main.py             # Application entry point
├── db/                     # Database migrations and seed data
└── pyproject.toml          # Project dependencies and metadata
```

### Predictor (ML Models)

Contains machine learning models to predict product expiration and generate recommendations.

**Tech Stack:**
- scikit-learn and XGBoost for predictive modeling
- Prophet for time-series forecasting
- Pandas/NumPy for data processing
- Joblib for model serialization

**Integration with Chat:**
- The predictor service processes chat queries to provide AI-powered responses
- Risk classification model helps identify products at risk of expiration
- Time-series models forecast optimal timing for promotions or inventory transfers
- Recommendation engine suggests actions based on product analysis

**Directory Structure:**
```
predictor/
├── src/                    # Source code
│   ├── data/               # Data processing utilities
│   ├── models/             # ML model implementations
│   │   ├── risk_classifier.py  # Product risk classification 
│   │   ├── time_series.py      # Time series forecasting
│   │   └── recommender.py      # Recommendation generation
│   └── utils/              # Utility functions
├── notebooks/              # Jupyter notebooks for research and model development
├── scripts/                # Automation scripts for training and evaluation
└── pyproject.toml          # Project dependencies and metadata
```

## Getting Started

### Using Docker (Recommended)

The easiest way to get started with SmartShelf is using Docker and Docker Compose.

#### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

#### Starting the Application

For production mode (optimized build):

```bash
# Build and start all services
docker-compose up --build
```

For development mode (with hot reloading):

```bash
# Build and start all services in development mode
docker-compose -f docker-compose.dev.yml up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

#### Stopping the Application

```bash
# Stop all services
docker-compose down

# Or for development mode
docker-compose -f docker-compose.dev.yml down
```

### Manual Setup (Alternative)

If you prefer to set up the application manually, you can use the following instructions.

#### Prerequisites

- [Python 3.11+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [PostgreSQL](https://www.postgresql.org/download/)

#### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/smartshelf.git
cd smartshelf

# Create and activate a virtual environment
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Set up environment variables
# Create a .env file with database connection details and other config
# Make sure to add your OpenAI API key for chat functionality

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

This will start the development server at http://localhost:3000.

#### Predictor Setup

```bash
cd predictor
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .

# Train models (optional)
python scripts/train_models.py
```

## Using the Chat Assistant

The SmartShelf Chat Assistant provides a natural language interface to interact with your inventory data:

1. **Accessing the Chat**: Click on the chat bubble in the bottom right corner of any page
2. **Asking Questions**: You can ask about:
   - Products nearing expiration
   - Inventory levels at different stores
   - Recommendations for promotions or transfers
   - General inventory statistics and trends
3. **AI-Powered Responses**: The assistant uses:
   - OpenAI's function calling API for precise data access
   - ML models to provide predictive insights
   - Natural language processing to understand complex queries

Example questions you can ask:
- "What products are expiring soon in the Pinheiros store?"
- "Show me high-risk items in the Tintas category"
- "What promotions should I create this week?"
- "Should I transfer any products between stores?"

## API Documentation

Once the backend is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

The API provides endpoints for:
- Product management
- Chat integration
- ML-powered recommendations

## Environment Variables

The application uses the following environment variables:

### Backend

- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG`: Set to "true" to enable debug mode
- `SECRET_KEY`: Secret key for JWT token generation
- `OPENAI_API_KEY`: API key for OpenAI integration (required for agentic chat)

## Development

### Managing Python Dependencies

The backend and predictor packages use pyproject.toml for dependency management:

```bash
# Install the project in development mode
pip install -e ".[dev]"
```
