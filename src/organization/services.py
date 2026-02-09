"""组织服务层"""

from typing import Dict, List, Optional
from .models import ORGANIZATION, Group, Person, get_group_from_dict


class OrganizationService:
    """组织服务类"""
    
    def __init__(self):
        self.org_data = ORGANIZATION.copy()
    
    def get_organization(self) -> Dict[str, Dict]:
        """获取完整组织架构"""
        return self.org_data
    
    def get_group(self, group_key: str) -> Optional[Dict]:
        """获取指定组信息"""
        return self.org_data.get(group_key)
    
    def get_all_groups(self) -> List[Dict]:
        """获取所有组列表"""
        return list(self.org_data.values())
    
    def get_leaders(self) -> List[Dict]:
        """获取所有组长信息"""
        leaders = []
        for group_key, group_data in self.org_data.items():
            leader_info = group_data.get("leader", {})
            leader_info["group"] = group_data.get("name")
            leaders.append(leader_info)
        return leaders
    
    def get_groups_count(self) -> int:
        """获取组数量"""
        return len(self.org_data)
    
    def get_total_members(self) -> int:
        """获取总人数"""
        return sum(group.get("members", 0) for group in self.org_data.values())
    
    def search_person(self, name: str) -> List[Dict]:
        """搜索人员"""
        results = []
        for group_key, group_data in self.org_data.items():
            leader = group_data.get("leader", {})
            if name in leader.get("name", ""):
                results.append({
                    "name": leader.get("name"),
                    "role": leader.get("role"),
                    "group": group_data.get("name"),
                    "group_key": group_key
                })
        return results
    
    def get_core_functions(self) -> Dict[str, str]:
        """获取各组核心职能"""
        functions = {}
        for group_key, group_data in self.org_data.items():
            functions[group_data.get("name")] = group_data.get("core_function", "")
        return functions
