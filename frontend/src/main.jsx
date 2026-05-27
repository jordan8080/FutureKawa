import { StrictMode, Component } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }
  static getDerivedStateFromError(error) {
    return { error }
  }
  render() {
    if (this.state.error) {
      return (
        <div style={{ background: '#030712', color: '#f87171', padding: '32px', fontFamily: 'monospace', minHeight: '100vh' }}>
          <h2 style={{ color: '#fbbf24', fontSize: '20px', marginBottom: '16px' }}>Erreur de rendu React</h2>
          <pre style={{ background: '#111827', padding: '16px', borderRadius: '8px', overflow: 'auto', fontSize: '13px', color: '#f87171' }}>
            {this.state.error.message}
            {'\n\n'}
            {this.state.error.stack}
          </pre>
        </div>
      )
    }
    return this.props.children
  }
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
