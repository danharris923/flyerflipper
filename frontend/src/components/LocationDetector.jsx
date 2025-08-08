/**
 * LocationDetector Component
 * 
 * Handles user location detection with permission requests and error handling.
 * Provides a clean UI for location access and manual location entry.
 */

import { useState, useEffect } from 'react';
import { MapPin, Loader2, AlertCircle, RefreshCw, Navigation } from 'lucide-react';
import { useLocation } from '../hooks/useLocation';

export default function LocationDetector({ onLocationDetected, className = '' }) {
  const {
    location,
    loading,
    error,
    isSupported,
    requestLocation,
    clearLocation,
    needsRefresh,
    hasLocation,
    isStale
  } = useLocation();

  const [manualEntry, setManualEntry] = useState(false);
  const [postalCode, setPostalCode] = useState('');
  const [postalCodeError, setPostalCodeError] = useState('');

  // Notify parent when location changes
  useEffect(() => {
    if (location && onLocationDetected) {
      onLocationDetected(location);
    }
  }, [location, onLocationDetected]);

  // Reset manual entry when component mounts
  useEffect(() => {
    setManualEntry(false);
    setPostalCode('');
    setPostalCodeError('');
  }, []);

  // Canadian postal code validation
  const validatePostalCode = (code) => {
    const canadianPostalRegex = /^[A-Z]\d[A-Z]\s?\d[A-Z]\d$/i;
    return canadianPostalRegex.test(code.replace(/\s/g, ''));
  };

  const handlePostalCodeSubmit = async (e) => {
    e.preventDefault();
    const cleanCode = postalCode.replace(/\s/g, '').toUpperCase();
    
    if (!validatePostalCode(cleanCode)) {
      setPostalCodeError('Please enter a valid Canadian postal code (e.g., K1A 0A6)');
      return;
    }

    setPostalCodeError('');
    
    // Format postal code with space for display
    const formattedCode = cleanCode.slice(0, 3) + ' ' + cleanCode.slice(3);
    
    // Create location object with postal code
    // The backend will handle geocoding if needed
    const postalLocation = {
      postalCode: cleanCode,
      city: `Postal Code: ${formattedCode}`,
      timestamp: Date.now(),
      source: 'postal_code'
    };

    onLocationDetected?.(postalLocation);
    setManualEntry(false);
    setPostalCode('');
  };

  const handleLocationRequest = async () => {
    try {
      await requestLocation();
    } catch (err) {
      console.error('Location request failed:', err);
    }
  };

  if (!isSupported) {
    return (
      <div className={`bg-yellow-50 border border-yellow-200 rounded-xl p-6 ${className}`}>
        <div className="flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="text-sm font-medium text-yellow-800 mb-2">
              Location Not Supported
            </h3>
            <p className="text-sm text-yellow-700 mb-3">
              Your browser doesn&apos;t support location services. You can still use FlyerFlutter by entering your postal code.
            </p>
            <button
              onClick={() => setManualEntry(true)}
              className="text-sm bg-yellow-600 text-white px-3 py-1.5 rounded-lg hover:bg-yellow-700 transition-colors"
            >
              Enter Postal Code
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (manualEntry) {
    return (
      <div className={`bg-white border border-neutral-200 rounded-xl p-6 shadow-soft ${className}`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-neutral-900">Enter Your Location</h3>
          <button
            onClick={() => {
              setManualEntry(false);
              setPostalCodeError('');
              setPostalCode('');
            }}
            className="text-neutral-500 hover:text-neutral-700"
          >
            Cancel
          </button>
        </div>

        <form onSubmit={handlePostalCodeSubmit} className="space-y-4">
          <div>
            <label htmlFor="postalCode" className="block text-sm font-medium text-neutral-700 mb-2">
              Canadian Postal Code
            </label>
            <input
              id="postalCode"
              type="text"
              value={postalCode}
              onChange={(e) => {
                setPostalCode(e.target.value);
                setPostalCodeError('');
              }}
              placeholder="K1A 0A6"
              className={`
                w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent
                ${postalCodeError ? 'border-red-300' : 'border-neutral-300'}
              `}
            />
            {postalCodeError && (
              <p className="text-sm text-red-600 mt-1">{postalCodeError}</p>
            )}
          </div>

          <div className="flex space-x-3">
            <button
              type="submit"
              className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              Use This Location
            </button>
            {isSupported && (
              <button
                type="button"
                onClick={() => setManualEntry(false)}
                className="px-4 py-2 border border-neutral-300 text-neutral-700 rounded-lg hover:bg-neutral-50 transition-colors"
              >
                Use GPS Instead
              </button>
            )}
          </div>
        </form>
      </div>
    );
  }

  if (hasLocation && !isStale) {
    return (
      <div className={`bg-green-50 border border-green-200 rounded-xl p-4 ${className}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-green-100 p-2 rounded-lg">
              <MapPin className="h-4 w-4 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-green-800">
                Location detected
              </p>
              <p className="text-xs text-green-600">
                {location.postalCode ? 
                  `Postal Code: ${location.postalCode.slice(0,3)} ${location.postalCode.slice(3)}` : 
                  location.city || `${location.lat?.toFixed(4)}, ${location.lng?.toFixed(4)}`
                }
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => {
                setManualEntry(true);
                setPostalCode('');
              }}
              className="text-xs text-green-700 hover:text-green-800 px-2 py-1 rounded hover:bg-green-100 transition-colors"
            >
              Change
            </button>
            {needsRefresh() && location.source !== 'postal_code' && (
              <button
                onClick={handleLocationRequest}
                disabled={loading}
                className="flex items-center space-x-1 text-xs text-green-700 hover:text-green-800 px-2 py-1 rounded hover:bg-green-100 transition-colors"
              >
                <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-xl p-6 ${className}`}>
        <div className="flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="text-sm font-medium text-red-800 mb-1">
              Location Access Required
            </h3>
            <p className="text-sm text-red-700 mb-1">
              {error.message}
            </p>
            {error.suggestion && (
              <p className="text-xs text-red-600 mb-3">
                {error.suggestion}
              </p>
            )}
            <div className="flex space-x-2">
              <button
                onClick={handleLocationRequest}
                disabled={loading}
                className="flex items-center space-x-2 text-sm bg-red-600 text-white px-3 py-1.5 rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Navigation className="h-4 w-4" />
                )}
                <span>Try Again</span>
              </button>
              <button
                onClick={() => setManualEntry(true)}
                className="text-sm border border-red-300 text-red-700 px-3 py-1.5 rounded-lg hover:bg-red-100 transition-colors"
              >
                Enter Postal Code
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Initial state - request location
  return (
    <div className={`bg-white border-2 border-dashed border-neutral-300 rounded-xl p-8 text-center ${className}`}>
      <div className="max-w-md mx-auto">
        <div className="bg-primary-100 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
          <MapPin className="h-8 w-8 text-primary-600" />
        </div>

        <h3 className="text-lg font-semibold text-neutral-900 mb-2">
          Find Deals Near You
        </h3>
        <p className="text-neutral-600 mb-6">
          Allow location access to discover grocery stores and deals in your area, or enter your postal code manually.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={handleLocationRequest}
            disabled={loading}
            className="flex items-center justify-center space-x-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 font-medium"
          >
            {loading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Navigation className="h-5 w-5" />
            )}
            <span>{loading ? 'Getting Location...' : 'Use My Location'}</span>
          </button>

          <button
            onClick={() => setManualEntry(true)}
            className="flex items-center justify-center space-x-2 border border-neutral-300 text-neutral-700 px-6 py-3 rounded-lg hover:bg-neutral-50 transition-colors"
          >
            <MapPin className="h-5 w-5" />
            <span>Enter Postal Code</span>
          </button>
        </div>

        <p className="text-xs text-neutral-500 mt-4">
          Your location is only used to find nearby stores and is stored locally on your device.
        </p>
      </div>
    </div>
  );
}