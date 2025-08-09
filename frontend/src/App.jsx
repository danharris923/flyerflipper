/**
 * Main App Component
 * 
 * Root component that handles layout, routing, and global state management.
 * Includes navigation, location detection, and deal display.
 */

import { useState, useEffect } from 'react';
import { 
  MapPin, 
  
  Filter,
  Menu,
  X,
  Home,
  Heart,
  Store as StoreIcon,
  Settings,
  Bell,
  User
} from 'lucide-react';
import { FilterProvider } from './contexts/FilterContext';
import LocationDetector from './components/LocationDetector';
import StoreCard from './components/StoreCard';
import DealList from './components/DealList';
import FilterPanel from './components/FilterPanel';
import { apiService } from './services/api';

// Header Component
function AppHeader({ 
  userLocation, 
  onLocationChange, 
  onFilterToggle, 
  showMobileNav,
  onMobileNavToggle 
}) {
  return (
    <header className="bg-white shadow-sm border-b border-neutral-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Mobile Menu */}
          <div className="flex items-center space-x-4">
            <button
              onClick={onMobileNavToggle}
              className="md:hidden p-2 text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 rounded-lg"
            >
              {showMobileNav ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
            
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-red-500 to-orange-500 rounded-lg flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-sm">🛒</span>
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl font-bold text-neutral-900">
                  FlyerFlutter
                </h1>
                <p className="text-xs text-neutral-500 -mt-1">Canadian Coupon Finder</p>
              </div>
            </div>
          </div>

          {/* Location Display */}
          <div className="flex-1 max-w-md mx-4">
            <div className="flex items-center space-x-2 px-3 py-2 bg-neutral-50 rounded-lg">
              <MapPin className="h-4 w-4 text-neutral-500 flex-shrink-0" />
              <span className="text-sm text-neutral-700 truncate">
                {userLocation 
                  ? `${userLocation.city || userLocation.postalCode || 'Unknown Location'}`
                  : 'Location not set'
                }
              </span>
              <button
                onClick={onLocationChange}
                className="text-xs text-primary-600 hover:text-primary-700 font-medium ml-2 flex-shrink-0"
              >
                Change
              </button>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-2">
            <button
              onClick={onFilterToggle}
              className="p-2 text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 rounded-lg"
            >
              <Filter className="h-5 w-5" />
            </button>
            
            <button className="p-2 text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 rounded-lg hidden sm:block">
              <Bell className="h-5 w-5" />
            </button>
            
            <button className="p-2 text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 rounded-lg hidden sm:block">
              <User className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

// Navigation Component
function AppNavigation({ showMobileNav, onClose }) {
  const navItems = [
    { icon: Home, label: 'Deals', active: true },
    { icon: StoreIcon, label: 'Stores', active: false },
    { icon: Heart, label: 'Favorites', active: false },
    { icon: Settings, label: 'Settings', active: false }
  ];

  return (
    <>
      {/* Mobile Navigation Overlay */}
      {showMobileNav && (
        <div className="fixed inset-0 z-30 md:hidden">
          <div 
            className="absolute inset-0 bg-black bg-opacity-50"
            onClick={onClose}
          />
          <nav className="absolute left-0 top-0 h-full w-64 bg-white shadow-xl">
            <div className="p-4">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">FF</span>
                </div>
                <span className="text-lg font-semibold text-neutral-900">FlyerFlutter</span>
              </div>
              
              <ul className="space-y-2">
                {navItems.map((item) => (
                  <li key={item.label}>
                    <button
                      className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                        item.active
                          ? 'bg-primary-50 text-primary-700 font-medium'
                          : 'text-neutral-700 hover:bg-neutral-100'
                      }`}
                    >
                      <item.icon className="h-5 w-5" />
                      <span>{item.label}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </nav>
        </div>
      )}

      {/* Desktop Navigation - Remove fixed sidebar that was overlapping content */}
    </>
  );
}

// Main App Component
export default function App() {
  // State management
  const [userLocation, setUserLocation] = useState(null);
  const [showLocationDetector, setShowLocationDetector] = useState(false);
  const [showFilterPanel, setShowFilterPanel] = useState(false);
  const [showMobileNav, setShowMobileNav] = useState(false);
  
  // Data state
  const [stores, setStores] = useState([]);
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Check for saved location and URL parameters on mount
  useEffect(() => {
    // Check for postal code in URL parameters first
    const urlParams = new URLSearchParams(window.location.search);
    const postalCodeParam = urlParams.get('postal_code');
    
    if (postalCodeParam) {
      // Use postal code from URL
      const location = {
        postalCode: postalCodeParam.replace(/\s/g, '').toUpperCase(),
        city: `Postal Code ${postalCodeParam}`,
        source: 'url_parameter'
      };
      setUserLocation(location);
      localStorage.setItem('userLocation', JSON.stringify(location));
    } else {
      // Check for saved location
      const savedLocation = localStorage.getItem('userLocation');
      if (savedLocation) {
        try {
          const location = JSON.parse(savedLocation);
          setUserLocation(location);
        } catch (e) {
          console.error('Failed to parse saved location:', e);
        }
      } else {
        setShowLocationDetector(true);
      }
    }
  }, []);

  // Load data when location changes
  useEffect(() => {
    if (userLocation && (userLocation.lat && userLocation.lng || userLocation.postalCode)) {
      loadStoresAndDeals();
    }
  }, [userLocation]);

  const loadStoresAndDeals = async () => {
    if (!userLocation || !(userLocation.lat && userLocation.lng || userLocation.postalCode)) return;

    setLoading(true);
    setError(null);

    try {
      // Load nearby stores using coordinates or postal code
      if (userLocation.lat && userLocation.lng) {
        // Use GPS coordinates
        const storesData = await apiService.getNearbyStores({
          lat: userLocation.lat,
          lng: userLocation.lng,
          radius: 20000, // 20km in meters
          maxResults: 20
        });
        setStores(storesData.stores || []);
      } else if (userLocation.postalCode) {
        // Use postal code - with fallback for backend compatibility
        try {
          const storesData = await apiService.getNearbyStores({
            postal_code: userLocation.postalCode,
            radius: 20000, // 20km in meters
            maxResults: 20
          });
          setStores(storesData.stores || []);
        } catch (error) {
          console.warn('Postal code stores API not yet deployed, skipping stores:', error);
          // Fallback: don't load stores for postal code until backend is updated
          setStores([]);
        }
      } else {
        // No location data available
        setStores([]);
      }

      // Load deals using the correct API (works with postal code or coordinates)
      // Get MORE deals to see all local stores in 20km radius
      const dealsData = await apiService.getDeals({
        lat: userLocation.lat,
        lng: userLocation.lng,
        postalCode: userLocation.postalCode,
        page: 1,
        perPage: 200, // Increased from 50 to see more stores
        refresh: false // Set to true for fresh data
      });
      setDeals(dealsData.items || []);

    } catch (err) {
      console.error('Failed to load data:', err);
      setError(err.response?.data?.detail || 'Failed to load deals and stores');
      setStores([]);
      setDeals([]);
    } finally {
      setLoading(false);
    }
  };

  const handleLocationDetected = (location) => {
    setUserLocation(location);
    setShowLocationDetector(false);
    localStorage.setItem('userLocation', JSON.stringify(location));
  };

  const handleLocationChange = () => {
    // Clear current location to allow re-selection
    setUserLocation(null);
    localStorage.removeItem('userLocation');
    setShowLocationDetector(true);
    // Clear any existing data
    setStores([]);
    setDeals([]);
    setError(null);
  };

  const handleFilterToggle = () => {
    setShowFilterPanel(!showFilterPanel);
  };

  const handleMobileNavToggle = () => {
    setShowMobileNav(!showMobileNav);
  };

  const closeMobileNav = () => {
    setShowMobileNav(false);
  };

  return (
    <FilterProvider>
      <div className="min-h-screen bg-neutral-50">
        {/* Header */}
        <AppHeader
          userLocation={userLocation}
          onLocationChange={handleLocationChange}
          onFilterToggle={handleFilterToggle}
          showMobileNav={showMobileNav}
          onMobileNavToggle={handleMobileNavToggle}
        />

        {/* Navigation */}
        <AppNavigation 
          showMobileNav={showMobileNav} 
          onClose={closeMobileNav}
        />

        {/* Main Content */}
        <main className="w-full">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {/* Location Detector Modal */}
            {showLocationDetector && (
              <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
                <div className="bg-white rounded-xl p-6 w-full max-w-md">
                  <h2 className="text-xl font-semibold text-neutral-900 mb-4">
                    Set Your Location
                  </h2>
                  <LocationDetector
                    onLocationDetected={handleLocationDetected}
                    className="w-full"
                  />
                  {userLocation && (
                    <button
                      onClick={() => setShowLocationDetector(false)}
                      className="mt-4 w-full px-4 py-2 border border-neutral-300 text-neutral-700 rounded-lg hover:bg-neutral-50 transition-colors"
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <X className="h-5 w-5 text-red-400" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">
                      Error loading data
                    </h3>
                    <div className="mt-1 text-sm text-red-700">
                      {error}
                    </div>
                    <div className="mt-3">
                      <button
                        onClick={loadStoresAndDeals}
                        className="text-sm font-medium text-red-800 hover:text-red-900"
                      >
                        Try again
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Welcome Message */}
            {!userLocation && !showLocationDetector && (
              <div className="relative overflow-hidden bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 rounded-2xl p-12 text-center">
                <div className="absolute inset-0 bg-white/60 backdrop-blur-sm"></div>
                <div className="relative z-10">
                  <div className="w-20 h-20 bg-gradient-to-br from-red-500 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl">
                    <span className="text-3xl">🛒💰</span>
                  </div>
                  <h2 className="text-3xl font-bold text-neutral-900 mb-4">
                    Welcome to FlyerFlutter
                  </h2>
                  <p className="text-lg text-neutral-700 mb-2 max-w-2xl mx-auto">
                    🇨🇦 Canada's Premier Grocery Coupon & Flyer Comparison App
                  </p>
                  <p className="text-neutral-600 mb-8 max-w-md mx-auto">
                    Compare weekly flyer deals across major Canadian grocery chains. 
                    Save money on your groceries every Wednesday when new flyers drop!
                  </p>
                  <button
                    onClick={handleLocationChange}
                    className="px-8 py-3 bg-gradient-to-r from-red-500 to-orange-500 text-white rounded-xl hover:from-red-600 hover:to-orange-600 transition-all duration-200 font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                  >
                    🎯 Find Deals Near Me
                  </button>
                  
                  <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
                    <div className="bg-white/80 rounded-lg p-4 backdrop-blur-sm">
                      <div className="text-2xl mb-2">🏪</div>
                      <p className="text-sm font-medium text-neutral-700">Real Store Data</p>
                    </div>
                    <div className="bg-white/80 rounded-lg p-4 backdrop-blur-sm">
                      <div className="text-2xl mb-2">📅</div>
                      <p className="text-sm font-medium text-neutral-700">Weekly Updates</p>
                    </div>
                    <div className="bg-white/80 rounded-lg p-4 backdrop-blur-sm">
                      <div className="text-2xl mb-2">💵</div>
                      <p className="text-sm font-medium text-neutral-700">Price Comparison</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Main Content Grid - Improved Layout */}
            {userLocation && (
              <div className="space-y-6">
                {/* Nearby Stores Section - Now Horizontal on Desktop */}
                <div className="bg-white rounded-xl shadow-soft p-6">
                  <h2 className="text-lg font-semibold text-neutral-900 mb-4">
                    Nearby Stores
                  </h2>
                  
                  {loading && stores.length === 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                      {[...Array(4)].map((_, i) => (
                        <div key={i} className="animate-pulse">
                          <div className="h-4 bg-neutral-200 rounded mb-2"></div>
                          <div className="h-3 bg-neutral-100 rounded w-3/4"></div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {stores.length === 0 ? (
                        <p className="text-neutral-500 text-sm">
                          No stores found nearby
                        </p>
                      ) : (
                        <>
                          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                            {stores.slice(0, 8).map((store) => (
                              <StoreCard
                                key={store.id}
                                store={store}
                                compact={true}
                              />
                            ))}
                          </div>
                          {stores.length > 8 && (
                            <div className="text-center">
                              <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                                View all stores ({stores.length})
                              </button>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  )}
                </div>

                {/* Deals List - Full Width */}
                <div className="w-full">
                  <DealList
                    deals={deals}
                    loading={loading}
                    error={null}
                    showFilters={true}
                    showSearch={true}
                    userLocation={userLocation}
                  />
                </div>
              </div>
            )}
          </div>
        </main>

        {/* Filter Panel */}
        <FilterPanel
          isOpen={showFilterPanel}
          onClose={() => setShowFilterPanel(false)}
        />
      </div>
    </FilterProvider>
  );
}