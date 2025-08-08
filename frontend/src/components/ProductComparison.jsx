/**
 * ProductComparison Component
 * 
 * Shows price comparisons for a product across all stores
 * Enables price matching and finding the best deals
 */

import { useState, useEffect, useMemo } from 'react';
import { 
  X, 
  TrendingDown, 
  MapPin, 
  Store,
  CheckCircle,
  AlertCircle,
  DollarSign,
  ShoppingCart,
  ExternalLink
} from 'lucide-react';

// Store categories and price match policies
const STORE_INFO = {
  // Grocery Stores
  'Loblaws': { category: 'grocery', priceMatch: true, matchPolicy: 'Matches competitors within 5km' },
  'No Frills': { category: 'grocery', priceMatch: true, matchPolicy: 'Matches all major competitors' },
  'Metro': { category: 'grocery', priceMatch: true, matchPolicy: 'Matches identical items only' },
  'Sobeys': { category: 'grocery', priceMatch: true, matchPolicy: 'Matches with flyer proof' },
  'FreshCo': { category: 'grocery', priceMatch: true, matchPolicy: 'Matches all competitors' },
  'Food Basics': { category: 'grocery', priceMatch: true, matchPolicy: 'Matches identical items' },
  'Walmart': { category: 'grocery', priceMatch: true, matchPolicy: 'Ad match on identical items' },
  'Costco': { category: 'grocery', priceMatch: false, matchPolicy: 'No price matching' },
  'Save-On-Foods': { category: 'grocery', priceMatch: true, matchPolicy: 'More rewards points instead' },
  'Real Canadian Superstore': { category: 'grocery', priceMatch: true, matchPolicy: 'Matches competitors' },
  
  // Electronics
  'Best Buy': { category: 'electronics', priceMatch: true, matchPolicy: 'Matches authorized dealers' },
  'The Source': { category: 'electronics', priceMatch: true, matchPolicy: 'Matches major retailers' },
  'Staples': { category: 'electronics', priceMatch: true, matchPolicy: '110% price match guarantee' },
  
  // Home
  'Canadian Tire': { category: 'home', priceMatch: true, matchPolicy: 'Triangle rewards adjustment' },
  'Home Depot': { category: 'home', priceMatch: true, matchPolicy: 'Matches + 10% difference' },
  'Rona': { category: 'home', priceMatch: true, matchPolicy: 'Matches local competitors' },
  'Lowes': { category: 'home', priceMatch: true, matchPolicy: 'Matches and beats by 10%' },
  
  // Pharmacy
  'Shoppers Drug Mart': { category: 'pharmacy', priceMatch: false, matchPolicy: 'Optimum points only' },
  'Rexall': { category: 'pharmacy', priceMatch: false, matchPolicy: 'No price matching' }
};

// Fuzzy matching for similar products
function calculateSimilarity(str1, str2) {
  const s1 = str1.toLowerCase();
  const s2 = str2.toLowerCase();
  
  // Check if key words match
  const words1 = s1.split(/\s+/);
  const words2 = s2.split(/\s+/);
  
  let matches = 0;
  words1.forEach(word => {
    if (word.length > 2 && words2.some(w => w.includes(word) || word.includes(w))) {
      matches++;
    }
  });
  
  return matches / Math.max(words1.length, words2.length);
}

function getStoreInfo(storeName) {
  // Try exact match first
  if (STORE_INFO[storeName]) {
    return STORE_INFO[storeName];
  }
  
  // Try partial match
  const storeKey = Object.keys(STORE_INFO).find(key => 
    storeName.toLowerCase().includes(key.toLowerCase()) ||
    key.toLowerCase().includes(storeName.toLowerCase())
  );
  
  return storeKey ? STORE_INFO[storeKey] : { 
    category: 'other', 
    priceMatch: false, 
    matchPolicy: 'Unknown policy' 
  };
}

