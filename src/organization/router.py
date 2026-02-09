"""API路由"""

from typing import Dict, List
from fastapi import APIRouter
from .services import OrganizationService

router = APIRouter(prefix="/organization", tags=["组织架构"])
service = OrganizationService()


@router.get("")
def get_organization() -> Dict[str, Dict]:
    """获取完整组织架构"""
    return service.get_organization()


@router.get("/groups")
def get_all_groups() -> List[Dict]:
    """获取所有组列表"""
    return service.get_all_groups()


@router.get("/groups/{group_key}")
def get_group(group_key: str) -> Dict:
    """获取指定组信息"""
    return service.get_group(group_key)


@router.get("/leaders")
def get_leaders() -> List[Dict]:
    """获取所有组长"""
    return service.get_leaders()


@router.get("/stats")
def get_stats() -> Dict:
    """获取组织统计信息"""
    return {
        "groups_count": service.get_groups_count(),
        "total_members": service.get_total_members()
    }


@router.get("/search/person")
def search_person(name: str) -> List[Dict]:
    """搜索人员"""
    return service.search_person(name)


@router.get("/functions")
def get_core_functions() -> Dict[str, str]:
    """获取各组核心职能"""
    return service.get_core_functions()
