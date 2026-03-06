import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import WidgetApp from './WidgetApp.tsx'

const isWidget = window.location.hash === '#widget';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {isWidget ? <WidgetApp /> : <App />}
  </StrictMode>,
)
