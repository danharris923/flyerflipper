# Best Practices and Legal Considerations

## Web Scraping Ethics and Legal Compliance

### Legal Framework in Canada

#### Key Legislation
1. **Personal Information Protection and Electronic Documents Act (PIPEDA)**
   - Governs collection, use, and disclosure of personal information
   - Applies to private sector organizations
   - Requires consent for personal data collection

2. **Copyright Act**
   - Protects original creative works including website content
   - Fair dealing exceptions may apply for research/analysis

3. **Computer Fraud and Abuse Considerations**
   - Unauthorized access to computer systems can be prosecuted
   - Respect robots.txt and terms of service

4. **Provincial Privacy Laws**
   - Additional privacy requirements may apply by province

### Terms of Service Compliance

#### Common Restrictions
```python
class TermsOfServiceChecker:
    """Helper to check common ToS restrictions"""
    
    @staticmethod
    def check_common_restrictions():
        """Common terms to watch for"""
        restrictions = {
            'automated_access': 'Prohibition of bots, scrapers, or automated tools',
            'commercial_use': 'Restrictions on commercial use of data',
            'data_extraction': 'Explicit prohibition of data extraction',
            'rate_limits': 'Requirements for reasonable request rates',
            'attribution': 'Requirements to credit data sources',
            'modification': 'Prohibition of modifying or redistributing data'
        }
        return restrictions
    
    @staticmethod
    def robots_txt_checker(domain: str):
        """Check robots.txt compliance"""
        import requests
        from urllib.robotparser import RobotFileParser
        
        try:
            rp = RobotFileParser()
            rp.set_url(f'https://{domain}/robots.txt')
            rp.read()
            
            # Check if scraping is allowed for common user agents
            user_agents = ['*', 'python-requests', 'scrapy']
            
            results = {}
            for ua in user_agents:
                results[ua] = {
                    'can_fetch_root': rp.can_fetch(ua, '/'),
                    'can_fetch_api': rp.can_fetch(ua, '/api/'),
                    'crawl_delay': rp.crawl_delay(ua)
                }
            
            return results
            
        except Exception as e:
            return {'error': f'Could not check robots.txt: {e}'}

# Example usage
checker = TermsOfServiceChecker()
loblaws_robots = checker.robots_txt_checker('loblaws.ca')
```

### Ethical Scraping Practices

#### Rate Limiting Implementation
```python
import time
import random
from typing import Optional
import logging

class EthicalScraper:
    """Base class implementing ethical scraping practices"""
    
    def __init__(self, 
                 min_delay: float = 2.0,
                 max_delay: float = 5.0,
                 max_concurrent: int = 1,
                 respect_robots: bool = True):
        
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_concurrent = max_concurrent
        self.respect_robots = respect_robots
        self.last_request_time = 0
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def polite_delay(self):
        """Implement random delay between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        min_delay = self.min_delay
        
        if time_since_last < min_delay:
            additional_delay = min_delay - time_since_last
            total_delay = additional_delay + random.uniform(0, self.max_delay - self.min_delay)
            
            self.logger.info(f"Polite delay: {total_delay:.2f} seconds")
            time.sleep(total_delay)
        
        self.last_request_time = time.time()
    
    def check_server_load(self, url: str) -> bool:
        """Check if server appears to be under heavy load"""
        import requests
        
        try:
            start_time = time.time()
            response = requests.head(url, timeout=10)
            response_time = time.time() - start_time
            
            # If response time is very slow, back off
            if response_time > 10:
                self.logger.warning(f"Slow response time ({response_time:.2f}s), backing off")
                return False
            
            # Check for rate limiting headers
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    self.logger.info(f"Rate limited, waiting {retry_after} seconds")
                    time.sleep(int(retry_after))
                return False
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error checking server load: {e}")
            return False
    
    def adaptive_rate_limiting(self, response_times: list, error_count: int):
        """Adapt scraping speed based on server response"""
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Increase delays if server is slow or errors are frequent
        if avg_response_time > 5 or error_count > 3:
            self.min_delay *= 1.5
            self.max_delay *= 1.5
            self.logger.info(f"Increased delays: min={self.min_delay:.2f}, max={self.max_delay:.2f}")
        
        # Decrease delays if server is responsive and no errors
        elif avg_response_time < 2 and error_count == 0:
            self.min_delay = max(1.0, self.min_delay * 0.9)
            self.max_delay = max(2.0, self.max_delay * 0.9)
            self.logger.info(f"Decreased delays: min={self.min_delay:.2f}, max={self.max_delay:.2f}")
```

