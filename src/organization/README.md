# 组织架构模块

## 概述
提供组织架构管理功能，包括组、角色和人员的管理。

## 模块结构
- `models.py` - 组织模型定义
- `services.py` - 组织服务层
- `router.py` - API路由
- `__init__.py` - 模块导出

## 功能
- 组织架构查询
- 角色定义
- 人员管理
- 协作关系维护

## 组织结构
- **战略科学家组** - 负责战略制定、最终决策
- **谋略科学家组** - 负责风险评估、策略推演

## 使用方法
```python
from src.organization import OrganizationService

service = OrganizationService()
org = service.get_organization()
```
