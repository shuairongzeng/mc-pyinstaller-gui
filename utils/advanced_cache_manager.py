"""
高级缓存管理器
提供多层缓存、智能失效和性能优化
"""

import os
import sys
import time
import json
import pickle
import hashlib
import threading
import sqlite3
from typing import Any, Optional, Dict, List, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import weakref


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    data: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl: int  # 生存时间（秒）
    size: int  # 数据大小（字节）
    tags: List[str]  # 标签用于批量失效
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl <= 0:
            return False
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)
    
    def touch(self):
        """更新访问时间"""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class CacheStats:
    """缓存统计信息"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    memory_entries: int = 0
    disk_entries: int = 0
    database_entries: int = 0
    total_memory_size: int = 0
    total_disk_size: int = 0
    evictions: int = 0
    
    @property
    def hit_rate(self) -> float:
        """缓存命中率"""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests
    
    @property
    def miss_rate(self) -> float:
        """缓存未命中率"""
        return 1.0 - self.hit_rate


class AdvancedCacheManager:
    """高级缓存管理器"""
    
    def __init__(self, 
                 cache_dir: str = "cache",
                 max_memory_size: int = 100 * 1024 * 1024,  # 100MB
                 max_memory_entries: int = 1000,
                 max_disk_size: int = 1024 * 1024 * 1024,   # 1GB
                 default_ttl: int = 3600,  # 1小时
                 cleanup_interval: int = 300):  # 5分钟
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # 配置参数
        self.max_memory_size = max_memory_size
        self.max_memory_entries = max_memory_entries
        self.max_disk_size = max_disk_size
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        
        # 多层缓存
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.memory_lock = threading.RLock()
        
        # 统计信息
        self.stats = CacheStats()
        self.stats_lock = threading.Lock()
        
        # 数据库缓存
        self.db_path = self.cache_dir / "cache.db"
        self._init_database()
        
        # 后台清理线程
        self.cleanup_thread = None
        self.cleanup_stop_event = threading.Event()
        self._start_cleanup_thread()
        
        # 弱引用回调
        self.weak_refs: Dict[str, weakref.ref] = {}
    
    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    data BLOB,
                    created_at REAL,
                    last_accessed REAL,
                    access_count INTEGER,
                    ttl INTEGER,
                    size INTEGER,
                    tags TEXT
                )
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_last_accessed 
                ON cache_entries(last_accessed)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON cache_entries(created_at)
            ''')
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取缓存数据"""
        with self.stats_lock:
            self.stats.total_requests += 1
        
        # 1. 检查内存缓存
        with self.memory_lock:
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                if not entry.is_expired():
                    entry.touch()
                    with self.stats_lock:
                        self.stats.cache_hits += 1
                    return entry.data
                else:
                    # 过期，删除
                    del self.memory_cache[key]
        
        # 2. 检查磁盘缓存
        disk_data = self._get_from_disk(key)
        if disk_data is not None:
            # 提升到内存缓存
            self._set_memory_cache(key, disk_data, self.default_ttl)
            with self.stats_lock:
                self.stats.cache_hits += 1
            return disk_data
        
        # 3. 检查数据库缓存
        db_data = self._get_from_database(key)
        if db_data is not None:
            # 提升到内存和磁盘缓存
            self._set_memory_cache(key, db_data, self.default_ttl)
            self._set_disk_cache(key, db_data, self.default_ttl)
            with self.stats_lock:
                self.stats.cache_hits += 1
            return db_data
        
        # 缓存未命中
        with self.stats_lock:
            self.stats.cache_misses += 1
        
        return default
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None, 
            tags: Optional[List[str]] = None) -> None:
        """设置缓存数据"""
        if ttl is None:
            ttl = self.default_ttl
        
        if tags is None:
            tags = []
        
        # 计算数据大小
        try:
            data_size = len(pickle.dumps(data))
        except:
            data_size = sys.getsizeof(data)
        
        # 设置内存缓存
        self._set_memory_cache(key, data, ttl, tags, data_size)
        
        # 异步设置磁盘和数据库缓存
        def async_set():
            self._set_disk_cache(key, data, ttl, tags)
            self._set_database_cache(key, data, ttl, tags, data_size)
        
        # 使用线程池异步执行
        ThreadPoolExecutor(max_workers=1).submit(async_set)
    
    def _set_memory_cache(self, key: str, data: Any, ttl: int, 
                         tags: Optional[List[str]] = None, 
                         data_size: Optional[int] = None) -> None:
        """设置内存缓存"""
        if tags is None:
            tags = []
        
        if data_size is None:
            try:
                data_size = len(pickle.dumps(data))
            except:
                data_size = sys.getsizeof(data)
        
        with self.memory_lock:
            # 检查是否需要清理空间
            self._ensure_memory_space(data_size)
            
            # 创建缓存条目
            entry = CacheEntry(
                key=key,
                data=data,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                ttl=ttl,
                size=data_size,
                tags=tags
            )
            
            self.memory_cache[key] = entry
            
            # 更新统计
            with self.stats_lock:
                self.stats.memory_entries = len(self.memory_cache)
                self.stats.total_memory_size += data_size
    
    def _ensure_memory_space(self, required_size: int) -> None:
        """确保内存空间足够"""
        # 检查条目数量限制
        while len(self.memory_cache) >= self.max_memory_entries:
            self._evict_lru_memory()
        
        # 检查内存大小限制
        current_size = sum(entry.size for entry in self.memory_cache.values())
        while current_size + required_size > self.max_memory_size:
            if not self._evict_lru_memory():
                break  # 无法继续清理
            current_size = sum(entry.size for entry in self.memory_cache.values())
    
    def _evict_lru_memory(self) -> bool:
        """清理最近最少使用的内存缓存条目"""
        if not self.memory_cache:
            return False
        
        # 找到最近最少使用的条目
        lru_key = min(self.memory_cache.keys(), 
                     key=lambda k: self.memory_cache[k].last_accessed)
        
        entry = self.memory_cache.pop(lru_key)
        
        # 更新统计
        with self.stats_lock:
            self.stats.evictions += 1
            self.stats.total_memory_size -= entry.size
            self.stats.memory_entries = len(self.memory_cache)
        
        return True
    
    def _get_from_disk(self, key: str) -> Any:
        """从磁盘获取缓存"""
        cache_file = self.cache_dir / f"{self._hash_key(key)}.cache"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 检查是否过期
            if cache_data.get('ttl', 0) > 0:
                created_at = datetime.fromisoformat(cache_data['created_at'])
                if datetime.now() > created_at + timedelta(seconds=cache_data['ttl']):
                    cache_file.unlink()  # 删除过期文件
                    return None
            
            return cache_data['data']
        
        except Exception:
            # 文件损坏，删除
            try:
                cache_file.unlink()
            except:
                pass
            return None
    
    def _set_disk_cache(self, key: str, data: Any, ttl: int, 
                       tags: Optional[List[str]] = None) -> None:
        """设置磁盘缓存"""
        cache_file = self.cache_dir / f"{self._hash_key(key)}.cache"
        
        cache_data = {
            'key': key,
            'data': data,
            'created_at': datetime.now().isoformat(),
            'ttl': ttl,
            'tags': tags or []
        }
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            # 磁盘写入失败，忽略
            pass
    
    def _get_from_database(self, key: str) -> Any:
        """从数据库获取缓存"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute(
                    'SELECT data, created_at, ttl FROM cache_entries WHERE key = ?',
                    (key,)
                )
                row = cursor.fetchone()
                
                if row is None:
                    return None
                
                data_blob, created_at, ttl = row
                
                # 检查是否过期
                if ttl > 0:
                    created_time = datetime.fromtimestamp(created_at)
                    if datetime.now() > created_time + timedelta(seconds=ttl):
                        # 删除过期条目
                        conn.execute('DELETE FROM cache_entries WHERE key = ?', (key,))
                        return None
                
                # 更新访问时间
                conn.execute(
                    'UPDATE cache_entries SET last_accessed = ?, access_count = access_count + 1 WHERE key = ?',
                    (time.time(), key)
                )
                
                return pickle.loads(data_blob)
        
        except Exception:
            return None
    
    def _set_database_cache(self, key: str, data: Any, ttl: int, 
                           tags: Optional[List[str]] = None, 
                           data_size: Optional[int] = None) -> None:
        """设置数据库缓存"""
        try:
            data_blob = pickle.dumps(data)
            now = time.time()
            
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO cache_entries 
                    (key, data, created_at, last_accessed, access_count, ttl, size, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    key, data_blob, now, now, 1, ttl, 
                    data_size or len(data_blob), 
                    json.dumps(tags or [])
                ))
        
        except Exception:
            pass
    
    def _hash_key(self, key: str) -> str:
        """生成键的哈希值"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def delete(self, key: str) -> bool:
        """删除缓存条目"""
        deleted = False
        
        # 删除内存缓存
        with self.memory_lock:
            if key in self.memory_cache:
                entry = self.memory_cache.pop(key)
                with self.stats_lock:
                    self.stats.total_memory_size -= entry.size
                    self.stats.memory_entries = len(self.memory_cache)
                deleted = True
        
        # 删除磁盘缓存
        cache_file = self.cache_dir / f"{self._hash_key(key)}.cache"
        if cache_file.exists():
            try:
                cache_file.unlink()
                deleted = True
            except:
                pass
        
        # 删除数据库缓存
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute('DELETE FROM cache_entries WHERE key = ?', (key,))
                if cursor.rowcount > 0:
                    deleted = True
        except:
            pass
        
        return deleted
    
    def clear(self, tags: Optional[List[str]] = None) -> int:
        """清空缓存"""
        cleared_count = 0
        
        if tags is None:
            # 清空所有缓存
            with self.memory_lock:
                cleared_count += len(self.memory_cache)
                self.memory_cache.clear()
                with self.stats_lock:
                    self.stats.memory_entries = 0
                    self.stats.total_memory_size = 0
            
            # 清空磁盘缓存
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    cache_file.unlink()
                    cleared_count += 1
                except:
                    pass
            
            # 清空数据库缓存
            try:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.execute('DELETE FROM cache_entries')
                    cleared_count += cursor.rowcount
            except:
                pass
        
        else:
            # 按标签清空
            # TODO: 实现按标签清空的逻辑
            pass
        
        return cleared_count
    
    def get_stats(self) -> CacheStats:
        """获取缓存统计信息"""
        with self.stats_lock:
            stats = CacheStats(
                total_requests=self.stats.total_requests,
                cache_hits=self.stats.cache_hits,
                cache_misses=self.stats.cache_misses,
                memory_entries=len(self.memory_cache),
                total_memory_size=sum(entry.size for entry in self.memory_cache.values()),
                evictions=self.stats.evictions
            )
        
        # 获取磁盘统计
        try:
            disk_files = list(self.cache_dir.glob("*.cache"))
            stats.disk_entries = len(disk_files)
            stats.total_disk_size = sum(f.stat().st_size for f in disk_files)
        except:
            pass
        
        # 获取数据库统计
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM cache_entries')
                stats.database_entries = cursor.fetchone()[0]
        except:
            pass
        
        return stats
    
    def _start_cleanup_thread(self):
        """启动后台清理线程"""
        def cleanup_worker():
            while not self.cleanup_stop_event.wait(self.cleanup_interval):
                self._cleanup_expired()
        
        self.cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self.cleanup_thread.start()
    
    def _cleanup_expired(self):
        """清理过期条目"""
        # 清理内存缓存
        with self.memory_lock:
            expired_keys = [
                key for key, entry in self.memory_cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                entry = self.memory_cache.pop(key)
                with self.stats_lock:
                    self.stats.total_memory_size -= entry.size
        
        # 清理数据库缓存
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                now = time.time()
                conn.execute('''
                    DELETE FROM cache_entries 
                    WHERE ttl > 0 AND created_at + ttl < ?
                ''', (now,))
        except:
            pass
    
    def __del__(self):
        """析构函数"""
        if hasattr(self, 'cleanup_stop_event'):
            self.cleanup_stop_event.set()
        if hasattr(self, 'cleanup_thread') and self.cleanup_thread:
            self.cleanup_thread.join(timeout=1)
