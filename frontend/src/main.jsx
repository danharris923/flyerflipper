/**
 * Main Entry Point
 * 
 * React application entry point with error boundary and performance monitoring.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('React Error Boundary caught an error:', error, errorInfo);
    
    // In production, you might want to send this to an error reporting service
    // Example: Sentry.captureException(error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-soft p-8 max-w-md w-full text-center">
            <div className="text-red-500 mb-4">
              <svg 
                className="h-12 w-12 mx-auto" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
                />
              </svg>
            </div>
            <h1 className="text-xl font-bold text-neutral-900 mb-2">
              Something went wrong
            </h1>
            <p className="text-neutral-600 mb-4">
              We encountered an unexpected error. Please refresh the page to try again.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              Refresh Page
            </button>
            {import.meta.env.DEV && (
              <details className="mt-4 text-left">
                <summary className="cursor-pointer text-sm text-neutral-500 hover:text-neutral-700">
                  Technical Details
                </summary>
                <pre className="mt-2 p-2 bg-neutral-100 rounded text-xs text-neutral-700 overflow-auto">
                  {this.state.error?.toString()}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Performance measurement (optional)
function measurePerformance() {
  // Mark the start of app rendering
  performance.mark('app-start');
  
  // Measure when the app is fully loaded
  window.addEventListener('load', () => {
    performance.mark('app-loaded');
    performance.measure('app-load-time', 'app-start', 'app-loaded');
    
    const measure = performance.getEntriesByName('app-load-time')[0];
    if (measure && import.meta.env.DEV) {
      console.warn(`🚀 App loaded in ${Math.round(measure.duration)}ms`);
    }
  });
}

// Initialize performance measurement
measurePerformance();

// Mount React application
const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);

// Hot module replacement for development
if (import.meta.hot) {
  import.meta.hot.accept('./App.jsx', (newApp) => {
    const NewApp = newApp.default;
    root.render(
      <React.StrictMode>
        <ErrorBoundary>
          <NewApp />
        </ErrorBoundary>
      </React.StrictMode>
    );
  });
}