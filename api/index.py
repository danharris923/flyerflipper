"""
Minimal FlyerFlutter API for Vercel
Simple serverless function that returns mock Canadian grocery deals
"""

def handler(request):
    """Vercel serverless function handler"""
    import json
    from datetime import datetime
    
    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    if request.method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    path = request.url.path
    
    # Health check
    if path.endswith('/health'):
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'healthy',
                'application': 'FlyerFlutter',
                'version': '2.0.1',
                'environment': 'vercel-simple'
            })
        }
    
    # Deals endpoint
    if path.endswith('/deals') or 'deals' in path:
        sample_deals = [
            {
                "id": 1,
                "name": "Milk 2% - 2L",
                "description": "Fresh 2% milk, 2 liter carton",
                "category": "dairy",
                "price": 3.49,
                "original_price": 4.99,
                "discount_percent": 30,
                "image_url": "https://cdn.loblaws.ca/dam/jcr:content/renditions/cq5dam.web.1280.1280.jpeg",
                "store_name": "Loblaws",
                "store_id": 1,
                "sale_start": "2025-08-07T00:00:00",
                "sale_end": "2025-08-14T23:59:59",
                "created_at": "2025-08-07T00:00:00",
                "updated_at": "2025-08-07T00:00:00",
                "external_id": "deal_1",
                "source": "flipp",
                "store_distance": None,
                "rank_score": 30,
                "is_active": True,
                "days_remaining": 7
            },
            {
                "id": 2,
                "name": "Ground Beef - Lean",
                "description": "Fresh lean ground beef, per lb",
                "category": "meat",
                "price": 5.99,
                "original_price": 7.99,
                "discount_percent": 25,
                "image_url": "https://cdn.metro.ca/dam/jcr:content/renditions/cq5dam.web.1280.1280.jpeg",
                "store_name": "Metro",
                "store_id": 2,
                "sale_start": "2025-08-07T00:00:00",
                "sale_end": "2025-08-14T23:59:59",
                "created_at": "2025-08-07T00:00:00",
                "updated_at": "2025-08-07T00:00:00",
                "external_id": "deal_2",
                "source": "flipp",
                "store_distance": None,
                "rank_score": 25,
                "is_active": True,
                "days_remaining": 7
            },
            {
                "id": 3,
                "name": "Bananas - Organic",
                "description": "Organic bananas, per lb",
                "category": "produce",
                "price": 1.49,
                "original_price": 1.99,
                "discount_percent": 25,
                "image_url": "https://cdn.nofrills.ca/dam/jcr:content/renditions/cq5dam.web.1280.1280.jpeg",
                "store_name": "No Frills",
                "store_id": 3,
                "sale_start": "2025-08-07T00:00:00",
                "sale_end": "2025-08-14T23:59:59",
                "created_at": "2025-08-07T00:00:00",
                "updated_at": "2025-08-07T00:00:00",
                "external_id": "deal_3",
                "source": "flipp",
                "store_distance": None,
                "rank_score": 25,
                "is_active": True,
                "days_remaining": 7
            }
        ]
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'items': sample_deals,
                'total': len(sample_deals),
                'page': 1,
                'per_page': 50,
                'has_next': False,
                'has_prev': False,
                'categories': ['dairy', 'meat', 'produce', 'bakery', 'frozen']
            })
        }
    
    # Stores endpoint
    if path.endswith('/stores') or 'stores' in path:
        sample_stores = [
            {
                "id": 1,
                "name": "Loblaws",
                "address": "123 Main St, Victoria, BC",
                "lat": 48.4284,
                "lng": -123.3656,
                "distance": 1.2
            },
            {
                "id": 2,
                "name": "Metro",
                "address": "456 Douglas St, Victoria, BC", 
                "lat": 48.4294,
                "lng": -123.3666,
                "distance": 1.5
            },
            {
                "id": 3,
                "name": "No Frills",
                "address": "789 Blanshard St, Victoria, BC",
                "lat": 48.4274,
                "lng": -123.3646,
                "distance": 0.8
            }
        ]
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'stores': sample_stores,
                'total': len(sample_stores),
                'page': 1,
                'per_page': 20
            })
        }
    
    # Default response
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'message': '🍎 FlyerFlutter API',
            'version': '2.0.1',
            'endpoints': ['/api/health', '/api/deals', '/api/stores']
        })
    }