#### Resource Usage Monitoring
```python
import psutil
import threading
from typing import Dict
import time

class ResourceMonitor:
    """Monitor system resources during scraping"""
    
    def __init__(self, max_cpu_percent: float = 80.0, max_memory_percent: float = 80.0):
        self.max_cpu_percent = max_cpu_percent
        self.max_memory_percent = max_memory_percent
        self.monitoring = False
        self.stats = {
            'cpu_usage': [],
            'memory_usage': [],
            'network_io': [],
            'disk_io': []
        }
    
    def start_monitoring(self):
        """Start resource monitoring in background thread"""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_resources)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
    
    def _monitor_resources(self):
        """Monitor system resources"""
        while self.monitoring:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.stats['cpu_usage'].append(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.stats['memory_usage'].append(memory.percent)
            
            # Network I/O
            net_io = psutil.net_io_counters()
            self.stats['network_io'].append(net_io.bytes_sent + net_io.bytes_recv)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.stats['disk_io'].append(disk_io.read_bytes + disk_io.write_bytes)
            
            time.sleep(5)  # Monitor every 5 seconds
    
    def should_throttle(self) -> bool:
        """Check if scraping should be throttled due to resource usage"""
        if not self.stats['cpu_usage'] or not self.stats['memory_usage']:
            return False
        
        recent_cpu = self.stats['cpu_usage'][-10:]  # Last 10 measurements
        recent_memory = self.stats['memory_usage'][-10:]
        
        avg_cpu = sum(recent_cpu) / len(recent_cpu)
        avg_memory = sum(recent_memory) / len(recent_memory)
        
        return avg_cpu > self.max_cpu_percent or avg_memory > self.max_memory_percent
    
    def get_resource_report(self) -> Dict:
        """Get resource usage report"""
        if not self.stats['cpu_usage']:
            return {'error': 'No monitoring data available'}
        
        return {
            'avg_cpu': sum(self.stats['cpu_usage']) / len(self.stats['cpu_usage']),
            'max_cpu': max(self.stats['cpu_usage']),
            'avg_memory': sum(self.stats['memory_usage']) / len(self.stats['memory_usage']),
            'max_memory': max(self.stats['memory_usage']),
            'total_network_io': self.stats['network_io'][-1] - self.stats['network_io'][0] if len(self.stats['network_io']) > 1 else 0
        }
```

### Data Privacy and Security

#### Data Handling Best Practices
```python
import hashlib
import json
from typing import Dict, Any
from datetime import datetime, timedelta
import sqlite3

class SecureDataHandler:
    """Handle scraped data securely and in compliance with privacy laws"""
    
    def __init__(self, db_path: str = "grocery_data.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Setup SQLite database with privacy considerations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables with data retention policies
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hash TEXT UNIQUE,
                merchant TEXT NOT NULL,
                product_name TEXT NOT NULL,
                price REAL,
                scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                data_source TEXT,
                anonymized BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create index for efficient cleanup
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON scraped_data(expires_at)')
        
        conn.commit()
        conn.close()
    
    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or hash potentially sensitive information"""
        anonymized = data.copy()
        
        # Remove potentially sensitive fields
        sensitive_fields = ['user_id', 'session_id', 'ip_address', 'location_details']
        for field in sensitive_fields:
            anonymized.pop(field, None)
        
        # Hash identifiable information
        if 'postal_code' in anonymized:
            anonymized['postal_code_hash'] = self.hash_data(anonymized['postal_code'])
            del anonymized['postal_code']
        
        return anonymized
    
    def hash_data(self, data: str) -> str:
        """Create hash of sensitive data"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def store_data(self, data: Dict[str, Any], retention_days: int = 30):
        """Store data with automatic expiration"""
        anonymized_data = self.anonymize_data(data)
        data_hash = self.hash_data(json.dumps(anonymized_data, sort_keys=True))
        
        expires_at = datetime.now() + timedelta(days=retention_days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO scraped_data 
                (data_hash, merchant, product_name, price, expires_at, data_source)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data_hash,
                anonymized_data.get('merchant', ''),
                anonymized_data.get('name', ''),
                anonymized_data.get('price'),
                expires_at,
                anonymized_data.get('source', 'web_scraping')
            ))
            
            conn.commit()
            
        except sqlite3.IntegrityError:
            # Data already exists, update timestamp
            cursor.execute('''
                UPDATE scraped_data 
                SET scraped_at = CURRENT_TIMESTAMP, expires_at = ?
                WHERE data_hash = ?
            ''', (expires_at, data_hash))
            conn.commit()
        
        finally:
            conn.close()
    
    def cleanup_expired_data(self):
        """Remove expired data automatically"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM scraped_data WHERE expires_at < ?', (datetime.now(),))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def get_data_retention_report(self) -> Dict:
        """Generate data retention compliance report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN expires_at > datetime('now') THEN 1 END) as active_records,
                COUNT(CASE WHEN expires_at <= datetime('now') THEN 1 END) as expired_records,
                MIN(scraped_at) as oldest_record,
                MAX(scraped_at) as newest_record
            FROM scraped_data
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_records': result[0],
            'active_records': result[1], 
            'expired_records': result[2],
            'oldest_record': result[3],
            'newest_record': result[4],
            'report_generated': datetime.now().isoformat()
        }
```

