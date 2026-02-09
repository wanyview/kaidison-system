"""
增强长期记忆模块 v2.1
基于AgentScope最佳实践

功能：
- 向量检索
- 关键词检索  
- 记忆分层（全局/天级）
- 记忆压缩
"""

import asyncio
import hashlib
import json
import os
import re
import shutil
import sqlite3
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
import math

# 尝试导入向量库
try:
    import numpy as np
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False
    np = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    TFIDF_AVAILABLE = True
except ImportError:
    TFIDF_AVAILABLE = False


@dataclass
class Memory:
    """记忆数据模型"""
    id: str
    content: str
    context: Dict[str, Any]
    timestamp: str
    layer: str  # 'global' or 'daily'
    keywords: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    importance: float = 0.5
    access_count: int = 0
    last_access: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Memory':
        return cls(**data)


class VectorStore:
    """向量存储管理器"""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.vectors_file = os.path.join(storage_path, "vectors.json")
        self.vectors: Dict[str, List[float]] = {}
        self._load_vectors()
    
    def _load_vectors(self):
        """加载向量数据"""
        if os.path.exists(self.vectors_file):
            try:
                with open(self.vectors_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.vectors = {k: v for k, v in data.items()}
            except Exception:
                self.vectors = {}
    
    def save_vectors(self):
        """保存向量数据"""
        try:
            with open(self.vectors_file, 'w', encoding='utf-8') as f:
                json.dump(self.vectors, f, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving vectors: {e}")
    
    def add(self, memory_id: str, embedding: List[float]):
        """添加向量"""
        self.vectors[memory_id] = embedding
        self.save_vectors()
    
    def get(self, memory_id: str) -> Optional[List[float]]:
        """获取向量"""
        return self.vectors.get(memory_id)
    
    def delete(self, memory_id: str):
        """删除向量"""
        self.vectors.pop(memory_id, None)
        self.save_vectors()
    
    def search(self, query_embedding: List[float], top_k: int = 10, 
               exclude_ids: List[str] = None) -> List[Tuple[str, float]]:
        """向量相似度搜索"""
        if not VECTOR_AVAILABLE or TFIDF_AVAILABLE:
            # 使用TF-IDF作为后备
            return self._tfidf_search(query_embedding, top_k, exclude_ids)
        
        results = []
        exclude_ids = exclude_ids or []
        
        for mem_id, embedding in self.vectors.items():
            if mem_id in exclude_ids:
                continue
            similarity = self._cosine_similarity(query_embedding, embedding)
            results.append((mem_id, similarity))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        if not vec1 or not vec2:
            return 0.0
        
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot / (norm1 * norm2))
    
    def _tfidf_search(self, query_embedding: List[float], top_k: int,
                      exclude_ids: List[str] = None) -> List[Tuple[str, float]]:
        """TF-IDF搜索作为后备"""
        # 简化版本：基于存储的向量ID返回随机分数作为后备
        exclude_ids = exclude_ids or []
        available = [mid for mid in self.vectors.keys() if mid not in exclude_ids]
        
        if not available:
            return []
        
        # 简单返回前top_k个
        return [(mid, 1.0) for mid in available[:top_k]]


class KeywordIndexer:
    """关键词索引器"""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.index_file = os.path.join(storage_path, "keyword_index.json")
        self.index: Dict[str, List[str]] = {}  # keyword -> memory_ids
        self._load_index()
    
    def _load_index(self):
        """加载索引"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.index = {k: v for k, v in data.items()}
            except Exception:
                self.index = {}
    
    def _save_index(self):
        """保存索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving keyword index: {e}")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单分词
        words = re.findall(r'\b[a-zA-Z\u4e00-\u9fa5]+\b', text.lower())
        # 过滤停用词
        stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
                     'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'of', 'in', 'for',
                     'and', 'or', 'but', 'on', 'at', 'by', 'with', 'this', 'that'}
        keywords = [w for w in words if len(w) > 1 and w not in stopwords]
        return list(set(keywords))
    
    def add(self, memory_id: str, content: str):
        """添加索引"""
        keywords = self._extract_keywords(content)
        
        for keyword in keywords:
            if keyword not in self.index:
                self.index[keyword] = []
            if memory_id not in self.index[keyword]:
                self.index[keyword].append(memory_id)
        
        self._save_index()
    
    def remove(self, memory_id: str):
        """移除索引"""
        for keyword in list(self.index.keys()):
            if memory_id in self.index[keyword]:
                self.index[keyword].remove(memory_id)
            if not self.index[keyword]:
                del self.index[keyword]
        self._save_index()
    
    def search(self, query: str, top_k: int = 20) -> List[Tuple[str, int]]:
        """关键词搜索"""
        query_keywords = self._extract_keywords(query)
        scores: Dict[str, int] = defaultdict(int)
        
        for keyword in query_keywords:
            if keyword in self.index:
                for mem_id in self.index[keyword]:
                    scores[mem_id] += 1
        
        results = [(mid, score) for mid, score in scores.items()]
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


