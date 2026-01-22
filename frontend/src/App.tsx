import { BrowserRouter, Routes, Route } from 'react-router-dom'
import MainLayout from './components/layout/MainLayout'
import Dashboard from './pages/Dashboard'
import PipelineControl from './pages/PipelineControl'
import ModelGallery from './pages/ModelGallery'
import TabletGallery from './pages/TabletGallery'
import DetectionInspector from './pages/DetectionInspector'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/pipeline" element={<PipelineControl />} />
          <Route path="/models" element={<ModelGallery />} />
          <Route path="/tablets" element={<TabletGallery />} />
          <Route path="/detection" element={<DetectionInspector />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
