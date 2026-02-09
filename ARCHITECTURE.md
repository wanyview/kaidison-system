# KAIdison 系统架构设计

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      前端层 (Frontend)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   React     │  │  Dashboard  │  │  Visualization│      │
│  │   Admin     │  │   Panel     │  │   Components  │       │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST API / WebSocket
┌───────────────────────────▼─────────────────────────────────┐
│                    API Gateway (FastAPI)                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  认证 │ 限流 │ 路由 │ 日志 │ 版本控制               │    │
│  └─────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   胶囊服务     │  │   知识图谱服务  │  │   DATM评分服务  │
│  (Capsule)    │  │  (Knowledge)   │  │    (Scoring)   │
└───────────────┘  └───────────────┘  └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据持久层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ PostgreSQL  │  │    Neo4j    │  │  MinIO/S3   │        │
│  │ (关系数据)   │  │ (知识图谱)   │  │ (文件存储)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 核心模块

### 1. 胶囊服务层 (Capsule Service)

#### 胶囊类型定义

```python
class CapsuleType(Enum):
    TECHNICAL_ROUTE = "technical_route"      # 技术路线胶囊
    PAPER = "paper"                           # 论文胶囊
    CASE = "case"                             # 案例胶囊
    EXPERIMENT_DATA = "experiment_data"      # 实验数据胶囊
```

#### 胶囊数据模型

```python
@dataclass
class Capsule:
    id: UUID
    type: CapsuleType
    title: str
    content: Dict
    datm_score: DATMScore
    metadata: CapsuleMetadata
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    version: int
    status: CapsuleStatus
```

### 2. DATM 评分引擎

```python
@dataclass
class DATMScore:
    # Truth (科学性) - 技术的科学依据
    truth: float = 0.0
    # Goodness (安全性) - 安全性评估
    goodness: float = 0.0
    # Beauty (美学) - 用户体验/界面
    beauty: float = 0.0
    # Intelligence (实用性) - 实用价值
    intelligence: float = 0.0
    
    @property
    def overall(self) -> float:
        return (self.truth + self.goodness + 
                self.beauty + self.intelligence) / 4
```

### 3. 知识图谱服务

#### 图谱节点类型

```python
class NodeType(Enum):
    TECHNOLOGY = "technology"           # 技术
    INSTITUTION = "institution"          # 机构
    RESEARCHER = "researcher"            # 学者
    PAPER = "paper"                      # 论文
    CAPSULE = "capsule"                  # 胶囊
    CASE = "case"                       # 案例
```

#### 图谱关系类型

```python
class RelationshipType(Enum):
    USES = "uses"                        # 使用关系
    DEVELOPS = "develops"                # 发展关系
    CITES = "cites"                      # 引用关系
    AFFILIATED_WITH = "affiliated_with"  # 所属关系
    COLLABORATES = "collaborates"        # 合作关系
    DERIVED_FROM = "derived_from"       # 衍生关系
```

## 数据流设计

### 胶囊创建流程

```
用户提交 → 格式验证 → DATM评分 → 图谱更新 → 版本控制 → 发布
   │           │          │          │          │         │
   ▼           ▼          ▼          ▼          ▼         ▼
Input    Schema      Scoring    Graph    Version   Publish
Validator Engine     Engine     Update   Manager   Manager
```

### 查询处理流程

```
查询请求 → 缓存检查 → 权限验证 → 图谱检索 → 结果聚合 → 评分排序 → 返回
   │          │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼          ▼
Request  Cache    Auth    Graph    Aggregator  Ranker    Response
         Check             Search             Engine
```

## 技术选型

| 层级 | 技术 | 用途 |
|------|------|------|
| API框架 | FastAPI | 高性能异步API |
| ORM | SQLAlchemy 2.0 | 数据库访问 |
| 图数据库 | Neo4j 5.x | 知识图谱存储 |
| 关系数据库 | PostgreSQL 15 | 业务数据存储 |
| 缓存 | Redis 7.x | 会话/缓存 |
| 消息队列 | RabbitMQ | 异步任务 |
| 容器化 | Docker | 部署标准化 |
| 编排 | Kubernetes | 容器编排 |

## 扩展性设计

### 微服务拆分策略

```
┌─────────────────────────────────────────────────────────┐
│                    独立部署单元                          │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Capsule MS  │  │ Graph MS    │  │ Scoring MS  │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Auth MS     │  │ Search MS   │  │ Report MS   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 插件机制

```python
# 插件接口定义
class ICapsulePlugin(Protocol):
    name: str
    version: str
    
    def process(self, capsule: Capsule) -> Capsule:
        ...
    
    def validate(self, data: Dict) -> bool:
        ...
```

## 安全性设计

```
┌─────────────────────────────────────────────────────┐
│                   安全防护层                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────┐ │
│  │ JWT认证  │  │ RBAC授权 │  │ 数据加密 │  │ 审计  │ │
│  └─────────┘  └─────────┘  └─────────┘  └───────┘ │
└─────────────────────────────────────────────────────┘
```

## 部署架构

```
                                    ┌─────────────────┐
                                    │   Load Balancer │
                                    │    (Nginx)      │
                                    └────────┬────────┘
                                             │
              ┌──────────────────────────────┼──────────────────────────────┐
              │                              │                              │
              ▼                              ▼                              ▼
    ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
    │   K8s Cluster   │          │   K8s Cluster   │          │   K8s Cluster   │
    │   (Production)  │          │   (Staging)     │          │   (Development) │
    └─────────────────┘          └─────────────────┘          └─────────────────┘
```
