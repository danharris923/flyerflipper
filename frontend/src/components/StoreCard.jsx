/**
 * StoreCard Component
 * 
 * Displays individual store information with deals, distance, and actions.
 * Includes favorite/block functionality and directions integration.
 */

import { 
  MapPin, 
  Navigation, 
  Star, 
  Phone, 
  Globe, 
  Heart,
  X,
  Tag,
  Clock
} from 'lucide-react';
import { useFilters } from '../contexts/FilterContext';

export default function StoreCard({ 
  store, 
  className = '',
  showDeals = true,
  compact = false 
}) {
  const {
    isFavoriteStore,
    isBlockedStore,
    toggleFavoriteStore,
    toggleBlockedStore
  } = useFilters();

  if (!store) return null;

  const isFavorite = isFavoriteStore(store.id);
  const isBlocked = isBlockedStore(store.id);

  const handleGetDirections = () => {
    if (store.lat && store.lng) {
      // Use Google Maps directions
      const url = `https://www.google.com/maps/dir/?api=1&destination=${store.lat},${store.lng}`;
      window.open(url, '_blank');
    } else if (store.address) {
      // Fallback to address search
      const encodedAddress = encodeURIComponent(store.address);
      const url = `https://www.google.com/maps/search/?api=1&query=${encodedAddress}`;
      window.open(url, '_blank');
    }
  };

  const handleToggleFavorite = (e) => {
    e.stopPropagation();
    toggleFavoriteStore(store.id);
  };

  const handleToggleBlocked = (e) => {
    e.stopPropagation();
    toggleBlockedStore(store.id);
  };

  const formatDistance = (distance) => {
    if (distance === undefined || distance === null) return '';
    if (distance < 1) return `${Math.round(distance * 1000)}m`;
    return `${distance.toFixed(1)}km`;
  };

  if (compact) {
    return (
      <div className={`bg-white border border-neutral-200 rounded-lg p-3 hover:shadow-medium transition-shadow ${className}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 flex-1 min-w-0">
            <div className="flex-shrink-0">
              {store.rating && (
                <div className="flex items-center space-x-1">
                  <Star className="h-4 w-4 text-yellow-400 fill-current" />
                  <span className="text-sm text-neutral-600">{store.rating.toFixed(1)}</span>
                </div>
              )}
            </div>
            
            <div className="flex-1 min-w-0">
              <h3 className="font-medium text-neutral-900 truncate">{store.name}</h3>
              <div className="flex items-center space-x-2 text-sm text-neutral-500">
                {store.distance !== undefined && (
                  <span className="flex items-center space-x-1">
                    <MapPin className="h-3 w-3" />
                    <span>{formatDistance(store.distance)}</span>
                  </span>
                )}
                {store.active_deals_count > 0 && (
                  <span className="flex items-center space-x-1">
                    <Tag className="h-3 w-3" />
                    <span>{store.active_deals_count} deals</span>
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-1 flex-shrink-0">
            <button
              onClick={handleToggleFavorite}
              className={`p-1.5 rounded-lg transition-colors ${
                isFavorite 
                  ? 'text-red-500 bg-red-50 hover:bg-red-100' 
                  : 'text-neutral-400 hover:text-red-500 hover:bg-red-50'
              }`}
              title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
            >
              <Heart className={`h-4 w-4 ${isFavorite ? 'fill-current' : ''}`} />
            </button>
            
            <button
              onClick={handleGetDirections}
              className="p-1.5 rounded-lg text-neutral-400 hover:text-primary-600 hover:bg-primary-50 transition-colors"
              title="Get directions"
            >
              <Navigation className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white border border-neutral-200 rounded-xl shadow-soft hover:shadow-medium transition-all duration-200 overflow-hidden ${isBlocked ? 'opacity-60' : ''} ${className}`}>
      {/* Header */}
      <div className="p-6 pb-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-1">
              <h3 className="text-lg font-semibold text-neutral-900 truncate">
                {store.name}
              </h3>
              {isFavorite && (
                <div className="bg-red-100 text-red-600 px-2 py-0.5 rounded text-xs font-medium">
                  Favorite
                </div>
              )}
            </div>
            
            <p className="text-sm text-neutral-600 line-clamp-2">
              {store.address}
            </p>
          </div>

          <div className="flex items-center space-x-2 ml-4">
            <button
              onClick={handleToggleFavorite}
              className={`p-2 rounded-lg transition-colors ${
                isFavorite 
                  ? 'text-red-500 bg-red-50 hover:bg-red-100' 
                  : 'text-neutral-400 hover:text-red-500 hover:bg-red-50'
              }`}
              title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
            >
              <Heart className={`h-5 w-5 ${isFavorite ? 'fill-current' : ''}`} />
            </button>
            
            <button
              onClick={handleToggleBlocked}
              className={`p-2 rounded-lg transition-colors ${
                isBlocked 
                  ? 'text-neutral-600 bg-neutral-100 hover:bg-neutral-200' 
                  : 'text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100'
              }`}
              title={isBlocked ? 'Unblock store' : 'Block store'}
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Store Info */}
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4">
            {store.rating && (
              <div className="flex items-center space-x-1">
                <Star className="h-4 w-4 text-yellow-400 fill-current" />
                <span className="text-neutral-600">{store.rating.toFixed(1)}</span>
              </div>
            )}
            
            {store.distance !== undefined && (
              <div className="flex items-center space-x-1 text-neutral-500">
                <MapPin className="h-4 w-4" />
                <span>{formatDistance(store.distance)}</span>
              </div>
            )}

            {store.active_deals_count > 0 && (
              <div className="flex items-center space-x-1 text-primary-600">
                <Tag className="h-4 w-4" />
                <span className="font-medium">{store.active_deals_count} active deals</span>
              </div>
            )}
          </div>

          {store.updated_at && (
            <div className="flex items-center space-x-1 text-neutral-400">
              <Clock className="h-3 w-3" />
              <span className="text-xs">
                Updated {new Date(store.updated_at).toLocaleDateString()}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Contact Info */}
      {(store.phone || store.website) && (
        <div className="px-6 pb-4">
          <div className="flex items-center space-x-4 text-sm">
            {store.phone && (
              <a
                href={`tel:${store.phone}`}
                className="flex items-center space-x-1 text-neutral-600 hover:text-primary-600 transition-colors"
              >
                <Phone className="h-4 w-4" />
                <span>{store.phone}</span>
              </a>
            )}
            
            {store.website && (
              <a
                href={store.website}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-1 text-neutral-600 hover:text-primary-600 transition-colors"
              >
                <Globe className="h-4 w-4" />
                <span>Website</span>
              </a>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="px-6 py-4 bg-neutral-50 border-t border-neutral-100">
        <div className="flex space-x-3">
          <button
            onClick={handleGetDirections}
            className="flex-1 bg-primary-600 text-white px-4 py-2.5 rounded-lg hover:bg-primary-700 transition-colors font-medium text-sm flex items-center justify-center space-x-2"
          >
            <Navigation className="h-4 w-4" />
            <span>Get Directions</span>
          </button>
          
          {showDeals && store.active_deals_count > 0 && (
            <button
              className="px-4 py-2.5 border border-neutral-300 text-neutral-700 rounded-lg hover:bg-white transition-colors font-medium text-sm"
            >
              View Deals ({store.active_deals_count})
            </button>
          )}
        </div>
      </div>
    </div>
  );
}