### Error Handling and Resilience

#### Robust Error Handling
```python
import logging
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Callable, Any
import functools

class RobustScraper:
    """Scraper with comprehensive error handling and retry logic"""
    
    def __init__(self):
        self.setup_logging()
        self.setup_session()
        self.error_counts = {}
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_reset_time = 300  # 5 minutes
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_session(self):
        """Setup requests session with retry strategy"""
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1,
            raise_on_status=False
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set timeout for all requests
        self.session.request = functools.partial(self.session.request, timeout=30)
    
    def circuit_breaker(self, func: Callable) -> Callable:
        """Circuit breaker decorator to prevent cascade failures"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            
            # Check if circuit is open
            if self.is_circuit_open(func_name):
                self.logger.warning(f"Circuit breaker open for {func_name}")
                return None
            
            try:
                result = func(*args, **kwargs)
                self.reset_error_count(func_name)
                return result
                
            except Exception as e:
                self.increment_error_count(func_name)
                self.logger.error(f"Error in {func_name}: {e}")
                
                if self.should_open_circuit(func_name):
                    self.open_circuit(func_name)
                
                return None
        
        return wrapper
    
    def is_circuit_open(self, func_name: str) -> bool:
        """Check if circuit breaker is open"""
        if func_name not in self.error_counts:
            return False
        
        error_info = self.error_counts[func_name]
        
        if error_info['count'] >= self.circuit_breaker_threshold:
            time_since_last_error = time.time() - error_info['last_error_time']
            
            if time_since_last_error > self.circuit_breaker_reset_time:
                # Reset circuit after timeout
                self.reset_error_count(func_name)
                return False
            
            return True
        
        return False
    
    def increment_error_count(self, func_name: str):
        """Increment error count for function"""
        if func_name not in self.error_counts:
            self.error_counts[func_name] = {'count': 0, 'last_error_time': 0}
        
        self.error_counts[func_name]['count'] += 1
        self.error_counts[func_name]['last_error_time'] = time.time()
    
    def reset_error_count(self, func_name: str):
        """Reset error count for function"""
        if func_name in self.error_counts:
            del self.error_counts[func_name]
    
    def should_open_circuit(self, func_name: str) -> bool:
        """Check if circuit should be opened"""
        return (func_name in self.error_counts and 
                self.error_counts[func_name]['count'] >= self.circuit_breaker_threshold)
    
    def open_circuit(self, func_name: str):
        """Open circuit breaker"""
        self.logger.warning(f"Opening circuit breaker for {func_name}")
    
    @circuit_breaker
    def safe_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make safe HTTP request with comprehensive error handling"""
        try:
            response = self.session.get(url, **kwargs)
            
            # Log response details
            self.logger.info(f"Request to {url} returned {response.status_code}")
            
            # Handle different status codes
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                # Rate limited
                retry_after = response.headers.get('Retry-After', 60)
                self.logger.warning(f"Rate limited, waiting {retry_after} seconds")
                time.sleep(int(retry_after))
                return None
            elif response.status_code in [500, 502, 503, 504]:
                # Server errors
                self.logger.error(f"Server error {response.status_code} for {url}")
                return None
            else:
                self.logger.warning(f"Unexpected status code {response.status_code} for {url}")
                return None
                
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout for request to {url}")
            return None
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Connection error for {url}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request exception for {url}: {e}")
            return None
    
    def graceful_shutdown(self):
        """Gracefully shutdown scraper"""
        self.logger.info("Shutting down scraper gracefully")
        
        # Save error statistics
        with open('error_statistics.json', 'w') as f:
            import json
            json.dump(self.error_counts, f, indent=2)
        
        # Close session
        if hasattr(self, 'session'):
            self.session.close()
        
        self.logger.info("Scraper shutdown complete")
```

### Monitoring and Alerting

