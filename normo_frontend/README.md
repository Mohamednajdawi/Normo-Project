# Normo Frontend

A modern React frontend for the Normo Legal Assistant - an AI-powered tool for Austrian building regulations and architectural requirements.

## Features

- 🏗️ **ChatGPT-style Interface** - Familiar and intuitive chat experience
- 📚 **Austrian Legal Documents** - Query real Austrian building codes and regulations  
- 🧮 **Calculation Detection** - Automatic highlighting of formulas and measurements
- 📖 **Source Citations** - Detailed references with page numbers and sections
- 🎨 **Modern Design** - Dark theme with smooth animations and responsive layout
- ⚡ **Real-time Chat** - Instant responses from the Normo backend API

## Prerequisites

- Node.js 16+ and npm
- Normo Backend running on `http://localhost:8000`

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

### Example Queries

Try asking questions like:

- "I am building apartment building with 5 flats in Linz. How many square meters of playground do I have to plan?"
- "What are the building height requirements in Austrian law?"
- "What waste management regulations apply in Upper Austria?"
- "What are the room height requirements for residential buildings?"

### Features in Action

- **Instant Responses**: Get detailed answers with exact calculations (e.g., 100 + 5×10 = 150 m²)
- **Legal Citations**: Every answer includes source references with PDF names, page numbers, and sections
- **Calculation Highlighting**: Formulas and measurements are automatically detected and highlighted
- **Professional Interface**: Clean, modern design similar to ChatGPT

## Configuration

The frontend connects to the backend via environment variables:

- `REACT_APP_API_URL`: Backend API URL (default: `http://localhost:8000`)

## Architecture

- **React 18** with TypeScript
- **Material-UI** for components and theming
- **Axios** for API communication
- **React Markdown** for formatted message display
- **Responsive Design** with mobile support

## Backend Integration

This frontend connects to the Normo Backend API endpoints:

- `POST /chat` - Send messages and receive responses
- `GET /health` - Check backend availability

## Development

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### Project Structure

```
src/
├── components/          # React components
│   ├── ChatInterface.tsx    # Main chat interface
│   ├── MessageBubble.tsx    # Individual message display
│   ├── MessageList.tsx      # Message list container
│   ├── CitationsList.tsx    # Source citations display
│   └── Sidebar.tsx          # Navigation sidebar
├── services/            # API services
│   └── api.ts              # Backend API integration
├── types/               # TypeScript definitions
│   └── api.ts              # API type definitions
└── App.tsx             # Main application component
```

## License

This project is part of the Normo Legal Assistant system.