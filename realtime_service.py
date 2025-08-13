import asyncio
import json
import time
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Any, Callable
import threading
from queue import Queue
import config
from database_service import get_database_service, get_cache_service

class RealTimeAnalyzer:
    def __init__(self):
        self.active_streams = {}
        self.subscribers = {}
        self.analysis_queue = Queue()
        self.cache_service = get_cache_service()
        self.db_service = get_database_service()
        self.is_running = False
        self.worker_thread = None
    
    def start_service(self):
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._process_queue)
            self.worker_thread.daemon = True
            self.worker_thread.start()
    
    def stop_service(self):
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join()
    
    def _process_queue(self):
        while self.is_running:
            try:
                if not self.analysis_queue.empty():
                    task = self.analysis_queue.get(timeout=1)
                    self._execute_realtime_analysis(task)
                else:
                    time.sleep(0.1)
            except:
                continue
    
    def add_data_stream(self, stream_id: str, data_source: str, analysis_config: Dict):
        self.active_streams[stream_id] = {
            'source': data_source,
            'config': analysis_config,
            'last_update': datetime.now(),
            'status': 'active',
            'buffer': []
        }
        return stream_id
    
    def update_stream_data(self, stream_id: str, new_data: Dict or List[Dict]):
        if stream_id not in self.active_streams:
            return False
        
        stream = self.active_streams[stream_id]
        
        if isinstance(new_data, dict):
            new_data = [new_data]
        
        stream['buffer'].extend(new_data)
        stream['last_update'] = datetime.now()
        
        if len(stream['buffer']) >= stream['config'].get('batch_size', 100):
            self._trigger_analysis(stream_id)
        
        return True
    
    def _trigger_analysis(self, stream_id: str):
        if stream_id not in self.active_streams:
            return
        
        stream = self.active_streams[stream_id]
        data_batch = stream['buffer'].copy()
        stream['buffer'].clear()
        
        analysis_task = {
            'stream_id': stream_id,
            'data': data_batch,
            'config': stream['config'],
            'timestamp': datetime.now()
        }
        
        self.analysis_queue.put(analysis_task)
    
    def _execute_realtime_analysis(self, task):
        try:
            stream_id = task['stream_id']
            data = task['data']
            config = task['config']
            
            df = pd.DataFrame(data)
            
            analysis_result = self._perform_quick_analysis(df, config)
            
            self._cache_result(stream_id, analysis_result)
            
            self._notify_subscribers(stream_id, analysis_result)
            
        except Exception as e:
            print(f"Error in realtime analysis: {e}")
    
    def _perform_quick_analysis(self, df: pd.DataFrame, config: Dict) -> Dict:
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'row_count': len(df),
            'summary_stats': {},
            'alerts': [],
            'trends': {}
        }
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            analysis['summary_stats'][col] = {
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'latest': float(df[col].iloc[-1]) if len(df) > 0 else 0
            }
            
            if len(df) > 1:
                trend = 'increasing' if df[col].iloc[-1] > df[col].iloc[-2] else 'decreasing'
                analysis['trends'][col] = trend
        
        for col in numeric_cols:
            threshold_high = config.get('thresholds', {}).get(col, {}).get('high')
            threshold_low = config.get('thresholds', {}).get(col, {}).get('low')
            
            latest_value = df[col].iloc[-1] if len(df) > 0 else 0
            
            if threshold_high and latest_value > threshold_high:
                analysis['alerts'].append({
                    'type': 'threshold_exceeded',
                    'column': col,
                    'value': latest_value,
                    'threshold': threshold_high,
                    'severity': 'high'
                })
            elif threshold_low and latest_value < threshold_low:
                analysis['alerts'].append({
                    'type': 'threshold_below',
                    'column': col,
                    'value': latest_value,
                    'threshold': threshold_low,
                    'severity': 'medium'
                })
        
        return analysis
    
    def _cache_result(self, stream_id: str, result: Dict):
        cache_key = f"realtime_analysis:{stream_id}"
        self.cache_service.set(cache_key, result, expiry=300)
        
        history_key = f"analysis_history:{stream_id}"
        history = self.cache_service.get(history_key) or []
        history.append(result)
        
        if len(history) > 100:
            history = history[-100:]
        
        self.cache_service.set(history_key, history, expiry=3600)
    
    def _notify_subscribers(self, stream_id: str, result: Dict):
        if stream_id in self.subscribers:
            for callback in self.subscribers[stream_id]:
                try:
                    callback(result)
                except Exception as e:
                    print(f"Error notifying subscriber: {e}")
    
    def subscribe_to_stream(self, stream_id: str, callback: Callable):
        if stream_id not in self.subscribers:
            self.subscribers[stream_id] = []
        self.subscribers[stream_id].append(callback)
    
    def get_latest_analysis(self, stream_id: str) -> Dict:
        cache_key = f"realtime_analysis:{stream_id}"
        return self.cache_service.get(cache_key)
    
    def get_analysis_history(self, stream_id: str, limit: int = 50) -> List[Dict]:
        history_key = f"analysis_history:{stream_id}"
        history = self.cache_service.get(history_key) or []
        return history[-limit:] if len(history) > limit else history
    
    def get_active_streams(self) -> Dict:
        return {
            stream_id: {
                'status': stream['status'],
                'last_update': stream['last_update'].isoformat(),
                'buffer_size': len(stream['buffer'])
            }
            for stream_id, stream in self.active_streams.items()
        }
    
    def remove_stream(self, stream_id: str) -> bool:
        if stream_id in self.active_streams:
            del self.active_streams[stream_id]
        if stream_id in self.subscribers:
            del self.subscribers[stream_id]
        return True

class MetricsCollector:
    def __init__(self):
        self.metrics = {}
        self.start_time = datetime.now()
    
    def record_metric(self, name: str, value: float, tags: Dict = None):
        timestamp = datetime.now()
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            'timestamp': timestamp,
            'value': value,
            'tags': tags or {}
        })
        
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-500:]
    
    def get_metric_summary(self, name: str, time_range: timedelta = None) -> Dict:
        if name not in self.metrics:
            return {}
        
        data = self.metrics[name]
        
        if time_range:
            cutoff_time = datetime.now() - time_range
            data = [m for m in data if m['timestamp'] > cutoff_time]
        
        if not data:
            return {}
        
        values = [m['value'] for m in data]
        
        return {
            'count': len(values),
            'mean': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'latest': values[-1],
            'timestamp_range': {
                'start': data[0]['timestamp'].isoformat(),
                'end': data[-1]['timestamp'].isoformat()
            }
        }
    
    def get_all_metrics(self) -> Dict:
        return {
            name: self.get_metric_summary(name, timedelta(hours=1))
            for name in self.metrics.keys()
        }

realtime_analyzer = RealTimeAnalyzer()
metrics_collector = MetricsCollector()

def get_realtime_analyzer():
    return realtime_analyzer

def get_metrics_collector():
    return metrics_collector