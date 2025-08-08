/**
 * useLocation Hook
 * 
 * A React hook for geolocation functionality with error handling and persistence.
 * Manages user location detection, storage, and refresh capabilities.
 */

import { useState, useEffect, useCallback } from 'react';
import { useLocalStorage } from './useLocalStorage';

/**
 * Custom hook for managing user geolocation
 * 
 * @param {Object} options - Geolocation options
 * @returns {Object} Location state and methods
 */
export function useLocation(options = {}) {
  const defaultOptions = {
    enableHighAccuracy: true,
    timeout: 10000,
    maximumAge: 300000, // 5 minutes
    ...options
  };

  // Persistent location storage
  const [savedLocation, setSavedLocation, removeSavedLocation] = useLocalStorage('userLocation', null);
  
  // Current location state
  const [location, setLocation] = useState(savedLocation);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(savedLocation?.timestamp || null);

  // Check if geolocation is supported
  const isSupported = typeof navigator !== 'undefined' && 'geolocation' in navigator;

  /**
   * Get current position from browser
   */
  const getCurrentPosition = useCallback(() => {
    if (!isSupported) {
      setError({ 
        code: 'UNSUPPORTED', 
        message: 'Geolocation is not supported by this browser' 
      });
      return;
    }

    setLoading(true);
    setError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const locationData = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: Date.now()
        };

        setLocation(locationData);
        setSavedLocation(locationData);
        setLastUpdated(locationData.timestamp);
        setLoading(false);
        setError(null);
      },
      (error) => {
        let errorMessage = 'Failed to get location';
        let suggestion = '';
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location access blocked';
            suggestion = 'Please enable location permission in your browser settings, or enter your postal code instead.';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location temporarily unavailable';
            suggestion = 'Try again in a moment, or enter your postal code instead.';
            break;
          case error.TIMEOUT:
            errorMessage = 'Location request timed out';
            suggestion = 'Your GPS signal may be weak. Try again or enter your postal code.';
            break;
          default:
            errorMessage = 'Location detection failed';
            suggestion = 'Enter your postal code to find nearby deals.';
            break;
        }

        console.error('Geolocation error:', error);
        
        setError({ 
          code: error.code, 
          message: errorMessage,
          suggestion,
          originalError: error
        });
        setLoading(false);
      },
      defaultOptions
    );
  }, [isSupported, defaultOptions, setSavedLocation]);

  /**
   * Clear saved location
   */
  const clearLocation = useCallback(() => {
    setLocation(null);
    removeSavedLocation();
    setLastUpdated(null);
    setError(null);
  }, [removeSavedLocation]);

  /**
   * Check if location needs refresh (older than 5 minutes)
   */
  const needsRefresh = useCallback(() => {
    if (!lastUpdated) return true;
    const fiveMinutes = 5 * 60 * 1000;
    return (Date.now() - lastUpdated) > fiveMinutes;
  }, [lastUpdated]);

  /**
   * Request location with permission handling
   */
  const requestLocation = useCallback(() => {
    if (!isSupported) {
      setError({ 
        code: 'UNSUPPORTED', 
        message: 'Geolocation is not supported by this browser' 
      });
      return Promise.reject(new Error('Geolocation not supported'));
    }

    return new Promise((resolve, reject) => {
      setLoading(true);
      setError(null);

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const locationData = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: Date.now()
          };

          setLocation(locationData);
          setSavedLocation(locationData);
          setLastUpdated(locationData.timestamp);
          setLoading(false);
          resolve(locationData);
        },
        (error) => {
          let errorMessage = 'Failed to get location';
          
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = 'Location access denied. Please enable location access in your browser settings.';
              break;
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'Location information is unavailable. Please try again.';
              break;
            case error.TIMEOUT:
              errorMessage = 'Location request timed out. Please try again.';
              break;
            default:
              errorMessage = 'An unknown error occurred while getting your location.';
              break;
          }

          const errorObj = { 
            code: error.code, 
            message: errorMessage,
            originalError: error
          };

          setError(errorObj);
          setLoading(false);
          reject(errorObj);
        },
        defaultOptions
      );
    });
  }, [isSupported, defaultOptions, setSavedLocation]);

  /**
   * Watch position (for real-time updates)
   */
  const watchPosition = useCallback(() => {
    if (!isSupported) return null;

    const watchId = navigator.geolocation.watchPosition(
      (position) => {
        const locationData = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: Date.now()
        };

        setLocation(locationData);
        setSavedLocation(locationData);
        setLastUpdated(locationData.timestamp);
      },
      (error) => {
        console.warn('Watch position error:', error);
      },
      {
        ...defaultOptions,
        maximumAge: 60000 // 1 minute for watch
      }
    );

    return () => navigator.geolocation.clearWatch(watchId);
  }, [isSupported, defaultOptions, setSavedLocation]);

  // Auto-load saved location on mount
  useEffect(() => {
    if (savedLocation && !location) {
      setLocation(savedLocation);
      setLastUpdated(savedLocation.timestamp);
    }
  }, [savedLocation, location]);

  // Calculate distance between two coordinates (Haversine formula)
  const calculateDistance = useCallback((lat1, lng1, lat2, lng2) => {
    const R = 6371; // Radius of the Earth in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = 
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
      Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // Distance in kilometers
  }, []);

  return {
    // State
    location,
    loading,
    error,
    isSupported,
    lastUpdated,
    
    // Methods
    getCurrentPosition,
    requestLocation,
    clearLocation,
    needsRefresh,
    watchPosition,
    calculateDistance,
    
    // Computed values
    hasLocation: !!location,
    isStale: needsRefresh()
  };
}