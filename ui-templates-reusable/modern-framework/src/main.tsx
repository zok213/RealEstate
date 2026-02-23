import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './styles/design-system.css'
import App from './App.tsx'
// import TestMapView from './TestMapView.tsx'
import ProfessionalMapDemo from './ProfessionalMapDemo.tsx'

// Check URL to determine which component to render
const urlParams = new URLSearchParams(window.location.search);
const viewMode = urlParams.get('view');

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {viewMode === 'professional' ? <ProfessionalMapDemo /> : <App />}
    {/* Use ?view=professional in URL to see Professional CAD-style Map */}
    {/* Uncomment below to test Design Mode MapView */}
    {/* <TestMapView /> */}
  </StrictMode>,
)
