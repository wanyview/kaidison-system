"""组织模型定义"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Role:
    """角色模型"""
    name: str
    description: str = ""


@dataclass
class Person:
    """人员模型"""
    name: str
    role: str
    title: Optional[str] = None
    department: Optional[str] = None
    skills: List[str] = field(default_factory=list)


@dataclass
class Group:
    """组织组模型"""
    key: str
    name: str
    leader: Person
    members: int
    core_function: str
    members_detail: List[Person] = field(default_factory=list)


# 组织结构定义
ORGANIZATION: Dict[str, Dict] = {
    "strategic_group": {
        "name": "战略科学家组",
        "leader": {"name": "诸葛亮", "role": "组长"},
        "members": 10,
        "core_function": "战略制定、最终决策"
    },
    "tactical_group": {
        "name": "谋略科学家组",
        "leader": {"name": "贾诩", "role": "组长"},
        "members": 10,
        "core_function": "风险评估、策略推演"
    }
}


def get_group_from_dict(data: Dict) -> Group:
    """从字典创建Group对象"""
    leader_data = data.get("leader", {})
    leader = Person(
        name=leader_data.get("name", ""),
        role=leader_data.get("role", "")
    )
    return Group(
        key="",
        name=data.get("name", ""),
        leader=leader,
        members=data.get("members", 0),
        core_function=data.get("core_function", "")
    )
