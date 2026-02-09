# KAIdison API 接口文档

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证**: Bearer Token (JWT)
- **Content-Type**: application/json

---

## 胶囊管理 API

### 1. 创建胶囊

**POST** `/capsules`

**请求体**:

```json
{
  "type": "technical_route",
  "title": "侵入式BCI技术路线 - Neuralink方案",
  "content": {
    "technology": "侵入式脑机接口",
    "approach": "Utah阵列电极",
    "parameters": {
      "channels": 1024,
      "sampling_rate": "20kHz",
      "resolution": "16-bit"
    },
    "description": "详细的技术路线描述..."
  },
  "datm_score": {
    "truth": 95,
    "goodness": 75,
    "beauty": 80,
    "intelligence": 90
  },
  "metadata": {
    "tags": ["侵入式", "Neuralink", "1024通道"],
    "institution": "天津大学MBC",
    "authors": [" researcher_id_1"]
  }
}
```

**响应**:

```json
{
  "success": true,
  "data": {
    "id": "capsule_uuid",
    "type": "technical_route",
    "title": "侵入式BCI技术路线 - Neuralink方案",
    "datm_score": {
      "truth": 95,
      "goodness": 75,
      "beauty": 80,
      "intelligence": 90,
      "overall": 85.0
    },
    "version": 1,
    "status": "published",
    "created_at": "2026-02-09T08:20:00Z"
  }
}
```

### 2. 获取胶囊详情

**GET** `/capsules/{capsule_id}`

**响应**:

```json
{
  "success": true,
  "data": {
    "id": "capsule_uuid",
    "type": "technical_route",
    "title": "侵入式BCI技术路线 - Neuralink方案",
    "content": { ... },
    "datm_score": { ... },
    "metadata": { ... },
    "version": 1,
    "status": "published",
    "created_at": "2026-02-09T08:20:00Z",
    "updated_at": "2026-02-09T08:20:00Z"
  }
}
```

### 3. 搜索胶囊

**GET** `/capsules/search`

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| `type` | string | 胶囊类型 (technical_route/paper/case/experiment_data) |
| `query` | string | 关键词搜索 |
| `min_truth` | float | Truth 最低分 |
| `min_goodness` | float | Goodness 最低分 |
| `min_beauty` | float | Beauty 最低分 |
| `min_intelligence` | float | Intelligence 最低分 |
| `page` | int | 页码 (默认1) |
| `limit` | int | 每页数量 (默认20) |

**示例**:

```bash
GET /capsules/search?type=paper&query=EEG&min_truth=80
```

### 4. 更新胶囊

**PUT** `/capsules/{capsule_id}`

**请求体**: 同创建接口

### 5. 删除胶囊

**DELETE** `/capsules/{capsule_id}`

---

## DATM 评分 API

### 1. 计算 DATM 评分

**POST** `/datm/calculate`

**请求体**:

```json
{
  "capsule_type": "technical_route",
  "content": {
    "technology": "侵入式脑机接口",
    "approach": "Utah阵列电极",
    "parameters": { ... }
  },
  "evaluation_criteria": {
    "truth_factors": ["论文引用数", "实验验证", "理论支撑"],
    "goodness_factors": ["安全性记录", "伦理合规", "风险控制"],
    "beauty_factors": ["界面设计", "用户体验", "可视化效果"],
    "intelligence_factors": ["应用场景", "商业价值", "技术成熟度"]
  }
}
```

**响应**:

```json
{
  "success": true,
  "data": {
    "scores": {
      "truth": {
        "score": 95,
        "factors": {
          "论文引用数": 98,
          "实验验证": 94,
          "理论支撑": 93
        }
      },
      "goodness": {
        "score": 75,
        "factors": { ... }
      },
      "beauty": {
        "score": 80,
        "factors": { ... }
      },
      "intelligence": {
        "score": 90,
        "factors": { ... }
      }
    },
    "overall": 85.0,
    "confidence": 0.92
  }
}
```