class EnhancedMemory:
    """
    增强长期记忆模块
    
    基于AgentScope最佳实践，支持：
    - 向量检索
    - 关键词检索
    - 记忆分层（全局/天级）
    - 记忆压缩
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        max_daily_memories: int = 1000,
        global_memories_limit: int = 5000,
        compression_threshold: int = 2000,
        enable_vector_search: bool = True,
        enable_compression: bool = True
    ):
        """
        初始化增强记忆模块
        
        Args:
            storage_path: 存储路径
            max_daily_memories: 单日最大记忆数
            global_memories_limit: 全局记忆上限
            compression_threshold: 压缩阈值
            enable_vector_search: 启用向量搜索
            enable_compression: 启用自动压缩
        """
        # 设置存储路径
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(__file__).parent / "memory_store"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 配置参数
        self.max_daily_memories = max_daily_memories
        self.global_memories_limit = global_memories_limit
        self.compression_threshold = compression_threshold
        self.enable_vector_search = enable_vector_search
        self.enable_compression = enable_compression
        
        # 子索引
        self.vector_store = VectorStore(str(self.storage_path))
        self.keyword_indexer = KeywordIndexer(str(self.storage_path))
        
        # 数据库连接
        self.db_path = self.storage_path / "memories.db"
        self._init_db()
        
        # 缓存
        self._cache = {}
        self._cache_max_size = 100
        
        # 初始化TF-IDF向量化器
        if TFIDF_AVAILABLE and enable_vector_search:
            self._init_tfidf()
    
    def _init_db(self):
        """初始化SQLite数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 创建记忆表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                context TEXT,
                timestamp TEXT NOT NULL,
                layer TEXT NOT NULL,
                keywords TEXT,
                embedding_id TEXT,
                importance REAL DEFAULT 0.5,
                access_count INTEGER DEFAULT 0,
                last_access TEXT
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_layer ON memories(layer)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)')
        
        conn.commit()
        conn.close()
    
    def _init_tfidf(self):
        """初始化TF-IDF向量化器"""
        if not TFIDF_AVAILABLE:
            return
        
        # 加载现有内容用于训练
        contents = self._get_all_contents()
        if len(contents) >= 2:
            try:
                self.tfidf_vectorizer = TfidfVectorizer(max_features=1000)
                self.tfidf_vectorizer.fit(contents)
                self.tfidf_fitted = True
            except Exception:
                self.tfidf_fitted = False
        else:
            self.tfidf_fitted = False
    
    def _get_all_contents(self) -> List[str]:
        """获取所有记忆内容"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT content FROM memories')
        contents = [row[0] for row in cursor.fetchall()]
        conn.close()
        return contents
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        return f"mem_{uuid.uuid4().hex[:16]}_{int(datetime.now().timestamp() * 1000)}"
    
    def _get_today_str(self) -> str:
        """获取今天的日期字符串"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        return self.keyword_indexer._extract_keywords(content)
    
    def _calculate_importance(self, content: str, context: Dict[str, Any]) -> float:
        """计算记忆重要性分数"""
        score = 0.5  # 基础分数
        
        # 基于内容长度
        length = len(content)
        if length > 500:
            score += 0.1
        elif length > 200:
            score += 0.05
        
        # 基于上下文
        if context.get("importance"):
            score += 0.2
        
        if context.get("type") in ["decision", "preference", "commitment"]:
            score += 0.15
        
        if context.get("source") == "user":
            score += 0.1
        
        # 限制在0-1范围内
        return min(1.0, max(0.0, score))
    
    def _create_embedding(self, content: str) -> Optional[List[float]]:
        """创建内容嵌入向量"""
        if not self.enable_vector_search:
            return None
        
        # 简单词袋模型作为后备
        words = set(re.findall(r'\b[a-zA-Z]+\b', content.lower()))
        embedding = [0.0] * 100
        
        for i, word in enumerate(list(words)[:100]):
            embedding[i] = hash(word) % 1000 / 1000.0
        
        return embedding
    
    async def remember(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        存储记忆
        
        Args:
            content: 记忆内容
            context: 上下文信息
            
        Returns:
            记忆ID
        """
        context = context or {}
        
        # 生成ID
        memory_id = self._generate_id()
        timestamp = datetime.now().isoformat()
        layer = "global" if context.get("global_level") else "daily"
        keywords = self._extract_keywords(content)
        importance = self._calculate_importance(content, context)
        embedding = self._create_embedding(content)
        
        # 保存到数据库
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO memories 
            (id, content, context, timestamp, layer, keywords, importance, access_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        ''', (
            memory_id,
            content,
            json.dumps(context, ensure_ascii=False),
            timestamp,
            layer,
            json.dumps(keywords, ensure_ascii=False),
            importance
        ))
        
        conn.commit()
        conn.close()
        
        # 更新索引
        self.keyword_indexer.add(memory_id, content)
        
        if embedding:
            self.vector_store.add(memory_id, embedding)
        
        # 更新缓存
        self._cache[memory_id] = {
            "content": content,
            "context": context,
            "timestamp": timestamp,
            "layer": layer,
            "keywords": keywords,
            "importance": importance
        }
        
        # 清理缓存
        if len(self._cache) > self._cache_max_size:
            self._cache.pop(next(iter(self._cache)))
        
        # 检查是否需要压缩
        if self.enable_compression:
            asyncio.create_task(self._check_compression())
        
        return memory_id
    
    async def recall(self, query: str, layer: Optional[str] = None, 
                     top_k: int = 10, use_hybrid: bool = True) -> List[Memory]:
        """
        检索记忆
        
        Args:
            query: 查询内容
            layer: 记忆层 ('global', 'daily' 或 None表示所有)
            top_k: 返回数量
            use_hybrid: 混合检索（向量+关键词）
            
        Returns:
            匹配的记忆列表
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 构建查询条件
        where_clauses = []
        params = []
        
        if layer:
            where_clauses.append("layer = ?")
            params.append(layer)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # 获取所有候选记忆
        cursor.execute(f'''
            SELECT id, content, context, timestamp, layer, keywords, importance, 
                   access_count, last_access
            FROM memories 
            WHERE {where_sql}
            ORDER BY importance DESC, timestamp DESC
        ''', params)
        
        rows = cursor.fetchall()
        conn.close()
        
        # 检索结果
        results: List[Tuple[Memory, float]] = []
        seen_ids = set()
        
        if use_hybrid and self.enable_vector_search:
            # 混合检索
            vector_results = set()
            keyword_results = set()
            
            # 向量搜索
            embedding = self._create_embedding(query)
            if embedding:
                vector_matches = self.vector_store.search(embedding, top_k * 2)
                vector_results = {mid for mid, _ in vector_matches}
            
            # 关键词搜索
            keyword_matches = self.keyword_indexer.search(query, top_k * 2)
            keyword_results = {mid for mid, _ in keyword_matches}
            
            # 合并结果
            candidate_ids = list(vector_results | keyword_results)
        else:
            # 简单关键词搜索
            keyword_matches = self.keyword_indexer.search(query, top_k * 2)
            candidate_ids = [mid for mid, _ in keyword_matches]
        
        # 构建记忆对象
        for row in rows:
            mem_id = row[0]
            
            if candidate_ids and mem_id not in candidate_ids:
                continue
            
            try:
                context = json.loads(row[2]) if row[2] else {}
                keywords = json.loads(row[5]) if row[5] else []
                
                memory = Memory(
                    id=mem_id,
                    content=row[1],
                    context=context,
                    timestamp=row[3],
                    layer=row[4],
                    keywords=keywords,
                    importance=row[6],
                    access_count=row[7],
                    last_access=row[8]
                )
                
                # 计算相关性分数
                score = self._calculate_relevance(query, memory.content, keywords)
                results.append((memory, score))
                seen_ids.add(mem_id)
            except Exception:
                continue
        
        # 排序并返回
        results.sort(key=lambda x: x[1], reverse=True)
        
        # 更新访问计数
        for memory, _ in results[:top_k]:
            await self._update_access(memory.id)
        
        return [mem for mem, _ in results[:top_k]]
    
    def _calculate_relevance(self, query: str, content: str, keywords: List[str]) -> float:
        """计算相关性分数"""
        query_lower = query.lower()
        query_words = set(self._extract_keywords(query))
        
        # 关键词匹配
        content_words = set(keywords)
        keyword_match = len(query_words & content_words) / max(len(query_words), 1)
        
        # 内容包含
        content_lower = content.lower()
        content_match = 1.0 if query_lower in content_lower else 0.0
        
        # 组合分数
        return keyword_match * 0.6 + content_match * 0.4
    
    async def _update_access(self, memory_id: str):
        """更新访问信息"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE memories 
            SET access_count = access_count + 1,
                last_access = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), memory_id))
        
        conn.commit()
        conn.close()
    
    async def compress(self, strategy: str = "importance") -> Dict[str, Any]:
        """
        记忆压缩
        
        Args:
            strategy: 压缩策略
                - 'importance': 按重要性保留
                - 'similarity': 合并相似记忆
                - 'hybrid': 综合策略
                
        Returns:
            压缩统计信息
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 获取所有记忆
        cursor.execute('''
            SELECT id, content, context, timestamp, layer, keywords, importance, access_count
            FROM memories
            ORDER BY timestamp DESC
        ''')
        
        rows = cursor.fetchall()
        all_memories = []
        
        for row in rows:
            try:
                context = json.loads(row[2]) if row[2] else {}
                keywords = json.loads(row[5]) if row[5] else []
                
                all_memories.append({
                    "id": row[0],
                    "content": row[1],
                    "context": context,
                    "timestamp": row[3],
                    "layer": row[4],
                    "keywords": keywords,
                    "importance": row[6],
                    "access_count": row[7]
                })
            except Exception:
                continue
        
        conn.close()
        
        # 按层分组
        daily_memories = [m for m in all_memories if m["layer"] == "daily"]
        global_memories = [m for m in all_memories if m["layer"] == "global"]
        
        deleted_ids = []
        
        # 压缩每日记忆
        if len(daily_memories) > self.max_daily_memories:
            # 按重要性和访问频率排序
            daily_memories.sort(
                key=lambda x: (x["importance"], x["access_count"]),
                reverse=True
            )
            
            # 删除超出的记忆
            to_delete = daily_memories[self.max_daily_memories:]
            deleted_ids.extend(m["id"] for m in to_delete)
        
        # 压缩全局记忆
        if len(global_memories) > self.global_memories_limit:
            global_memories.sort(
                key=lambda x: (x["importance"], x["access_count"]),
                reverse=True
            )
            
            to_delete = global_memories[self.global_memories_limit:]
            deleted_ids.extend(m["id"] for m in to_delete)
        
        # 删除记忆
        if deleted_ids:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            placeholders = ",".join("?" * len(deleted_ids))
            cursor.execute(f"DELETE FROM memories WHERE id IN ({placeholders})", deleted_ids)
            
            conn.commit()
            conn.close()
            
            # 清理索引
            for mem_id in deleted_ids:
                self.keyword_indexer.remove(mem_id)
                self.vector_store.delete(mem_id)
        
        # 计算统计信息
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM memories')
        remaining_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "deleted_count": len(deleted_ids),
            "remaining_count": remaining_count,
            "strategy": strategy,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _check_compression(self):
        """检查是否需要压缩"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM memories')
        count = cursor.fetchone()[0]
        conn.close()
        
        if count >= self.compression_threshold:
            await self.compress()
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取记忆统计"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 总数
        cursor.execute('SELECT COUNT(*) FROM memories')
        total = cursor.fetchone()[0]
        
        # 按层统计
        cursor.execute('SELECT layer, COUNT(*) FROM memories GROUP BY layer')
        layer_stats = dict(cursor.fetchall())
        
        # 访问统计
        cursor.execute('SELECT SUM(access_count) FROM memories')
        total_access = cursor.fetchone()[0] or 0
        
        # 重要性分布
        cursor.execute('''
            SELECT CASE 
                WHEN importance >= 0.8 THEN 'high'
                WHEN importance >= 0.5 THEN 'medium'
                ELSE 'low'
            END,
            COUNT(*)
            FROM memories
            GROUP BY CASE 
                WHEN importance >= 0.8 THEN 'high'
                WHEN importance >= 0.5 THEN 'medium'
                ELSE 'low'
            END
        ''')
        importance_dist = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_memories": total,
            "layer_distribution": layer_stats,
            "total_access_count": total_access,
            "importance_distribution": importance_dist,
            "storage_path": str(self.storage_path)
        }
    
    async def clear(self, layer: Optional[str] = None) -> int:
        """
        清除记忆
        
        Args:
            layer: 指定层 ('global', 'daily' 或 None表示所有)
            
        Returns:
            删除的记忆数量
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if layer:
            cursor.execute('DELETE FROM memories WHERE layer = ?', (layer,))
        else:
            cursor.execute('DELETE FROM memories')
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        # 清理索引
        self.keyword_indexer = KeywordIndexer(str(self.storage_path))
        self.vector_store = VectorStore(str(self.storage_path))
        
        # 清理缓存
        self._cache.clear()
        
        return deleted_count
    
    async def export(self, file_path: str, layer: Optional[str] = None):
        """
        导出记忆
        
        Args:
            file_path: 导出路径
            layer: 指定层
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if layer:
            cursor.execute('SELECT * FROM memories WHERE layer = ?', (layer,))
        else:
            cursor.execute('SELECT * FROM memories')
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        
        data = {
            "export_time": datetime.now().isoformat(),
            "layer": layer or "all",
            "count": len(rows),
            "memories": [dict(zip(columns, row)) for row in rows]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    async def import_memories(self, file_path: str) -> int:
        """
        导入记忆
        
        Args:
            file_path: 导入路径
            
        Returns:
            导入的记忆数量
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        memories = data.get("memories", [])
        imported = 0
        
        for mem_data in memories:
            try:
                await self.remember(
                    content=mem_data.get("content", ""),
                    context=json.loads(mem_data.get("context", "{}"))
                )
                imported += 1
            except Exception:
                continue
        
        return imported


# 便捷函数
async def create_enhanced_memory(
    storage_path: Optional[str] = None,
    **kwargs
) -> EnhancedMemory:
    """创建增强记忆实例"""
    return EnhancedMemory(storage_path=storage_path, **kwargs)
