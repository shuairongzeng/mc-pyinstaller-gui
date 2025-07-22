"""
智能缓存管理器
提供统一的多层缓存管理，支持内存缓存、磁盘缓存和智能策略
"""

import os
import json
import pickle
import hashlib
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Dict, List, Tuple, Callable, Union
from dataclasses import dataclass, asdict
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheItem:
    """缓存项数据结构"""
    key: str
    data: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl: Optional[int] = None  # 生存时间（秒）
    size: int = 0  # 数据大小（字节）
    tags: List[str] = None  # 缓存标签
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    @property
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)
    
    @property
    def age_seconds(self) -> float:
        """获取缓存年龄（秒）"""
        return (datetime.now() - self.created_at).total_seconds()
    
    def touch(self):
        """更新访问时间和计数"""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class CacheStats:
    """缓存统计信息"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    memory_items: int = 0
    disk_items: int = 0
    total_size: int = 0
    hit_rate: float = 0.0
    
    def update_hit_rate(self):
        """更新命中率"""
        total = self.hits + self.misses
        self.hit_rate = self.hits / total if total > 0 else 0.0


class LRUCache:
    """LRU内存缓存实现"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheItem] = OrderedDict()
        self.lock = threading.RLock()
        self.current_size = 0
    
    def get(self, key: str) -> Optional[CacheItem]:
        """获取缓存项"""
        with self.lock:
            if key not in self.cache:
                return None
            
            item = self.cache[key]
            if item.is_expired:
                del self.cache[key]
                self.current_size -= item.size
                return None
            
            # 移动到末尾（最近使用）
            self.cache.move_to_end(key)
            item.touch()
            return item
    
    def set(self, key: str, item: CacheItem) -> bool:
        """设置缓存项"""
        with self.lock:
            # 如果已存在，先删除
            if key in self.cache:
                old_item = self.cache[key]
                self.current_size -= old_item.size
                del self.cache[key]
            
            # 检查是否需要清理空间
            self._evict_if_needed(item.size)
            
            # 添加新项
            self.cache[key] = item
            self.current_size += item.size
            return True
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                self.current_size -= item.size
                del self.cache[key]
                return True
            return False
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.current_size = 0
    
    def _evict_if_needed(self, new_item_size: int) -> int:
        """根据需要清理缓存"""
        evicted = 0
        
        # 检查数量限制
        while len(self.cache) >= self.max_size:
            self._evict_oldest()
            evicted += 1
        
        # 检查内存限制
        while (self.current_size + new_item_size) > self.max_memory_bytes and self.cache:
            self._evict_oldest()
            evicted += 1
        
        return evicted
    
    def _evict_oldest(self):
        """清理最旧的缓存项"""
        if self.cache:
            key, item = self.cache.popitem(last=False)
            self.current_size -= item.size
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self.lock:
            return {
                'items': len(self.cache),
                'size_bytes': self.current_size,
                'size_mb': self.current_size / (1024 * 1024),
                'max_size': self.max_size,
                'max_memory_mb': self.max_memory_bytes / (1024 * 1024)
            }


