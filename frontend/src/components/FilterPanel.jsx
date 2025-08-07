/**
 * FilterPanel Component
 * 
 * Advanced filtering interface for customizing deal display preferences.
 * Includes price ranges, categories, distance, discount thresholds, and store preferences.
 */

import { useState, useEffect } from 'react';
import { 
  X, 
  Filter,
  DollarSign,
  MapPin,
  Percent,
  Store,
  Calendar,
  Sliders,
  RotateCcw,
  Check,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { useFilters } from '../contexts/FilterContext';

export default function FilterPanel({ 
  isOpen, 
  onClose, 
  className = '' 
}) {
  const { filters, updateFilters, resetFilters } = useFilters();
  const [localFilters, setLocalFilters] = useState(filters);
  const [expandedSections, setExpandedSections] = useState({
    price: true,
    location: true,
    discount: true,
    stores: false,
    categories: false,
    time: false
  });

  // Sync local filters with global filters when panel opens
  useEffect(() => {
    if (isOpen) {
      setLocalFilters(filters);
    }
  }, [isOpen, filters]);

  const updateLocalFilter = (key, value) => {
    setLocalFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleApplyFilters = () => {
    updateFilters(localFilters);
    onClose();
  };

  const handleResetFilters = () => {
    const resetValues = {
      minPrice: 0,
      maxPrice: 100,
      maxDistance: 10,
      minDiscount: 0,
      categories: [],
      blockedStores: [],
      favoriteStores: [],
      showExpired: false,
      sortBy: 'discount',
      sortOrder: 'desc'
    };
    setLocalFilters(resetValues);
    resetFilters();
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const categoryOptions = [
    'Produce', 'Meat & Seafood', 'Dairy & Eggs', 'Bakery',
    'Frozen', 'Pantry', 'Beverages', 'Health & Beauty',
    'Household', 'Baby', 'Pet', 'Other'
  ];

  const commonStores = [
    'Walmart', 'Metro', 'Sobeys', 'Loblaws', 'No Frills',
    'FreshCo', 'Food Basics', 'IGA', 'Safeway', 'Save-On-Foods'
  ];

  if (!isOpen) return null;

  return (
    <div className={`fixed inset-0 z-50 ${className}`}>
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Panel */}
      <div className="absolute right-0 top-0 h-full w-full max-w-md bg-white shadow-xl">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-neutral-200">
            <div className="flex items-center space-x-3">
              <Filter className="h-5 w-5 text-primary-600" />
              <h2 className="text-lg font-semibold text-neutral-900">
                Filter Deals
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* Price Range */}
            <div className="space-y-3">
              <button
                onClick={() => toggleSection('price')}
                className="flex items-center justify-between w-full text-left"
              >
                <div className="flex items-center space-x-2">
                  <DollarSign className="h-4 w-4 text-neutral-500" />
                  <span className="font-medium text-neutral-900">Price Range</span>
                </div>
                {expandedSections.price ? (
                  <ChevronUp className="h-4 w-4 text-neutral-400" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-neutral-400" />
                )}
              </button>
              
              {expandedSections.price && (
                <div className="space-y-4 pl-6">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-1">
                        Min Price
                      </label>
                      <div className="relative">
                        <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-500 text-sm">
                          $
                        </span>
                        <input
                          type="number"
                          min="0"
                          step="0.50"
                          value={localFilters.minPrice}
                          onChange={(e) => updateLocalFilter('minPrice', parseFloat(e.target.value) || 0)}
                          className="w-full pl-8 pr-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-1">
                        Max Price
                      </label>
                      <div className="relative">
                        <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-500 text-sm">
                          $
                        </span>
                        <input
                          type="number"
                          min="0"
                          step="0.50"
                          value={localFilters.maxPrice}
                          onChange={(e) => updateLocalFilter('maxPrice', parseFloat(e.target.value) || 100)}
                          className="w-full pl-8 pr-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                  </div>
                  
                  {/* Price Range Slider */}
                  <div className="px-2">
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={localFilters.maxPrice}
                      onChange={(e) => updateLocalFilter('maxPrice', parseFloat(e.target.value))}
                      className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer slider"
                    />
                    <div className="flex justify-between text-xs text-neutral-500 mt-1">
                      <span>$0</span>
                      <span>$100+</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Distance */}
            <div className="space-y-3">
              <button
                onClick={() => toggleSection('location')}
                className="flex items-center justify-between w-full text-left"
              >
                <div className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4 text-neutral-500" />
                  <span className="font-medium text-neutral-900">Distance</span>
                </div>
                {expandedSections.location ? (
                  <ChevronUp className="h-4 w-4 text-neutral-400" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-neutral-400" />
                )}
              </button>
              
              {expandedSections.location && (
                <div className="space-y-3 pl-6">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      Maximum Distance: {localFilters.maxDistance}km
                    </label>
                    <input
                      type="range"
                      min="1"
                      max="50"
                      value={localFilters.maxDistance}
                      onChange={(e) => updateLocalFilter('maxDistance', parseInt(e.target.value))}
                      className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer slider"
                    />
                    <div className="flex justify-between text-xs text-neutral-500 mt-1">
                      <span>1km</span>
                      <span>50km</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Minimum Discount */}
            <div className="space-y-3">
              <button
                onClick={() => toggleSection('discount')}
                className="flex items-center justify-between w-full text-left"
              >
                <div className="flex items-center space-x-2">
                  <Percent className="h-4 w-4 text-neutral-500" />
                  <span className="font-medium text-neutral-900">Minimum Discount</span>
                </div>
                {expandedSections.discount ? (
                  <ChevronUp className="h-4 w-4 text-neutral-400" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-neutral-400" />
                )}
              </button>
              
              {expandedSections.discount && (
                <div className="space-y-3 pl-6">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      Minimum Discount: {localFilters.minDiscount}%
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="75"
                      step="5"
                      value={localFilters.minDiscount}
                      onChange={(e) => updateLocalFilter('minDiscount', parseInt(e.target.value))}
                      className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer slider"
                    />
                    <div className="flex justify-between text-xs text-neutral-500 mt-1">
                      <span>0%</span>
                      <span>75%</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Categories */}
            <div className="space-y-3">
              <button
                onClick={() => toggleSection('categories')}
                className="flex items-center justify-between w-full text-left"
              >
                <div className="flex items-center space-x-2">
                  <Sliders className="h-4 w-4 text-neutral-500" />
                  <span className="font-medium text-neutral-900">Categories</span>
                  {localFilters.categories?.length > 0 && (
                    <span className="bg-primary-100 text-primary-600 px-2 py-0.5 rounded-full text-xs font-medium">
                      {localFilters.categories.length}
                    </span>
                  )}
                </div>
                {expandedSections.categories ? (
                  <ChevronUp className="h-4 w-4 text-neutral-400" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-neutral-400" />
                )}
              </button>
              
              {expandedSections.categories && (
                <div className="space-y-2 pl-6 max-h-48 overflow-y-auto">
                  {categoryOptions.map(category => (
                    <label key={category} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={localFilters.categories?.includes(category) || false}
                        onChange={(e) => {
                          const categories = localFilters.categories || [];
                          if (e.target.checked) {
                            updateLocalFilter('categories', [...categories, category]);
                          } else {
                            updateLocalFilter('categories', categories.filter(c => c !== category));
                          }
                        }}
                        className="w-4 h-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500"
                      />
                      <span className="text-sm text-neutral-700">{category}</span>
                    </label>
                  ))}
                </div>
              )}
            </div>

            {/* Stores */}
            <div className="space-y-3">
              <button
                onClick={() => toggleSection('stores')}
                className="flex items-center justify-between w-full text-left"
              >
                <div className="flex items-center space-x-2">
                  <Store className="h-4 w-4 text-neutral-500" />
                  <span className="font-medium text-neutral-900">Store Preferences</span>
                </div>
                {expandedSections.stores ? (
                  <ChevronUp className="h-4 w-4 text-neutral-400" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-neutral-400" />
                )}
              </button>
              
              {expandedSections.stores && (
                <div className="space-y-4 pl-6">
                  {/* Favorite Stores */}
                  <div>
                    <h4 className="text-sm font-medium text-neutral-700 mb-2">
                      Favorite Stores
                    </h4>
                    <div className="space-y-2 max-h-32 overflow-y-auto">
                      {commonStores.map(store => (
                        <label key={store} className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={localFilters.favoriteStores?.includes(store) || false}
                            onChange={(e) => {
                              const favorites = localFilters.favoriteStores || [];
                              if (e.target.checked) {
                                updateLocalFilter('favoriteStores', [...favorites, store]);
                              } else {
                                updateLocalFilter('favoriteStores', favorites.filter(s => s !== store));
                              }
                            }}
                            className="w-4 h-4 text-green-600 border-neutral-300 rounded focus:ring-green-500"
                          />
                          <span className="text-sm text-neutral-700">{store}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Blocked Stores */}
                  <div>
                    <h4 className="text-sm font-medium text-neutral-700 mb-2">
                      Hide Stores
                    </h4>
                    <div className="space-y-2 max-h-32 overflow-y-auto">
                      {commonStores.map(store => (
                        <label key={store} className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={localFilters.blockedStores?.includes(store) || false}
                            onChange={(e) => {
                              const blocked = localFilters.blockedStores || [];
                              if (e.target.checked) {
                                updateLocalFilter('blockedStores', [...blocked, store]);
                              } else {
                                updateLocalFilter('blockedStores', blocked.filter(s => s !== store));
                              }
                            }}
                            className="w-4 h-4 text-red-600 border-neutral-300 rounded focus:ring-red-500"
                          />
                          <span className="text-sm text-neutral-700">{store}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Time Preferences */}
            <div className="space-y-3">
              <button
                onClick={() => toggleSection('time')}
                className="flex items-center justify-between w-full text-left"
              >
                <div className="flex items-center space-x-2">
                  <Calendar className="h-4 w-4 text-neutral-500" />
                  <span className="font-medium text-neutral-900">Time Preferences</span>
                </div>
                {expandedSections.time ? (
                  <ChevronUp className="h-4 w-4 text-neutral-400" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-neutral-400" />
                )}
              </button>
              
              {expandedSections.time && (
                <div className="space-y-3 pl-6">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={localFilters.showExpired || false}
                      onChange={(e) => updateLocalFilter('showExpired', e.target.checked)}
                      className="w-4 h-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500"
                    />
                    <span className="text-sm text-neutral-700">
                      Show expired deals
                    </span>
                  </label>
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-neutral-200 bg-neutral-50">
            <div className="flex space-x-3">
              <button
                onClick={handleResetFilters}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 border border-neutral-300 text-neutral-700 rounded-lg hover:bg-neutral-100 transition-colors"
              >
                <RotateCcw className="h-4 w-4" />
                <span>Reset</span>
              </button>
              
              <button
                onClick={handleApplyFilters}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                <Check className="h-4 w-4" />
                <span>Apply Filters</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #22c55e;
          cursor: pointer;
          border: 2px solid #fff;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .slider::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #22c55e;
          cursor: pointer;
          border: 2px solid #fff;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
      `}</style>
    </div>
  );
}