export default function ProductComparison({ 
  product, 
  allDeals, 
  userLocation,
  onClose 
}) {
  const [loading, setLoading] = useState(true);
  const [similarProducts, setSimilarProducts] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    if (product && allDeals) {
      findSimilarProducts();
    }
  }, [product, allDeals]);

  const findSimilarProducts = () => {
    setLoading(true);
    
    // Find products with similar names or in same category
    const similar = allDeals.filter(deal => {
      if (deal.id === product.id) return true; // Include original
      
      // Calculate name similarity
      const similarity = calculateSimilarity(deal.name || '', product.name || '');
      if (similarity > 0.3) return true;
      
      // Check category match
      if (deal.category === product.category && product.category) return true;
      
      // Check for common product keywords
      const productWords = (product.name || '').toLowerCase().split(/\s+/);
      const dealWords = (deal.name || '').toLowerCase().split(/\s+/);
      
      // Look for key product identifiers (cheese, milk, bread, etc)
      const keyWords = productWords.filter(w => w.length > 3);
      return keyWords.some(word => dealWords.includes(word));
    });

    // Sort by price (lowest first)
    similar.sort((a, b) => {
      const priceA = parseFloat(a.current_price) || parseFloat(a.price) || 999999;
      const priceB = parseFloat(b.current_price) || parseFloat(b.price) || 999999;
      return priceA - priceB;
    });

    setSimilarProducts(similar);
    setLoading(false);
  };

  // Group products by store category
  const groupedProducts = useMemo(() => {
    const groups = {
      grocery: [],
      electronics: [],
      home: [],
      pharmacy: [],
      other: []
    };

    similarProducts.forEach(product => {
      const storeInfo = getStoreInfo(product.merchant_name || product.store || '');
      groups[storeInfo.category].push({
        ...product,
        storeInfo
      });
    });

    return groups;
  }, [similarProducts]);

  // Get filtered products based on selected category
  const filteredProducts = selectedCategory === 'all' 
    ? similarProducts.map(p => ({
        ...p,
        storeInfo: getStoreInfo(p.merchant_name || p.store || '')
      }))
    : groupedProducts[selectedCategory];

  const lowestPrice = similarProducts[0]?.current_price || similarProducts[0]?.price;
  const savings = product.current_price ? 
    (parseFloat(product.current_price) - parseFloat(lowestPrice)).toFixed(2) : 0;

  if (!product) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end bg-black bg-opacity-50">
      {/* Mobile Bottom Sheet Style */}
      <div className="bg-white rounded-t-3xl w-full max-h-[92vh] overflow-hidden flex flex-col animate-slide-up">
        {/* Drag Handle */}
        <div className="flex justify-center pt-3 pb-2">
          <div className="w-12 h-1 bg-neutral-300 rounded-full"></div>
        </div>
        
        {/* Header - Compact Mobile Style */}
        <div className="px-4 pb-3">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <h2 className="text-lg font-bold text-neutral-900">Compare Prices</h2>
              <p className="text-sm text-neutral-600 line-clamp-1">{product.name}</p>
            </div>
            {savings > 0 && (
              <div className="bg-green-100 text-green-700 rounded-full px-3 py-1.5 flex items-center">
                <DollarSign className="h-4 w-4 mr-1" />
                <span className="font-bold text-sm">Save ${savings}</span>
              </div>
            )}
          </div>
        </div>

        {/* Mobile Horizontal Scroll Tabs */}
        <div className="border-b border-neutral-200">
          <div className="flex overflow-x-auto scrollbar-hide px-4 py-2 gap-2">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-4 py-2 rounded-full font-semibold text-sm whitespace-nowrap transition-all ${
                selectedCategory === 'all'
                  ? 'bg-primary-600 text-white'
                  : 'bg-neutral-100 text-neutral-700'
              }`}
            >
              All ({similarProducts.length})
            </button>
            <button
              onClick={() => setSelectedCategory('grocery')}
              className={`px-4 py-2 rounded-full font-semibold text-sm whitespace-nowrap transition-all ${
                selectedCategory === 'grocery'
                  ? 'bg-primary-600 text-white'
                  : 'bg-neutral-100 text-neutral-700'
              }`}
            >
              🛒 Grocery ({groupedProducts.grocery.length})
            </button>
            <button
              onClick={() => setSelectedCategory('electronics')}
              className={`px-4 py-2 rounded-full font-semibold text-sm whitespace-nowrap transition-all ${
                selectedCategory === 'electronics'
                  ? 'bg-primary-600 text-white'
                  : 'bg-neutral-100 text-neutral-700'
              }`}
            >
              📱 Tech ({groupedProducts.electronics.length})
            </button>
            <button
              onClick={() => setSelectedCategory('home')}
              className={`px-4 py-2 rounded-full font-semibold text-sm whitespace-nowrap transition-all ${
                selectedCategory === 'home'
                  ? 'bg-primary-600 text-white'
                  : 'bg-neutral-100 text-neutral-700'
              }`}
            >
              🏠 Home ({groupedProducts.home.length})
            </button>
            <button
              onClick={() => setSelectedCategory('pharmacy')}
              className={`px-4 py-2 rounded-full font-semibold text-sm whitespace-nowrap transition-all ${
                selectedCategory === 'pharmacy'
                  ? 'bg-primary-600 text-white'
                  : 'bg-neutral-100 text-neutral-700'
              }`}
            >
              💊 Health ({groupedProducts.pharmacy.length})
            </button>
          </div>
        </div>

        {/* Product List - Mobile Optimized */}
        <div className="flex-1 overflow-y-auto px-4 py-3">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
          ) : filteredProducts.length === 0 ? (
            <div className="text-center py-12">
              <AlertCircle className="h-12 w-12 text-neutral-400 mx-auto mb-4" />
              <p className="text-neutral-600">No similar products found in this category</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredProducts.map((deal, index) => {
                const price = parseFloat(deal.current_price) || parseFloat(deal.price) || 0;
                const isLowest = index === 0 && selectedCategory === 'all';
                const isCurrent = deal.id === product.id;
                
                return (
                  <div
                    key={deal.id}
                    className={`rounded-2xl p-4 transition-all active:scale-[0.98] ${
                      isLowest 
                        ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-400' 
                        : isCurrent
                        ? 'bg-primary-50 border-2 border-primary-400'
                        : 'bg-white border border-neutral-200'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div className="flex-1 mr-3">
                            <div className="flex items-center flex-wrap gap-1.5 mb-1">
                              <h3 className="font-bold text-neutral-900 text-base">
                                {deal.merchant_name || deal.store}
                              </h3>
                              {isLowest && (
                                <span className="inline-flex items-center px-2 py-0.5 bg-green-600 text-white text-[10px] font-bold rounded-full uppercase">
                                  Best Deal
                                </span>
                              )}
                              {deal.storeInfo?.priceMatch && (
                                <span className="inline-flex items-center px-2 py-0.5 bg-blue-500 text-white text-[10px] font-bold rounded-full">
                                  <CheckCircle className="h-2.5 w-2.5 mr-0.5" />
                                  Match
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-neutral-600 line-clamp-2">{deal.name}</p>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-black text-neutral-900">
                              ${price.toFixed(2)}
                            </div>
                            {deal.original_price && (
                              <div className="text-xs text-neutral-500 line-through">
                                ${deal.original_price}
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center justify-between mt-2 pt-2 border-t border-neutral-100">
                          <div className="flex items-center gap-3 text-xs text-neutral-500">
                            <span className="flex items-center">
                              <MapPin className="h-3 w-3 mr-0.5" />
                              {deal.distance ? `${deal.distance}km` : 'Near you'}
                            </span>
                            {deal.valid_to && (
                              <span>Ends {new Date(deal.valid_to).toLocaleDateString('en-CA', { month: 'short', day: 'numeric' })}</span>
                            )}
                          </div>
                          
                          {deal.storeInfo?.priceMatch && (
                            <button
                              onClick={() => alert(`Price Match Policy:\n${deal.storeInfo.matchPolicy}`)}
                              className="text-blue-600 text-xs font-semibold"
                            >
                              Match Info
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Mobile Safe Area Bottom */}
        <div className="border-t border-neutral-200 bg-white px-4 py-3 pb-safe">
          <button
            onClick={onClose}
            className="w-full py-3 bg-neutral-900 text-white rounded-2xl font-semibold active:scale-[0.98] transition-transform"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}