### 2. 对比评分

**POST** `/datm/compare`

**请求体**:

```json
{
  "capsule_ids": ["id1", "id2", "id3"]
}
```

---

## 知识图谱 API

### 1. 获取图谱节点

**GET** `/graph/nodes`

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| `type` | string | 节点类型 (technology/institution/researcher/paper/case/capsule) |
| `page` | int | 页码 |
| `limit` | int | 每页数量 |

### 2. 获取图谱关系

**GET** `/graph/relationships`

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| `source_id` | string | 源节点ID |
| `target_id` | string | 目标节点ID |
| `type` | string | 关系类型 |

### 3. 创建节点

**POST** `/graph/nodes`

**请求体**:

```json
{
  "type": "technology",
  "name": "非侵入式脑机接口",
  "properties": {
    "description": "无需手术的BCI技术",
    "modalities": ["EEG", "MEG", "fNIRS"],
    "applications": ["康复医疗", "游戏控制"]
  }
}
```

### 4. 创建关系

**POST** `/graph/relationships`

**请求体**:

```json
{
  "source": "node_id_1",
  "target": "node_id_2",
  "type": "DERIVED_FROM",
  "properties": {
    "description": "从非侵入式技术衍生而来",
    "confidence": 0.95
  }
}
```

### 5. 路径查询

**POST** `/graph/path`

**请求体**:

```json
{
  "source": "node_id_1",
  "target": "node_id_2",
  "max_depth": 3
}
```

---

## 机构管理 API

### 1. 获取机构列表

**GET** `/institutions`

### 2. 获取机构详情

**GET** `/institutions/{institution_id}`

**响应**:

```json
{
  "success": true,
  "data": {
    "id": "institution_id",
    "name": "天津大学",
    "type": "university",
    "bc_focus": ["侵入式BCI", "神经信号处理"],
    "related_capsules": 45,
    "researchers": ["researcher_id_1", "researcher_id_2"]
  }
}
```

---

## 学者网络 API

### 1. 获取学者详情

**GET** `/researchers/{researcher_id}`

**响应**:

```json
{
  "success": true,
  "data": {
    "id": "researcher_id",
    "name": "张教授",
    "institution": "天津大学",
    "expertise": ["脑机接口", "信号处理"],
    "papers": ["paper_id_1", "paper_id_2"],
    "collaborators": ["researcher_id_3", "researcher_id_4"],
    "h_index": 25
  }
}
```

### 2. 学者关联查询

**GET** `/researchers/{researcher_id}/network`

---

## 汇报管理 API

### 1. 生成汇报

**POST** `/reports/generate`

**请求体**:

```json
{
  "type": "summary",  // summary/progress/strategy
  "period": {
    "start": "2026-01-01",
    "end": "2026-02-09"
  },
  "focus_areas": ["技术路线", "论文进展"],
  "format": "markdown"
}
```

### 2. 获取曹操汇报

**GET** `/reports/cao-cao`

### 3. 获取 KAI 执行报告

**GET** `/reports/kai`

---

## 错误响应

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": [
      {
        "field": "datm_score.truth",
        "message": "分数必须在0-100之间"
      }
    ]
  }
}
```

### 错误码列表

| 错误码 | 描述 |
|--------|------|
| `VALIDATION_ERROR` | 参数验证失败 |
| `NOT_FOUND` | 资源不存在 |
| `UNAUTHORIZED` | 未认证 |
| `FORBIDDEN` | 无权限 |
| `INTERNAL_ERROR` | 服务器内部错误 |

---

## WebSocket 接口

### 实时评分更新

**WS** `/ws/dtm/updates/{capsule_id}`

```javascript
// 客户端代码示例
const ws = new WebSocket('ws://localhost:8000/ws/dtm/updates/capsule_id');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('评分更新:', data);
};
```