class DiskCache:
    """磁盘缓存实现"""
    
    def __init__(self, cache_dir: Union[str, Path], max_size_mb: int = 500):
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        
        # 创建索引文件
        self.index_file = self.cache_dir / "cache_index.json"
        self.index: Dict[str, Dict] = self._load_index()
    
    def _load_index(self) -> Dict[str, Dict]:
        """加载缓存索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache index: {e}")
        return {}
    
    def _save_index(self):
        """保存缓存索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")
    
    def _get_cache_file(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用哈希避免文件名过长
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.cache"
    
    def get(self, key: str) -> Optional[CacheItem]:
        """获取缓存项"""
        with self.lock:
            if key not in self.index:
                return None
            
            cache_file = self._get_cache_file(key)
            if not cache_file.exists():
                # 清理无效索引
                del self.index[key]
                self._save_index()
                return None
            
            try:
                with open(cache_file, 'rb') as f:
                    item = pickle.load(f)
                
                if item.is_expired:
                    self.delete(key)
                    return None
                
                item.touch()
                # 更新索引中的访问信息
                self.index[key].update({
                    'last_accessed': item.last_accessed.isoformat(),
                    'access_count': item.access_count
                })
                self._save_index()
                
                return item
                
            except Exception as e:
                logger.error(f"Failed to load cache item {key}: {e}")
                self.delete(key)
                return None
    
    def set(self, key: str, item: CacheItem) -> bool:
        """设置缓存项"""
        with self.lock:
            cache_file = self._get_cache_file(key)
            
            try:
                # 保存数据
                with open(cache_file, 'wb') as f:
                    pickle.dump(item, f)
                
                # 更新索引
                self.index[key] = {
                    'created_at': item.created_at.isoformat(),
                    'last_accessed': item.last_accessed.isoformat(),
                    'access_count': item.access_count,
                    'size': item.size,
                    'ttl': item.ttl,
                    'tags': item.tags,
                    'file_path': str(cache_file)
                }
                
                self._save_index()
                
                # 检查是否需要清理
                self._cleanup_if_needed()
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to save cache item {key}: {e}")
                return False

    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self.lock:
            if key not in self.index:
                return False

            cache_file = self._get_cache_file(key)
            try:
                if cache_file.exists():
                    cache_file.unlink()
                del self.index[key]
                self._save_index()
                return True
            except Exception as e:
                logger.error(f"Failed to delete cache item {key}: {e}")
                return False

    def clear(self):
        """清空所有缓存"""
        with self.lock:
            try:
                # 删除所有缓存文件
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()

                # 清空索引
                self.index.clear()
                self._save_index()

            except Exception as e:
                logger.error(f"Failed to clear cache: {e}")

    def _cleanup_if_needed(self):
        """根据需要清理缓存"""
        current_size = self._calculate_total_size()
        if current_size > self.max_size_bytes:
            self._cleanup_by_size()

    def _calculate_total_size(self) -> int:
        """计算总缓存大小"""
        total_size = 0
        for key, info in self.index.items():
            total_size += info.get('size', 0)
        return total_size

    def _cleanup_by_size(self):
        """按大小清理缓存"""
        # 按最后访问时间排序
        items = []
        for key, info in self.index.items():
            try:
                last_accessed = datetime.fromisoformat(info['last_accessed'])
                items.append((key, last_accessed, info.get('size', 0)))
            except:
                items.append((key, datetime.min, info.get('size', 0)))

        items.sort(key=lambda x: x[1])  # 按时间排序

        current_size = self._calculate_total_size()
        target_size = int(self.max_size_bytes * 0.8)  # 清理到80%

        for key, _, size in items:
            if current_size <= target_size:
                break
            self.delete(key)
            current_size -= size

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self.lock:
            total_size = self._calculate_total_size()
            return {
                'items': len(self.index),
                'size_bytes': total_size,
                'size_mb': total_size / (1024 * 1024),
                'max_size_mb': self.max_size_bytes / (1024 * 1024)
            }


class SmartCacheManager:
    """智能缓存管理器 - 统一的多层缓存管理"""

    def __init__(
        self,
        cache_dir: Union[str, Path] = "cache",
        memory_max_size: int = 1000,
        memory_max_mb: int = 100,
        disk_max_mb: int = 500,
        default_ttl: int = 3600,
        enable_compression: bool = False
    ):
        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        self.enable_compression = enable_compression

        # 初始化多层缓存
        self.memory_cache = LRUCache(memory_max_size, memory_max_mb)
        self.disk_cache = DiskCache(self.cache_dir, disk_max_mb)

        # 统计信息
        self.stats = CacheStats()
        self.lock = threading.RLock()

        # 启动后台清理任务
        self._start_cleanup_thread()

    def get(self, key: str, default: Any = None) -> Any:
        """获取缓存数据 - 多层查找"""
        with self.lock:
            # 1. 检查内存缓存
            item = self.memory_cache.get(key)
            if item is not None:
                self.stats.hits += 1
                self.stats.update_hit_rate()
                return item.data

            # 2. 检查磁盘缓存
            item = self.disk_cache.get(key)
            if item is not None:
                self.stats.hits += 1
                self.stats.update_hit_rate()

                # 提升到内存缓存
                self.memory_cache.set(key, item)
                return item.data

            # 3. 缓存未命中
            self.stats.misses += 1
            self.stats.update_hit_rate()
            return default

    def set(
        self,
        key: str,
        data: Any,
        ttl: Optional[int] = None,
        tags: List[str] = None,
        force_disk: bool = False
    ) -> bool:
        """设置缓存数据"""
        with self.lock:
            if ttl is None:
                ttl = self.default_ttl

            # 计算数据大小
            try:
                data_size = len(pickle.dumps(data))
            except:
                data_size = 1024  # 默认大小

            # 创建缓存项
            now = datetime.now()
            item = CacheItem(
                key=key,
                data=data,
                created_at=now,
                last_accessed=now,
                access_count=1,
                ttl=ttl,
                size=data_size,
                tags=tags or []
            )

            # 决定存储位置
            success = True
            if not force_disk and data_size < self.memory_cache.max_memory_bytes // 10:
                # 小数据存储到内存
                success = self.memory_cache.set(key, item)

            # 同时存储到磁盘（作为备份）
            if success:
                self.disk_cache.set(key, item)

            return success

    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self.lock:
            memory_deleted = self.memory_cache.delete(key)
            disk_deleted = self.disk_cache.delete(key)
            return memory_deleted or disk_deleted

    def clear(self, tags: List[str] = None) -> int:
        """清空缓存"""
        with self.lock:
            if tags is None:
                # 清空所有缓存
                self.memory_cache.clear()
                self.disk_cache.clear()
                cleared = self.stats.memory_items + self.stats.disk_items
                self.stats = CacheStats()
                return cleared
            else:
                # 按标签清空
                return self._clear_by_tags(tags)

    def _clear_by_tags(self, tags: List[str]) -> int:
        """按标签清空缓存"""
        cleared = 0
        keys_to_delete = []

        # 查找匹配标签的缓存项
        for key, info in self.disk_cache.index.items():
            item_tags = info.get('tags', [])
            if any(tag in item_tags for tag in tags):
                keys_to_delete.append(key)

        # 删除匹配的缓存项
        for key in keys_to_delete:
            if self.delete(key):
                cleared += 1

        return cleared

    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return (key in self.memory_cache.cache or
                key in self.disk_cache.index)

    def get_size(self, key: str) -> Optional[int]:
        """获取缓存项大小"""
        # 先检查内存缓存
        if key in self.memory_cache.cache:
            return self.memory_cache.cache[key].size

        # 再检查磁盘缓存
        if key in self.disk_cache.index:
            return self.disk_cache.index[key].get('size', 0)

        return None

    def get_stats(self) -> Dict[str, Any]:
        """获取详细的缓存统计信息"""
        with self.lock:
            memory_stats = self.memory_cache.get_stats()
            disk_stats = self.disk_cache.get_stats()

            self.stats.memory_items = memory_stats['items']
            self.stats.disk_items = disk_stats['items']
            self.stats.total_size = memory_stats['size_bytes'] + disk_stats['size_bytes']

            return {
                'hit_rate': f"{self.stats.hit_rate:.2%}",
                'hits': self.stats.hits,
                'misses': self.stats.misses,
                'evictions': self.stats.evictions,
                'memory': memory_stats,
                'disk': disk_stats,
                'total_size_mb': self.stats.total_size / (1024 * 1024),
                'cache_efficiency': self._calculate_efficiency()
            }

    def _calculate_efficiency(self) -> Dict[str, Any]:
        """计算缓存效率指标"""
        total_requests = self.stats.hits + self.stats.misses
        if total_requests == 0:
            return {'efficiency_score': 0.0, 'recommendation': 'No data'}

        efficiency_score = self.stats.hit_rate * 100

        if efficiency_score >= 80:
            recommendation = "缓存效率优秀"
        elif efficiency_score >= 60:
            recommendation = "缓存效率良好，可考虑增加缓存大小"
        elif efficiency_score >= 40:
            recommendation = "缓存效率一般，建议优化缓存策略"
        else:
            recommendation = "缓存效率较低，需要检查缓存配置"

        return {
            'efficiency_score': efficiency_score,
            'recommendation': recommendation,
            'total_requests': total_requests
        }

    def _start_cleanup_thread(self):
        """启动后台清理线程"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(300)  # 每5分钟清理一次
                    self._periodic_cleanup()
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()

    def _periodic_cleanup(self):
        """定期清理过期缓存"""
        with self.lock:
            # 清理内存缓存中的过期项
            expired_keys = []
            for key, item in self.memory_cache.cache.items():
                if item.is_expired:
                    expired_keys.append(key)

            for key in expired_keys:
                self.memory_cache.delete(key)
                self.stats.evictions += 1

            # 清理磁盘缓存中的过期项
            expired_keys = []
            for key, info in self.disk_cache.index.items():
                try:
                    if info.get('ttl'):
                        created_at = datetime.fromisoformat(info['created_at'])
                        if datetime.now() > created_at + timedelta(seconds=info['ttl']):
                            expired_keys.append(key)
                except:
                    pass

            for key in expired_keys:
                self.disk_cache.delete(key)
                self.stats.evictions += 1

    def optimize(self) -> Dict[str, Any]:
        """优化缓存性能"""
        with self.lock:
            optimization_result = {
                'actions_taken': [],
                'space_freed_mb': 0,
                'items_removed': 0
            }

            # 1. 清理过期项
            self._periodic_cleanup()

            # 2. 清理低频访问项
            low_access_items = []
            for key, item in self.memory_cache.cache.items():
                if item.access_count < 2 and item.age_seconds > 1800:  # 30分钟内访问少于2次
                    low_access_items.append(key)

            for key in low_access_items:
                item = self.memory_cache.cache[key]
                optimization_result['space_freed_mb'] += item.size / (1024 * 1024)
                optimization_result['items_removed'] += 1
                self.memory_cache.delete(key)

            if low_access_items:
                optimization_result['actions_taken'].append(f"清理了 {len(low_access_items)} 个低频访问项")

            # 3. 磁盘缓存压缩
            if self.disk_cache._calculate_total_size() > self.disk_cache.max_size_bytes * 0.9:
                self.disk_cache._cleanup_by_size()
                optimization_result['actions_taken'].append("执行了磁盘缓存压缩")

            return optimization_result


# 全局缓存管理器实例
_global_cache_manager: Optional[SmartCacheManager] = None


def get_cache_manager() -> SmartCacheManager:
    """获取全局缓存管理器实例"""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = SmartCacheManager()
    return _global_cache_manager


def set_cache_manager(cache_manager: SmartCacheManager):
    """设置全局缓存管理器实例"""
    global _global_cache_manager
    _global_cache_manager = cache_manager
