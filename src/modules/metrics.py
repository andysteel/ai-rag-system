import time
from functools import wraps
from typing import Dict, Any
import logging
import json
from modules.files import get_metrics_file_path
from modules.utils import Emojis

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'embeddings_generated': 0,
            'files_processed': 0,
            'api_calls': 0,
            'errors': 0,
            'processing_time': []
        }
    
    def increment(self, metric: str, value: int = 1):
        if metric in self.metrics:
            if isinstance(self.metrics[metric], list):
                self.metrics[metric].append(value)
            else:
                self.metrics[metric] += value
    
    def get_stats(self) -> Dict[str, Any]:
        stats = self.metrics.copy()
        if stats['processing_time']:
            stats['avg_processing_time'] = sum(stats['processing_time']) / len(stats['processing_time'])
        return stats
    
    def get_stats_from_file(self, filename: str) -> Dict[str, Any]:
        """Load metrics from a JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            logger.error(f"{Emojis.ERROR.value} Metrics file {filename} not found.")
            return {}

metrics = MetricsCollector()

def track_time(metric_name: str = 'processing_time'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                metrics.increment('errors')
                raise
            finally:
                duration = time.time() - start_time
                metrics.increment(metric_name, duration)
        return wrapper
    return decorator

class MetricsDashboard:
    def __init__(self):
        pass
    
    def print_dashboard(self):
        """Print formatted metrics dashboard"""
        
        print("\n" + "="*60)
        print("📊 EMBEDDINGS DASHBOARD")
        print("="*60)
        
        # Basic Statistics
        print("\n🔢 Basic Statistics:")
        basic_stats = metrics.get_stats_from_file(get_metrics_file_path())
        if not basic_stats:
            print(f"{Emojis.WARNING.value}  No metrics data available.")
            return

        for key, value in basic_stats.items():
            if key == 'processing_time':
                continue
            print(f"   {key.replace('_', ' ').title()}: {value}")
        
        # Timing Information
        times = basic_stats.get('processing_time', [])
        if times:
            print(f"\n⏱️  Timing Information:")
            print(f"   Total Requests: {len(times)}")
            print(f"   Fastest Request: {min(times):.2f}s")
            print(f"   Slowest Request: {max(times):.2f}s")
            print(f"   Average Time: {sum(times)/len(times):.2f}s")
        
        print("="*60)
    
    def save_metrics_to_file(self, filename: str = get_metrics_file_path()):
        """Save metrics to JSON file"""
        report = metrics.get_stats()
        
        # Add timestamp
        report['timestamp'] = time.time()
        report['readable_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📁 Metrics saved to {filename}")