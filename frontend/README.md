# Cuneiform Translator Frontend

React + TypeScript + Tailwind CSS web interface for the Cuneiform Translator pipeline.

## Features

- 📊 Real-time pipeline monitoring with WebSocket
- 🎨 Modern UI with Framer Motion animations
- 📈 Beautiful charts with Recharts
- 🖼️ Tablet gallery with search and filtering
- 🤖 Model comparison and management
- 🔍 Detection result inspection
- ⚡ Fast development with Vite

## Project Structure

```
frontend/
├── src/
│   ├── pages/              # Page components (7 main pages)
│   ├── components/
│   │   ├── layout/         # Header, Sidebar, MainLayout
│   │   ├── Card.tsx
│   │   ├── ProgressBar.tsx
│   │   └── StatCard.tsx
│   ├── stores/             # Zustand state management
│   │   ├── pipelineStore.ts
│   │   ├── uiStore.ts
│   │   └── authStore.ts
│   ├── hooks/              # Custom React hooks
│   │   ├── useAPI.ts       # API integration hooks
│   │   └── useWebSocket.ts # WebSocket hooks
│   ├── lib/
│   │   └── api.ts          # Axios client with interceptors
│   ├── App.tsx             # Main app component
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── public/                 # Static assets
├── index.html              # HTML template
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── tsconfig.json           # TypeScript configuration
└── package.json            # Dependencies

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Environment Variables

Create `.env.local`:
```
VITE_API_URL=http://localhost:5000/api
VITE_SOCKET_URL=http://localhost:5000
```

## Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Animations
- **Recharts** - Data visualization
- **Zustand** - State management
- **Socket.IO Client** - Real-time communication
- **Vite** - Build tool
- **React Router** - Navigation

## Pages

1. **Dashboard** - Overview and quick actions
2. **Pipeline Control** - Start and monitor runs
3. **Model Gallery** - Browse and compare models
4. **Tablet Gallery** - Search and view tablets
5. **Detection Inspector** - Visualize detection results
6. **Analytics** - Training metrics and statistics
7. **Settings** - Configuration options