#### Scraper Health Monitoring
```python
import time
import json
from typing import Dict, List
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ScraperMonitor:
    """Monitor scraper health and send alerts"""
    
    def __init__(self, alert_email: str = None, smtp_config: Dict = None):
        self.alert_email = alert_email
        self.smtp_config = smtp_config or {}
        self.metrics = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'data_points_collected': 0,
            'start_time': time.time(),
            'last_successful_scrape': None,
            'errors': []
        }
    
    def record_request(self, success: bool, url: str = None, error: str = None):
        """Record request metrics"""
        self.metrics['requests_made'] += 1
        
        if success:
            self.metrics['successful_requests'] += 1
            self.metrics['last_successful_scrape'] = datetime.now()
        else:
            self.metrics['failed_requests'] += 1
            if error:
                self.metrics['errors'].append({
                    'timestamp': datetime.now().isoformat(),
                    'url': url,
                    'error': error
                })
    
    def record_data_collection(self, count: int):
        """Record data points collected"""
        self.metrics['data_points_collected'] += count
    
    def get_health_status(self) -> Dict:
        """Get current health status"""
        current_time = time.time()
        uptime = current_time - self.metrics['start_time']
        
        success_rate = (
            self.metrics['successful_requests'] / self.metrics['requests_made'] 
            if self.metrics['requests_made'] > 0 else 0
        ) * 100
        
        requests_per_minute = self.metrics['requests_made'] / (uptime / 60)
        
        health_status = {
            'uptime_seconds': uptime,
            'success_rate_percent': success_rate,
            'requests_per_minute': requests_per_minute,
            'total_requests': self.metrics['requests_made'],
            'successful_requests': self.metrics['successful_requests'], 
            'failed_requests': self.metrics['failed_requests'],
            'data_points_collected': self.metrics['data_points_collected'],
            'last_successful_scrape': self.metrics['last_successful_scrape'],
            'recent_errors': self.metrics['errors'][-10:],  # Last 10 errors
            'status': self.determine_health_status(success_rate, uptime)
        }
        
        return health_status
    
    def determine_health_status(self, success_rate: float, uptime: float) -> str:
        """Determine overall health status"""
        if success_rate > 95 and uptime > 300:  # 5 minutes uptime
            return 'healthy'
        elif success_rate > 80:
            return 'degraded'
        else:
            return 'unhealthy'
    
    def should_alert(self) -> bool:
        """Check if alert should be sent"""
        health = self.get_health_status()
        
        # Alert conditions
        conditions = [
            health['success_rate_percent'] < 70,  # Low success rate
            health['failed_requests'] > 50,       # Too many failures
            health['status'] == 'unhealthy',      # Unhealthy status
            # No successful scrape in last 30 minutes
            (health['last_successful_scrape'] and 
             datetime.now() - health['last_successful_scrape'] > timedelta(minutes=30))
        ]
        
        return any(conditions)
    
    def send_alert(self, message: str):
        """Send alert via email"""
        if not self.alert_email or not self.smtp_config:
            print(f"ALERT: {message}")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config.get('from_email')
            msg['To'] = self.alert_email
            msg['Subject'] = 'Grocery Scraper Alert'
            
            body = f"""
            Grocery Scraper Alert
            
            Message: {message}
            
            Health Status:
            {json.dumps(self.get_health_status(), indent=2, default=str)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port'])
            server.starttls()
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.smtp_config['from_email'], self.alert_email, text)
            server.quit()
            
            print(f"Alert sent: {message}")
            
        except Exception as e:
            print(f"Failed to send alert: {e}")
    
    def check_and_alert(self):
        """Check health and send alert if needed"""
        if self.should_alert():
            health = self.get_health_status()
            message = f"Scraper health is {health['status']} - Success rate: {health['success_rate_percent']:.1f}%"
            self.send_alert(message)
    
    def save_metrics(self, filename: str):
        """Save metrics to file"""
        with open(filename, 'w') as f:
            json.dump(self.get_health_status(), f, indent=2, default=str)
```

## Summary

This comprehensive guide covers:

1. **Legal Compliance** - PIPEDA, copyright, and terms of service considerations
2. **Ethical Practices** - Rate limiting, resource monitoring, and respectful scraping
3. **Data Security** - Anonymization, retention policies, and secure storage
4. **Error Handling** - Circuit breakers, retry logic, and graceful failure handling
5. **Monitoring** - Health checks, alerting, and performance metrics

Following these best practices ensures your grocery scraping implementation is legal, ethical, reliable, and maintainable while respecting the rights and resources of data providers.