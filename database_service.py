import sqlite3
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import config

Base = declarative_base()

class AnalysisSession(Base):
    __tablename__ = 'analysis_sessions'
    
    id = Column(Integer, primary_key=True)
    dataset_name = Column(String(255))
    upload_time = Column(DateTime, default=datetime.utcnow)
    analysis_type = Column(String(100))
    status = Column(String(50))
    results_summary = Column(Text)
    file_path = Column(String(500))
    user_email = Column(String(255))

class DatasetMetadata(Base):
    __tablename__ = 'dataset_metadata'
    
    id = Column(Integer, primary_key=True)
    dataset_name = Column(String(255))
    rows = Column(Integer)
    columns = Column(Integer)
    size_mb = Column(Float)
    upload_time = Column(DateTime, default=datetime.utcnow)
    column_info = Column(Text)
    missing_values = Column(Integer)

class DatabaseService:
    def __init__(self, db_url=None):
        if db_url is None:
            db_url = getattr(config, 'DATABASE_URL', 'sqlite:///autoanalyst.db')
        
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def save_analysis_session(self, dataset_name, analysis_type, file_path, user_email=None):
        session = AnalysisSession(
            dataset_name=dataset_name,
            analysis_type=analysis_type,
            status='started',
            file_path=file_path,
            user_email=user_email
        )
        self.session.add(session)
        self.session.commit()
        return session.id
    
    def update_analysis_session(self, session_id, status, results_summary=None):
        session = self.session.query(AnalysisSession).filter_by(id=session_id).first()
        if session:
            session.status = status
            if results_summary:
                session.results_summary = json.dumps(results_summary)
            self.session.commit()
            return True
        return False
    
    def save_dataset_metadata(self, df, dataset_name):
        column_info = {
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'numeric_columns': list(df.select_dtypes(include=['number']).columns),
            'categorical_columns': list(df.select_dtypes(include=['object']).columns)
        }
        
        metadata = DatasetMetadata(
            dataset_name=dataset_name,
            rows=len(df),
            columns=len(df.columns),
            size_mb=df.memory_usage(deep=True).sum() / 1024 / 1024,
            column_info=json.dumps(column_info),
            missing_values=df.isnull().sum().sum()
        )
        
        self.session.add(metadata)
        self.session.commit()
        return metadata.id
    
    def get_analysis_history(self, limit=50):
        sessions = self.session.query(AnalysisSession).order_by(
            AnalysisSession.upload_time.desc()
        ).limit(limit).all()
        
        return [{
            'id': s.id,
            'dataset_name': s.dataset_name,
            'upload_time': s.upload_time,
            'analysis_type': s.analysis_type,
            'status': s.status,
            'user_email': s.user_email
        } for s in sessions]
    
    def get_dataset_stats(self):
        total_datasets = self.session.query(DatasetMetadata).count()
        total_analyses = self.session.query(AnalysisSession).count()
        
        avg_rows = self.session.query(DatasetMetadata).with_entities(
            DatasetMetadata.rows
        ).all()
        avg_rows = sum([r[0] for r in avg_rows]) / len(avg_rows) if avg_rows else 0
        
        return {
            'total_datasets': total_datasets,
            'total_analyses': total_analyses,
            'average_rows': int(avg_rows),
            'last_analysis': self.session.query(AnalysisSession).order_by(
                AnalysisSession.upload_time.desc()
            ).first().upload_time if total_analyses > 0 else None
        }
    
    def store_dataset(self, df, table_name):
        df.to_sql(table_name, self.engine, if_exists='replace', index=False)
        return True
    
    def load_dataset(self, table_name):
        try:
            return pd.read_sql_table(table_name, self.engine)
        except Exception as e:
            return None
    
    def list_stored_datasets(self):
        inspector = self.engine.dialect.get_table_names(self.engine.connect())
        return [table for table in inspector if not table.startswith('analysis_') and not table.startswith('dataset_')]
    
    def close(self):
        self.session.close()

class CacheService:
    def __init__(self, cache_type='memory'):
        self.cache_type = cache_type
        self.memory_cache = {}
        
        if cache_type == 'redis':
            try:
                import redis
                self.redis_client = redis.Redis(
                    host=getattr(config, 'REDIS_HOST', 'localhost'),
                    port=getattr(config, 'REDIS_PORT', 6379),
                    db=getattr(config, 'REDIS_DB', 0),
                    decode_responses=True
                )
            except ImportError:
                self.cache_type = 'memory'
    
    def set(self, key, value, expiry=3600):
        if self.cache_type == 'redis':
            try:
                self.redis_client.setex(key, expiry, json.dumps(value))
            except:
                self.memory_cache[key] = value
        else:
            self.memory_cache[key] = value
    
    def get(self, key):
        if self.cache_type == 'redis':
            try:
                value = self.redis_client.get(key)
                return json.loads(value) if value else None
            except:
                return self.memory_cache.get(key)
        else:
            return self.memory_cache.get(key)
    
    def delete(self, key):
        if self.cache_type == 'redis':
            try:
                self.redis_client.delete(key)
            except:
                pass
        if key in self.memory_cache:
            del self.memory_cache[key]

def get_database_service():
    return DatabaseService()

def get_cache_service():
    return CacheService()