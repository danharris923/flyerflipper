"""
Advanced product matching service for FlyerFlutter.
Provides intelligent product comparison with semantic similarity and relevance scoring.
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from difflib import SequenceMatcher
from collections import Counter
import unicodedata


logger = logging.getLogger(__name__)


class ProductMatcher:
    """
    Advanced product matching engine with semantic understanding.
    
    Features:
    - Brand recognition and matching
    - Product category validation
    - Size/quantity normalization
    - Semantic similarity scoring
    - Exclusion of unrelated products
    """
    
    def __init__(self):
        """Initialize the product matcher with brand and category data."""
        
        # Common grocery brands for better matching
        self.brands = {
            # Coffee brands
            'stok', 'starbucks', 'folgers', 'tim hortons', 'tims', 'maxwell house', 
            'nescafe', 'lavazza', 'illy', 'dunkin', 'green mountain', 'keurig',
            'death wish', 'bulletproof', 'eight oclock', 'community coffee',
            
            # Dairy brands  
            'lactaid', 'dairyland', 'natrel', 'saputo', 'gay lea', 'beatrice',
            'organic meadow', 'horizon', 'fairlife', 'lactantia',
            
            # Bread brands
            'wonder', 'dempsters', 'mcgavin', 'country harvest', 'pom',
            'silver hills', 'dave killer', 'ezekiel',
            
            # Snack brands
            'lays', 'doritos', 'cheetos', 'pringles', 'ruffles', 'tostitos',
            'oreo', 'chips ahoy', 'pepperidge farm', 'goldfish',
            
            # Cereal brands
            'kellogg', 'general mills', 'quaker', 'post', 'kellogs', 'cheerios',
            'frosted flakes', 'lucky charms', 'honey nut cheerios'
        }
        
        # Product categories with associated keywords
        self.categories = {
            'coffee': {
                'primary': ['coffee', 'espresso', 'cappuccino', 'latte', 'americano', 'mocha'],
                'secondary': ['cold brew', 'iced coffee', 'instant coffee', 'ground coffee', 'whole bean'],
                'exclude': ['creamer', 'maker', 'machine', 'filter', 'mug', 'cup', 'pot', 'grinder']
            },
            'milk': {
                'primary': ['milk'],
                'secondary': ['dairy', 'lactose', '1%', '2%', 'skim', 'whole', 'organic'],
                'exclude': ['chocolate', 'strawberry', 'vanilla', 'shake', 'powder', 'mix']
            },
            'bread': {
                'primary': ['bread', 'loaf'],
                'secondary': ['whole wheat', 'white', 'multigrain', 'sourdough', 'rye'],
                'exclude': ['crumb', 'maker', 'mix', 'flour']
            },
            'cheese': {
                'primary': ['cheese'],
                'secondary': ['cheddar', 'mozzarella', 'swiss', 'gouda', 'brie', 'feta'],
                'exclude': ['sauce', 'powder', 'flavored', 'crackers']
            },
            'yogurt': {
                'primary': ['yogurt', 'yoghurt'],
                'secondary': ['greek', 'vanilla', 'strawberry', 'plain', 'organic'],
                'exclude': ['drink', 'smoothie', 'maker']
            },
            'chips': {
                'primary': ['chips', 'crisps'],
                'secondary': ['potato', 'corn', 'tortilla', 'kettle', 'baked'],
                'exclude': ['dip', 'chocolate', 'cookie']
            }
        }
        
        # Size/quantity patterns for normalization
        self.size_patterns = [
            r'(\d+(?:\.\d+)?)\s*(ml|l|litre|liter|oz|fl oz|cup|cups)',
            r'(\d+(?:\.\d+)?)\s*(g|gram|grams|kg|kilogram|lb|lbs|pound|pounds)',
            r'(\d+)\s*(pack|pk|count|ct|pieces|pcs)',
            r'(\d+)\s*x\s*(\d+(?:\.\d+)?)\s*(ml|l|oz|g|kg)'
        ]
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        if not text:
            return ""
        
        # Convert to lowercase and normalize unicode
        text = unicodedata.normalize('NFKD', text.lower())
        
        # Remove special characters but keep spaces and alphanumeric
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_brand(self, product_name: str) -> Optional[str]:
        """Extract brand from product name."""
        normalized_name = self.normalize_text(product_name)
        
        for brand in self.brands:
            if brand in normalized_name:
                return brand
        
        return None
    
    def extract_size_info(self, product_name: str) -> Dict[str, Any]:
        """Extract size/quantity information from product name."""
        size_info = {
            'volume': None,
            'weight': None,
            'count': None,
            'raw_matches': []
        }
        
        for pattern in self.size_patterns:
            matches = re.findall(pattern, product_name.lower())
            for match in matches:
                size_info['raw_matches'].append(match)
                
                if len(match) >= 2:
                    value, unit = float(match[0]), match[1]
                    
                    # Categorize by unit type
                    if unit in ['ml', 'l', 'litre', 'liter', 'fl oz', 'oz', 'cup', 'cups']:
                        size_info['volume'] = (value, unit)
                    elif unit in ['g', 'gram', 'grams', 'kg', 'kilogram', 'lb', 'lbs', 'pound', 'pounds']:
                        size_info['weight'] = (value, unit)
                    elif unit in ['pack', 'pk', 'count', 'ct', 'pieces', 'pcs']:
                        size_info['count'] = (value, unit)
        
        return size_info
    
    def get_category_score(self, product_name: str, target_category: str) -> float:
        """
        Calculate category relevance score.
        
        Args:
            product_name: Product name to analyze
            target_category: Category to match against
            
        Returns:
            Score from 0.0 (no match) to 1.0 (perfect match)
        """
        if target_category not in self.categories:
            return 0.0
        
        normalized_name = self.normalize_text(product_name)
        category_def = self.categories[target_category]
        
        # Check for exclusion keywords (immediate disqualification)
        for exclude_word in category_def.get('exclude', []):
            if exclude_word in normalized_name:
                return 0.0
        
        score = 0.0
        
        # Primary keywords (high weight)
        for primary_word in category_def['primary']:
            if primary_word in normalized_name:
                score += 0.8
        
        # Secondary keywords (medium weight)  
        for secondary_word in category_def['secondary']:
            if secondary_word in normalized_name:
                score += 0.3
        
        return min(score, 1.0)
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using sequence matching."""
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def calculate_word_overlap(self, text1: str, text2: str) -> float:
        """Calculate word overlap percentage."""
        words1 = set(self.normalize_text(text1).split())
        words2 = set(self.normalize_text(text2).split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def score_product_match(self, query_product: str, candidate_product: str) -> Dict[str, Any]:
        """
        Score how well a candidate product matches the query product.
        
        Args:
            query_product: The product user is searching for
            candidate_product: Product from store data to evaluate
            
        Returns:
            Detailed scoring information
        """
        # Extract features from both products
        query_brand = self.extract_brand(query_product)
        candidate_brand = self.extract_brand(candidate_product)
        
        query_size = self.extract_size_info(query_product)
        candidate_size = self.extract_size_info(candidate_product)
        
        # Calculate various similarity scores
        text_similarity = self.calculate_text_similarity(query_product, candidate_product)
        word_overlap = self.calculate_word_overlap(query_product, candidate_product)
        
        # Brand matching bonus
        brand_score = 0.0
        if query_brand and candidate_brand:
            if query_brand == candidate_brand:
                brand_score = 1.0
            elif query_brand in candidate_brand or candidate_brand in query_brand:
                brand_score = 0.7
        
        # Category validation - determine what category the query belongs to
        category_scores = {}
        best_category = None
        best_category_score = 0.0
        
        for category in self.categories:
            category_score = self.get_category_score(query_product, category)
            category_scores[category] = category_score
            if category_score > best_category_score:
                best_category_score = category_score
                best_category = category
        
        # If we identified a category, check candidate against it
        category_match_score = 0.0
        if best_category:
            category_match_score = self.get_category_score(candidate_product, best_category)
        
        # Combined scoring with weights
        final_score = (
            text_similarity * 0.3 +           # Basic text similarity
            word_overlap * 0.3 +              # Word overlap
            brand_score * 0.2 +               # Brand matching
            category_match_score * 0.2        # Category validation
        )
        
        return {
            'total_score': final_score,
            'text_similarity': text_similarity,
            'word_overlap': word_overlap,
            'brand_score': brand_score,
            'category_match_score': category_match_score,
            'query_brand': query_brand,
            'candidate_brand': candidate_brand,
            'detected_category': best_category,
            'category_scores': category_scores,
            'is_relevant': final_score >= 0.3  # Threshold for relevance
        }
    
    def filter_and_rank_products(
        self, 
        query_product: str, 
        candidate_products: List[Dict[str, Any]], 
        min_score: float = 0.3,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Filter and rank products by relevance to the query.
        
        Args:
            query_product: Product being searched for
            candidate_products: List of product dictionaries
            min_score: Minimum relevance score to include
            max_results: Maximum number of results to return
            
        Returns:
            Ranked list of relevant products with scores
        """
        scored_products = []
        
        for product in candidate_products:
            product_name = product.get('name', '')
            if not product_name:
                continue
            
            # Score the match
            match_info = self.score_product_match(query_product, product_name)
            
            # Only include if meets minimum score threshold
            if match_info['is_relevant'] and match_info['total_score'] >= min_score:
                # Add scoring info to product
                enhanced_product = product.copy()
                enhanced_product['match_score'] = match_info['total_score']
                enhanced_product['match_details'] = match_info
                enhanced_product['relevance_reason'] = self._generate_relevance_reason(match_info)
                
                scored_products.append(enhanced_product)
        
        # Sort by score (highest first) then by price (lowest first)
        scored_products.sort(
            key=lambda x: (-x['match_score'], x.get('price', float('inf')))
        )
        
        return scored_products[:max_results]
    
    def _generate_relevance_reason(self, match_info: Dict[str, Any]) -> str:
        """Generate human-readable reason for why products match."""
        reasons = []
        
        if match_info['brand_score'] > 0:
            reasons.append("same brand")
        
        if match_info['category_match_score'] > 0.7:
            reasons.append(f"same category ({match_info['detected_category']})")
        
        if match_info['word_overlap'] > 0.6:
            reasons.append("similar product name")
        
        if not reasons:
            reasons.append("general product similarity")
        
        return ", ".join(reasons)


# Global matcher instance
product_matcher = ProductMatcher()