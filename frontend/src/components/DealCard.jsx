/**
 * DealCard Component - Beautiful coupon/deal display
 * 
 * Shows individual deals with store info, savings, and comparison features
 */

import { useState } from 'react';
import { 
  Star, 
  MapPin, 
  Clock, 
  Tag, 
  TrendingDown,
  ExternalLink,
  Heart,
  Share2,
  ShoppingCart,
  Calendar
} from 'lucide-react';

export default function DealCard({ 
  deal, 
  compact = false, 
  showStore = true,
  onCompare = null,
  onClick = null,
  className = '' 
}) {
  const [isFavorited, setIsFavorited] = useState(false);

  // Calculate savings information
  const savings = deal.original_price 
    ? (deal.original_price - deal.price).toFixed(2)
    : null;
  
  const savingsPercent = deal.discount_percent || 
    (deal.original_price ? Math.round(((deal.original_price - deal.price) / deal.original_price) * 100) : null);

  // Format dates
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-CA', {
      month: 'short',
      day: 'numeric'
    });
  };

  const handleFavorite = (e) => {
    e.stopPropagation();
    setIsFavorited(!isFavorited);
  };

  const handleShare = (e) => {
    e.stopPropagation();
    if (navigator.share) {
      navigator.share({
        title: deal.name,
        text: `Great deal on ${deal.name} - $${deal.price} at ${deal.store_name}`,
        url: window.location.href
      });
    }
  };

  const handleCompare = (e) => {
    e.stopPropagation();
    if (onCompare) {
      onCompare(deal);
    }
  };

  const handleCardClick = () => {
    if (onClick) {
      onClick(deal);
    } else if (onCompare) {
      onCompare(deal);
    }
  };

  if (compact) {
    return (
      <div 
        onClick={handleCardClick}
        className={`bg-white rounded-lg border border-neutral-200 p-3 hover:shadow-md transition-shadow cursor-pointer active:scale-[0.98] transition-transform ${className}`}>
        <div className="flex items-start space-x-3">
          {deal.image_url && (
            <img 
              src={deal.image_url} 
              alt={deal.name}
              className="w-12 h-12 object-cover rounded-lg flex-shrink-0"
            />
          )}
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-neutral-900 text-sm line-clamp-2">
              {deal.name}
            </h3>
            <div className="flex items-center space-x-2 mt-1">
              <span className="font-bold text-green-600 text-lg">
                ${deal.price}
              </span>
              {deal.original_price && (
                <span className="text-xs text-neutral-500 line-through">
                  ${deal.original_price}
                </span>
              )}
              {savingsPercent && (
                <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                  -{savingsPercent}%
                </span>
              )}
            </div>
            {showStore && (
              <p className="text-xs text-neutral-600 mt-1">
                {deal.store_name}
              </p>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      onClick={handleCardClick}
      className={`bg-white rounded-xl shadow-soft border border-neutral-200 overflow-hidden hover:shadow-md transition-all duration-200 group cursor-pointer active:scale-[0.99] ${className}`}>
      {/* Deal Image & Quick Actions */}
      <div className="relative">
        {deal.image_url ? (
          <img 
            src={deal.image_url} 
            alt={deal.name}
            className="w-full h-48 object-cover"
          />
        ) : (
          <div className="w-full h-48 bg-gradient-to-br from-neutral-100 to-neutral-200 flex items-center justify-center">
            <ShoppingCart className="h-12 w-12 text-neutral-400" />
          </div>
        )}
        
        {/* Savings Badge */}
        {savingsPercent && (
          <div className="absolute top-3 left-3 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold shadow-lg">
            -{savingsPercent}% OFF
          </div>
        )}

        {/* Quick Actions */}
        <div className="absolute top-3 right-3 flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={handleFavorite}
            className={`p-2 rounded-full backdrop-blur-sm ${
              isFavorited 
                ? 'bg-red-500 text-white' 
                : 'bg-white/80 text-neutral-700 hover:bg-white'
            } shadow-lg transition-colors`}
          >
            <Heart className={`h-4 w-4 ${isFavorited ? 'fill-current' : ''}`} />
          </button>
          <button
            onClick={handleShare}
            className="p-2 rounded-full bg-white/80 backdrop-blur-sm text-neutral-700 hover:bg-white shadow-lg transition-colors"
          >
            <Share2 className="h-4 w-4" />
          </button>
        </div>

        {/* Valid dates overlay */}
        <div className="absolute bottom-3 left-3 bg-black/70 text-white px-2 py-1 rounded text-xs backdrop-blur-sm">
          <div className="flex items-center space-x-1">
            <Calendar className="h-3 w-3" />
            <span>
              {formatDate(deal.sale_start)} - {formatDate(deal.sale_end)}
            </span>
          </div>
        </div>
      </div>

      {/* Deal Content */}
      <div className="p-6">
        {/* Deal Title & Category */}
        <div className="mb-3">
          <h3 className="text-lg font-semibold text-neutral-900 line-clamp-2 mb-1">
            {deal.name}
          </h3>
          {deal.category && (
            <div className="flex items-center space-x-2">
              <Tag className="h-3 w-3 text-neutral-500" />
              <span className="text-xs text-neutral-600 uppercase tracking-wide">
                {deal.category}
              </span>
            </div>
          )}
        </div>

        {/* Description */}
        {deal.description && (
          <p className="text-sm text-neutral-600 mb-4 line-clamp-2">
            {deal.description}
          </p>
        )}

        {/* Price & Savings */}
        <div className="mb-4">
          <div className="flex items-baseline space-x-2 mb-1">
            <span className="text-2xl font-bold text-green-600">
              ${deal.price}
            </span>
            {deal.original_price && (
              <span className="text-lg text-neutral-500 line-through">
                ${deal.original_price}
              </span>
            )}
          </div>
          
          {savings && (
            <div className="flex items-center space-x-1 text-green-700">
              <TrendingDown className="h-4 w-4" />
              <span className="text-sm font-medium">
                Save ${savings}
              </span>
            </div>
          )}
        </div>

        {/* Store Information */}
        {showStore && (
          <div className="mb-4 p-3 bg-neutral-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                  <span className="text-white text-xs font-bold">
                    {deal.store_name?.charAt(0) || 'S'}
                  </span>
                </div>
                <div>
                  <p className="font-medium text-neutral-900 text-sm">
                    {deal.store_name}
                  </p>
                  {deal.store_distance && (
                    <div className="flex items-center space-x-1 text-xs text-neutral-600">
                      <MapPin className="h-3 w-3" />
                      <span>{deal.store_distance}km away</span>
                    </div>
                  )}
                </div>
              </div>
              
              {deal.flyer_url && (
                <a
                  href={deal.flyer_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="text-primary-600 hover:text-primary-700 text-xs font-medium flex items-center space-x-1"
                >
                  <span>View Flyer</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between">
          {onCompare && (
            <button
              onClick={handleCompare}
              className="px-4 py-2 bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100 transition-colors font-medium text-sm"
            >
              Compare Prices
            </button>
          )}
          
          <div className="flex items-center space-x-2 text-xs text-neutral-500">
            <Clock className="h-3 w-3" />
            <span>
              {new Date(deal.updated_at) > new Date(Date.now() - 24 * 60 * 60 * 1000) 
                ? 'Updated today' 
                : `Updated ${formatDate(deal.updated_at)}`
              }
            </span>
          </div>
        </div>

        {/* Rank Score Indicator */}
        {deal.rank_score && (
          <div className="mt-3 pt-3 border-t border-neutral-200">
            <div className="flex items-center justify-between">
              <span className="text-xs text-neutral-600">Deal Score</span>
              <div className="flex items-center space-x-1">
                <div className="flex space-x-0.5">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`h-3 w-3 ${
                        i < Math.round(deal.rank_score / 20)
                          ? 'text-yellow-400 fill-current'
                          : 'text-neutral-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-xs text-neutral-600 ml-1">
                  {Math.round(deal.rank_score)}/100
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}