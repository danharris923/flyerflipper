"""
Simple Vercel Python API for FlyerFlutter
Returns mock Canadian grocery deals
"""

from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Set CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        path = self.path
        
        # Health check
        if '/health' in path:
            response = {
                'status': 'healthy',
                'application': 'FlyerFlutter',
                'version': '2.0.1',
                'environment': 'vercel'
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Deals endpoint
        if '/deals' in path:
            deals = [
                {
                    "id": 1,
                    "name": "Milk 2% - 2L",
                    "description": "Fresh 2% milk, 2 liter carton",
                    "category": "dairy",
                    "price": 3.49,
                    "original_price": 4.99,
                    "discount_percent": 30,
                    "image_url": "https://via.placeholder.com/200x200/4A90E2/FFFFFF?text=Milk",
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
                    "image_url": "https://via.placeholder.com/200x200/E74C3C/FFFFFF?text=Beef",
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
                    "image_url": "https://via.placeholder.com/200x200/F39C12/FFFFFF?text=Bananas",
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
            
            response = {
                'items': deals,
                'total': len(deals),
                'page': 1,
                'per_page': 50,
                'has_next': False,
                'has_prev': False,
                'categories': ['dairy', 'meat', 'produce', 'bakery', 'frozen']
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Stores endpoint
        if '/stores' in path:
            stores = [
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
            
            response = {
                'stores': stores,
                'total': len(stores),
                'page': 1,
                'per_page': 20
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Default response
        response = {
            'message': '🍎 FlyerFlutter API',
            'version': '2.0.1',
            'endpoints': ['/api/health', '/api/deals', '/api/stores']
        }
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
    def do_POST(self):
        # Handle POST requests the same as GET for now
        self.do_GET()