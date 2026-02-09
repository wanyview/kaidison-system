"""
SOP Engine - MetaGPT标准化流程引擎模块

基于MetaGPT SOP模式的智能体协作流程引擎

主要类:
- SOPEngine: 核心流程引擎
- StrategyScientistGroup: 谋略科学家团队
- Agent: 智能体数据类
- SOPStep: SOP步骤数据类
- SOPResult: 执行结果数据类
- AgentRole: 角色枚举

模板:
- default: 默认三步流程
- quick: 快速两步流程  
- detailed: 详细五步流程
"""

from .sop_engine import (
    SOPEngine,
    StrategyScientistGroup,
    Agent,
    SOPStep,
    SOPResult,
    AgentRole,
    SOPTemplate,
    create_default_sop_engine,
    create_quick_sop,
    create_detailed_sop,
    example_usage
)

__version__ = "1.0.0"
__all__ = [
    "SOPEngine",
    "StrategyScientistGroup", 
    "Agent",
    "SOPStep",
    "SOPResult",
    "AgentRole",
    "SOPTemplate",
    "create_default_sop_engine",
    "create_quick_sop",
    "create_detailed_sop",
    "example_usage"
]
