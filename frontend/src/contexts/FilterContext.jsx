/**
 * Filter Context
 * 
 * Global state management for user filters and preferences.
 * Handles favorite stores, blocked stores, hidden categories, and location preferences.
 */

import { createContext, useContext, useCallback, useMemo } from 'react';
import { useLocalStorage } from '../hooks/useLocalStorage';

// Create the context
const FilterContext = createContext();

// Default filter state
const defaultFilters = {
  favoriteStores: [],
  blockedStores: [],
  hiddenCategories: [],
  maxDistance: 10, // km
  minDiscount: 0, // percentage
  sortBy: 'distance', // distance, price, discount, name
  showExpiredDeals: false,
  preferredView: 'grid' // grid, list
};

/**
 * Filter Context Provider
 */
export function FilterProvider({ children }) {
  const [filters, setFilters] = useLocalStorage('userFilters', defaultFilters);

  // Update specific filter
  const updateFilter = useCallback((key, value) => {
    setFilters(prevFilters => ({
      ...prevFilters,
      [key]: value
    }));
  }, [setFilters]);

  // Update multiple filters at once
  const updateFilters = useCallback((newFilters) => {
    setFilters(prevFilters => ({
      ...prevFilters,
      ...newFilters
    }));
  }, [setFilters]);

  // Reset filters to defaults
  const resetFilters = useCallback(() => {
    setFilters(defaultFilters);
  }, [setFilters]);

  // Store management
  const toggleFavoriteStore = useCallback((storeId) => {
    setFilters(prevFilters => {
      const favoriteStores = prevFilters.favoriteStores || [];
      const isCurrentlyFavorite = favoriteStores.includes(storeId);
      
      return {
        ...prevFilters,
        favoriteStores: isCurrentlyFavorite
          ? favoriteStores.filter(id => id !== storeId)
          : [...favoriteStores, storeId],
        // Remove from blocked if adding to favorites
        blockedStores: isCurrentlyFavorite 
          ? prevFilters.blockedStores 
          : (prevFilters.blockedStores || []).filter(id => id !== storeId)
      };
    });
  }, [setFilters]);

  const toggleBlockedStore = useCallback((storeId) => {
    setFilters(prevFilters => {
      const blockedStores = prevFilters.blockedStores || [];
      const isCurrentlyBlocked = blockedStores.includes(storeId);
      
      return {
        ...prevFilters,
        blockedStores: isCurrentlyBlocked
          ? blockedStores.filter(id => id !== storeId)
          : [...blockedStores, storeId],
        // Remove from favorites if blocking
        favoriteStores: isCurrentlyBlocked 
          ? prevFilters.favoriteStores 
          : (prevFilters.favoriteStores || []).filter(id => id !== storeId)
      };
    });
  }, [setFilters]);

  // Category management
  const toggleHiddenCategory = useCallback((category) => {
    setFilters(prevFilters => {
      const hiddenCategories = prevFilters.hiddenCategories || [];
      const isCurrentlyHidden = hiddenCategories.includes(category);
      
      return {
        ...prevFilters,
        hiddenCategories: isCurrentlyHidden
          ? hiddenCategories.filter(cat => cat !== category)
          : [...hiddenCategories, category]
      };
    });
  }, [setFilters]);

  // Computed values
  const computedValues = useMemo(() => {
    const favoriteStores = filters.favoriteStores || [];
    const blockedStores = filters.blockedStores || [];
    const hiddenCategories = filters.hiddenCategories || [];

    return {
      hasFavoriteStores: favoriteStores.length > 0,
      hasBlockedStores: blockedStores.length > 0,
      hasHiddenCategories: hiddenCategories.length > 0,
      hasActiveFilters: (
        favoriteStores.length > 0 ||
        blockedStores.length > 0 ||
        hiddenCategories.length > 0 ||
        filters.maxDistance !== defaultFilters.maxDistance ||
        filters.minDiscount !== defaultFilters.minDiscount
      ),
      
      // Helper functions
      isFavoriteStore: (storeId) => favoriteStores.includes(storeId),
      isBlockedStore: (storeId) => blockedStores.includes(storeId),
      isCategoryHidden: (category) => hiddenCategories.includes(category),
      
      // Filter functions for data
      shouldShowStore: (store) => {
        if (!store) return false;
        
        // Don't show blocked stores
        if (blockedStores.includes(store.id)) return false;
        
        // If there are favorite stores, prioritize them but don't exclude others
        // (favorites just get shown first in sorting)
        return true;
      },
      
      shouldShowDeal: (deal) => {
        if (!deal) return false;
        
        // Don't show deals from blocked stores
        if (deal.store_id && blockedStores.includes(deal.store_id)) return false;
        
        // Don't show hidden categories
        if (deal.category && hiddenCategories.includes(deal.category)) return false;
        
        // Check minimum discount
        if (filters.minDiscount > 0 && (deal.discount_percent || 0) < filters.minDiscount) return false;
        
        // Check expired deals
        if (!filters.showExpiredDeals && deal.sale_end) {
          const endDate = new Date(deal.sale_end);
          if (endDate < new Date()) return false;
        }
        
        return true;
      }
    };
  }, [filters]);

  // Sort function
  const sortData = useCallback((data, type = 'deals') => {
    if (!Array.isArray(data)) return data;
    
    const { favoriteStores } = filters;
    
    return [...data].sort((a, b) => {
      // Always put favorites first (for stores)
      if (type === 'stores') {
        const aIsFavorite = favoriteStores.includes(a.id);
        const bIsFavorite = favoriteStores.includes(b.id);
        
        if (aIsFavorite && !bIsFavorite) return -1;
        if (!aIsFavorite && bIsFavorite) return 1;
      }
      
      // Then sort by selected criteria
      switch (filters.sortBy) {
        case 'distance':
          if (a.distance !== undefined && b.distance !== undefined) {
            return (a.distance || 999) - (b.distance || 999);
          }
          break;
          
        case 'price':
          if (a.price !== undefined && b.price !== undefined) {
            return a.price - b.price;
          }
          break;
          
        case 'discount': {
          const aDiscount = a.discount_percent || 0;
          const bDiscount = b.discount_percent || 0;
          return bDiscount - aDiscount; // Higher discount first
        }
          
        case 'name': {
          const aName = a.name || '';
          const bName = b.name || '';
          return aName.localeCompare(bName);
        }
          
        default:
          break;
      }
      
      return 0;
    });
  }, [filters]);

  // Context value
  const contextValue = useMemo(() => ({
    // State
    filters,
    
    // Actions
    updateFilter,
    updateFilters,
    resetFilters,
    toggleFavoriteStore,
    toggleBlockedStore,
    toggleHiddenCategory,
    sortData,
    
    // Computed values
    ...computedValues
  }), [
    filters,
    updateFilter,
    updateFilters,
    resetFilters,
    toggleFavoriteStore,
    toggleBlockedStore,
    toggleHiddenCategory,
    sortData,
    computedValues
  ]);

  return (
    <FilterContext.Provider value={contextValue}>
      {children}
    </FilterContext.Provider>
  );
}

/**
 * Hook to use the filter context
 */
export function useFilters() {
  const context = useContext(FilterContext);
  
  if (!context) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  
  return context;
}

/**
 * Hook to use filter state only (for performance)
 */
export function useFilterState() {
  const context = useContext(FilterContext);
  
  if (!context) {
    throw new Error('useFilterState must be used within a FilterProvider');
  }
  
  return context.filters;
}

export default FilterContext;