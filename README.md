# Smart Fridge AI Dashboard

A modern, mobile-friendly system that uses GPT-4 Vision and LLM multi-agent technology to monitor your refrigerator and provide intelligent insights.

## Features

- **React + Tailwind CSS** frontend with responsive design
- **FastAPI** backend with GPT-4 Vision and LLM integration
- Real-time sensor monitoring (temperature, gas, humidity)
- Food detection using computer vision
- AI-powered analysis for:
  - Food safety alerts
  - Freshness tracking
  - Recipe suggestions

## Project Structure

```
├── frontend/               # React frontend
│   ├── public/             # Static assets
│   └── src/
│       ├── components/     # UI components
│       ├── pages/          # Page components
│       └── utils/          # Utility functions
│
└── backend/                # FastAPI backend
    ├── agents/             # FridgeAgent LLM logic
    ├── data/               # Data storage
    ├── routes/             # API endpoints
    ├── services/           # Vision and other services
    └── utils/              # Utility functions
```

## Setup Instructions

### Frontend

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

### Backend

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install fastapi uvicorn openai python-dotenv
   ```

4. Set up your environment variables:
   ```
   cp .env.example .env
   # Edit .env to add your OpenAI API key
   ```

5. Start the server:
   ```
   uvicorn main:app --reload
   ```

## API Endpoints

- `POST /api/upload` - Upload sensor data and fridge image
- `GET /api/fridge-status` - Get current fridge status

## Technologies Used

- **Frontend**: React, Tailwind CSS
- **Backend**: FastAPI, OpenAI API (GPT-4 Vision)
- **Data**: JSON for storage

## License

MIT 