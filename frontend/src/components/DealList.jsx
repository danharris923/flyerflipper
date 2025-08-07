/**
 * DealList Component
 * 
 * Displays a list of grocery deals with filtering, sorting, and comparison features.
 * Includes search, category filtering, and deal cards.
 */

import React, { useState, useMemo } from 'react';
import { 
  Search, 
  Filter, 
  Grid3X3, 
  List, 
  SortAsc, 
  SortDesc,
  Tag,
  Percent,
  DollarSign,
  Loader2,
  TrendingUp,
  Clock,
  Award
} from 'lucide-react';
import { useFilters } from '../contexts/FilterContext';
import DealCard from './DealCard';
import { apiService } from '../services/api';

// Price Comparison Modal Component
function PriceComparisonModal({ product, isOpen, onClose, userLocation }) {
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadComparison = async () => {
    if (!product || !isOpen) return;
    
    setLoading(true);
    try {
      const result = await apiService.compareDeals(
        product.name,
        userLocation?.postalCode
      );
      setComparison(result);
    } catch (error) {
      console.error('Failed to load comparison:', error);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (isOpen && product) {
      loadComparison();
    }
  }, [isOpen, product]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
        <div className="p-6 border-b border-neutral-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-neutral-900">
              Price Comparison: {product?.name}
            </h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
            >
              ✕
            </button>
          </div>
        </div>
        
        <div className="p-6 overflow-y-auto">
          {loading ? (
            <div className="text-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary-600 mx-auto mb-4" />
              <p>Comparing prices across stores...</p>
            </div>
          ) : comparison ? (
            <div className="space-y-4">
              {/* Best Deal */}
              <div className="bg-green-50 border-2 border-green-200 rounded-xl p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Award className="h-5 w-5 text-green-600" />
                  <span className="font-semibold text-green-800">Best Deal</span>
                </div>
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-semibold text-neutral-900">
                      {comparison.best_deal?.store_name}
                    </p>
                    <p className="text-sm text-neutral-600">
                      {comparison.best_deal?.name}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-green-600">
                      ${comparison.best_deal?.price}
                    </p>
                    {comparison.max_savings > 0 && (
                      <p className="text-sm text-green-700">
                        Save up to ${comparison.max_savings.toFixed(2)}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Other Deals */}
              {comparison.other_deals?.length > 0 && (
                <div className="space-y-3">
                  <h3 className="font-semibold text-neutral-900">Other Options</h3>
                  {comparison.other_deals.map((deal, index) => (
                    <div key={index} className="bg-neutral-50 rounded-lg p-3">
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium text-neutral-900">
                            {deal.store_name}
                          </p>
                          <p className="text-sm text-neutral-600">
                            {deal.name}
                          </p>
                        </div>
                        <p className="text-lg font-semibold text-neutral-900">
                          ${deal.price}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Summary */}
              <div className="bg-neutral-50 rounded-lg p-4">
                <p className="text-sm text-neutral-600">
                  Compared across {comparison.total_stores} stores in your area
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-neutral-600">
                No comparison data available for this product.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Main DealList Component
export default function DealList({ 
  deals = [], 
  loading = false, 
  error = null,
  className = '',
  showFilters = true,
  showSearch = true,
  userLocation = null
}) {
  const { shouldShowDeal } = useFilters();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortBy, setSortBy] = useState('discount');
  const [sortOrder, setSortOrder] = useState('desc');
  const [viewMode, setViewMode] = useState('grid'); // grid, list
  const [showFiltersPanel, setShowFiltersPanel] = useState(false);
  const [comparisonProduct, setComparisonProduct] = useState(null);
  const [showComparison, setShowComparison] = useState(false);

  // Filter and sort deals
  const processedDeals = useMemo(() => {
    let filtered = deals.filter(deal => {
      // Apply global filters
      if (!shouldShowDeal(deal)) return false;

      // Apply search term
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        const matchesSearch = 
          deal.name?.toLowerCase().includes(searchLower) ||
          deal.description?.toLowerCase().includes(searchLower) ||
          deal.store_name?.toLowerCase().includes(searchLower);
        if (!matchesSearch) return false;
      }

      // Apply category filter
      if (selectedCategory && deal.category !== selectedCategory) return false;

      return true;
    });

    // Sort deals
    filtered.sort((a, b) => {
      let aVal, bVal;

      switch (sortBy) {
        case 'price':
          aVal = a.price || 0;
          bVal = b.price || 0;
          break;
        case 'discount':
          aVal = a.discount_percent || 0;
          bVal = b.discount_percent || 0;
          break;
        case 'name':
          aVal = a.name || '';
          bVal = b.name || '';
          return sortOrder === 'asc' 
            ? aVal.localeCompare(bVal)
            : bVal.localeCompare(aVal);
        case 'store':
          aVal = a.store_name || '';
          bVal = b.store_name || '';
          return sortOrder === 'asc'
            ? aVal.localeCompare(bVal)
            : bVal.localeCompare(aVal);
        case 'expiry':
          aVal = new Date(a.sale_end || '9999-12-31');
          bVal = new Date(b.sale_end || '9999-12-31');
          break;
        default:
          return 0;
      }

      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
    });

    return filtered;
  }, [deals, searchTerm, selectedCategory, sortBy, sortOrder, shouldShowDeal]);

  // Get unique categories
  const categories = useMemo(() => {
    const cats = [...new Set(deals.map(deal => deal.category).filter(Boolean))];
    return cats.sort();
  }, [deals]);

  const toggleSort = (newSortBy) => {
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder(newSortBy === 'price' ? 'asc' : 'desc');
    }
  };

  const handleComparePrice = (deal) => {
    setComparisonProduct(deal);
    setShowComparison(true);
  };

  const closeComparison = () => {
    setShowComparison(false);
    setComparisonProduct(null);
  };

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-xl p-6 text-center ${className}`}>
        <div className="text-red-600 mb-2">
          <Search className="h-8 w-8 mx-auto mb-2" />
        </div>
        <h3 className="text-lg font-medium text-red-800 mb-2">Failed to load deals</h3>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-neutral-900">
            {searchTerm || selectedCategory ? 'Filtered ' : ''}Deals
            {!loading && (
              <span className="text-lg font-normal text-neutral-500 ml-2">
                ({processedDeals.length})
              </span>
            )}
          </h2>

          <div className="flex items-center space-x-2">
            {/* View Mode Toggle */}
            <div className="bg-neutral-100 p-1 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-white shadow-sm' : 'text-neutral-500'}`}
              >
                <Grid3X3 className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded ${viewMode === 'list' ? 'bg-white shadow-sm' : 'text-neutral-500'}`}
              >
                <List className="h-4 w-4" />
              </button>
            </div>

            {showFilters && (
              <button
                onClick={() => setShowFiltersPanel(!showFiltersPanel)}
                className="flex items-center space-x-2 px-3 py-2 border border-neutral-300 rounded-lg hover:bg-neutral-50"
              >
                <Filter className="h-4 w-4" />
                <span>Filter</span>
              </button>
            )}
          </div>
        </div>

        {/* Search and Quick Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          {showSearch && (
            <div className="relative flex-1">
              <Search className="h-5 w-5 text-neutral-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search deals, products, or stores..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          )}

          <div className="flex space-x-2">
            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>

            {/* Sort Options */}
            <button
              onClick={() => toggleSort('discount')}
              className={`flex items-center space-x-1 px-3 py-2 rounded-lg border ${
                sortBy === 'discount' 
                  ? 'bg-primary-50 border-primary-200 text-primary-700' 
                  : 'border-neutral-300 hover:bg-neutral-50'
              }`}
            >
              <Percent className="h-4 w-4" />
              <span>Discount</span>
              {sortBy === 'discount' && (
                sortOrder === 'desc' ? <SortDesc className="h-4 w-4" /> : <SortAsc className="h-4 w-4" />
              )}
            </button>

            <button
              onClick={() => toggleSort('price')}
              className={`flex items-center space-x-1 px-3 py-2 rounded-lg border ${
                sortBy === 'price' 
                  ? 'bg-primary-50 border-primary-200 text-primary-700' 
                  : 'border-neutral-300 hover:bg-neutral-50'
              }`}
            >
              <DollarSign className="h-4 w-4" />
              <span>Price</span>
              {sortBy === 'price' && (
                sortOrder === 'desc' ? <SortDesc className="h-4 w-4" /> : <SortAsc className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-neutral-600">Loading deals...</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && processedDeals.length === 0 && (
        <div className="text-center py-12">
          <Tag className="h-12 w-12 text-neutral-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-neutral-900 mb-2">No deals found</h3>
          <p className="text-neutral-600 mb-4">
            {searchTerm || selectedCategory 
              ? 'Try adjusting your search or filters to find more deals.'
              : 'No deals are currently available for your location.'}
          </p>
          {(searchTerm || selectedCategory) && (
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('');
              }}
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Clear filters
            </button>
          )}
        </div>
      )}

      {/* Deal Grid/List */}
      {!loading && processedDeals.length > 0 && (
        <div className={
          viewMode === 'grid' 
            ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
            : 'space-y-4'
        }>
          {processedDeals.map((deal, index) => (
            <DealCard
              key={deal.id || index}
              deal={deal}
              compact={viewMode === 'list'}
              onCompare={handleComparePrice}
              showStore={true}
            />
          ))}
        </div>
      )}

      {/* Price Comparison Modal */}
      <PriceComparisonModal
        product={comparisonProduct}
        isOpen={showComparison}
        onClose={closeComparison}
        userLocation={userLocation}
      />
    </div>
  );
}