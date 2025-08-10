// Configuration for different environments
const config = {
  development: {
    apiUrl: 'http://localhost:8000'
  },
  production: {
    apiUrl: 'https://fitness-coach-production.up.railway.app'
  }
};

// Get current environment
const environment = import.meta.env.MODE || 'development';

// Export the appropriate config
export const apiUrl = config[environment].apiUrl;

// For backward compatibility
if (typeof window !== 'undefined') {
  window.__VITE_API__ = apiUrl;
}
