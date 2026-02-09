"""
MetaGPT SOP Engine - 标准化流程引擎
基于MetaGPT SOP模式创建的智能体协作流程引擎
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
from datetime import datetime
from abc import ABC, abstractmethod


class AgentRole(Enum):
    """智能体角色枚举"""
    STRATEGY_DESIGN = "strategy_design"      # 策略设计
    PLAN_EVALUATION = "plan_evaluation"      # 方案推演
    RISK_ASSESSMENT = "risk_assessment"      # 风险评估
    GENERAL = "general"                       # 通用


@dataclass
class Agent:
    """智能体数据类"""
    name: str                    # 智能体名称
    role: AgentRole              # 角色类型
    specialty: str               # 专业领域
    description: str = ""       # 描述
    capabilities: List[str] = field(default_factory=list)  # 能力列表


@dataclass
class SOPStep:
    """SOP步骤数据类"""
    step_id: str
    name: str
    description: str
    assigned_role: AgentRole
    dependencies: List[str] = field(default_factory=list)
    input_template: str = ""
    output_template: str = ""
    async_execute: Optional[Callable] = None


@dataclass
class SOPResult:
    """SOP执行结果"""
    success: bool
    task: str
    steps_executed: List[Dict[str, Any]]
    final_output: Any
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class StrategyScientistGroup:
    """谋略科学家组 - 核心智能体团队"""
    
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._initialize_team()
    
    def _initialize_team(self):
        """初始化谋略科学家团队"""
        
        # 贾诩 - 策略设计
        jiaxu = Agent(
            name="贾诩",
            role=AgentRole.STRATEGY_DESIGN,
            specialty="策略设计",
            description="顶尖谋略家，擅长制定整体战略规划",
            capabilities=["战略分析", "局势研判", "策略制定", "目标规划"]
        )
        self._agents["贾诩"] = jiaxu
        
        # 庞统 - 方案推演
        pangtong = Agent(
            name="庞统",
            role=AgentRole.PLAN_EVALUATION,
            specialty="方案推演",
            description="杰出的方案推演专家，精通各种方案的可行性分析",
            capabilities=["方案推演", "可行性分析", "情景模拟", "效果评估"]
        )
        self._agents["庞统"] = pangtong
        
        # 蒋济 - 风险评估
        jiangji = Agent(
            name="蒋济",
            role=AgentRole.RISK_ASSESSMENT,
            specialty="风险评估",
            description="严谨的风险评估专家，善于识别潜在风险",
            capabilities=["风险识别", "风险量化", "风险应对", "安全评估"]
        )
        self._agents["蒋济"] = jiangji
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """获取智能体"""
        return self._agents.get(name)
    
    def get_agents_by_role(self, role: AgentRole) -> List[Agent]:
        """根据角色获取智能体"""
        return [agent for agent in self._agents.values() if agent.role == role]
    
    def list_agents(self) -> List[Agent]:
        """列出所有智能体"""
        return list(self._agents.values())
    
    def add_agent(self, agent: Agent):
        """添加智能体"""
        self._agents[agent.name] = agent


class SOPTemplate:
    """SOP模板"""
    
    TEMPLATES = {
        "default": [
            SOPStep(
                step_id="strategy_design",
                name="策略设计",
                description="制定整体策略和目标",
                assigned_role=AgentRole.STRATEGY_DESIGN,
                input_template="任务：{task}",
                output_template="策略方案：{strategy_output}"
            ),
            SOPStep(
                step_id="plan_evaluation",
                name="方案推演",
                description="对策略方案进行推演和验证",
                assigned_role=AgentRole.PLAN_EVALUATION,
                dependencies=["strategy_design"],
                input_template="策略方案：{strategy_output}",
                output_template="推演结果：{evaluation_output}"
            ),
            SOPStep(
                step_id="risk_assessment",
                name="风险评估",
                description="评估方案风险并提供应对措施",
                assigned_role=AgentRole.RISK_ASSESSMENT,
                dependencies=["plan_evaluation"],
                input_template="推演结果：{evaluation_output}",
                output_template="风险报告：{risk_output}"
            )
        ],
        "quick": [
            SOPStep(
                step_id="strategy_design",
                name="策略设计",
                description="快速制定策略",
                assigned_role=AgentRole.STRATEGY_DESIGN,
                input_template="任务：{task}",
                output_template="策略方案：{strategy_output}"
            ),
            SOPStep(
                step_id="risk_assessment",
                name="风险评估",
                description="评估主要风险",
                assigned_role=AgentRole.RISK_ASSESSMENT,
                dependencies=["strategy_design"],
                input_template="策略方案：{strategy_output}",
                output_template="风险报告：{risk_output}"
            )
        ],
        "detailed": [
            SOPStep(
                step_id="analysis",
                name="问题分析",
                description="深入分析任务背景",
                assigned_role=AgentRole.STRATEGY_DESIGN,
                input_template="任务：{task}",
                output_template="分析报告：{analysis_output}"
            ),
            SOPStep(
                step_id="strategy_design",
                name="策略设计",
                description="制定详细策略",
                assigned_role=AgentRole.STRATEGY_DESIGN,
                dependencies=["analysis"],
                input_template="分析报告：{analysis_output}",
                output_template="策略方案：{strategy_output}"
            ),
            SOPStep(
                step_id="plan_evaluation",
                name="方案推演",
                description="多方案推演比较",
                assigned_role=AgentRole.PLAN_EVALUATION,
                dependencies=["strategy_design"],
                input_template="策略方案：{strategy_output}",
                output_template="推演结果：{evaluation_output}"
            ),
            SOPStep(
                step_id="risk_assessment",
                name="风险评估",
                description="全面风险评估",
                assigned_role=AgentRole.RISK_ASSESSMENT,
                dependencies=["plan_evaluation"],
                input_template="推演结果：{evaluation_output}",
                output_template="风险报告：{risk_output}"
            ),
            SOPStep(
                step_id="optimization",
                name="方案优化",
                description="整合所有反馈优化方案",
                assigned_role=AgentRole.STRATEGY_DESIGN,
                dependencies=["risk_assessment"],
                input_template="风险报告：{risk_output}",
                output_template="最终方案：{final_output}"
            )
        ]
    }
    
    @classmethod
    def get_template(cls, template_name: str) -> List[SOPStep]:
        """获取SOP模板"""
        return cls.TEMPLATES.get(template_name, cls.TEMPLATES["default"]).copy()
    
    @classmethod
    def get_available_templates(cls) -> List[str]:
        """获取可用模板列表"""
        return list(cls.TEMPLATES.keys())


class SOPEngine:
    """
    MetaGPT SOP引擎 - 标准化流程执行引擎
    
    基于MetaGPT SOP模式，支持：
    - 定义智能体角色
    - 执行标准化流程
    - 管理智能体团队
    - 自定义SOP模板
    """
    
    def __init__(self, team: Optional[StrategyScientistGroup] = None):
        """
        初始化SOP引擎
        
        Args:
            team: 智能体团队，如果不提供则创建默认团队
        """
        self.team = team or StrategyScientistGroup()
        self.custom_roles: Dict[str, AgentRole] = {}
        self.execution_history: List[SOPResult] = []
        self._step_outputs: Dict[str, Any] = {}
        
    async def define_role(self, name: str, specialty: str, 
                         description: str = "", 
                         capabilities: Optional[List[str]] = None) -> Agent:
        """
        定义智能体角色
        
        Args:
            name: 智能体名称
            specialty: 专业领域
            description: 描述
            capabilities: 能力列表
            
        Returns:
            Agent: 创建的智能体
        """
        role = AgentRole.GENERAL
        
        # 根据专业领域自动分配角色
        specialty_lower = specialty.lower()
        if "策略" in specialty or "战略" in specialty:
            role = AgentRole.STRATEGY_DESIGN
        elif "推演" in specialty or "方案" in specialty or "评估" in specialty:
            role = AgentRole.PLAN_EVALUATION
        elif "风险" in specialty:
            role = AgentRole.RISK_ASSESSMENT
        
        agent = Agent(
            name=name,
            role=role,
            specialty=specialty,
            description=description,
            capabilities=capabilities or []
        )
        
        self.team.add_agent(agent)
        self.custom_roles[name] = role
        
        return agent
    
    async def execute_sop(self, task: str, 
                         team: Optional[List[Agent]] = None,
                         template: str = "default",
                         custom_steps: Optional[List[SOPStep]] = None,
                         step_callbacks: Optional[Dict[str, Callable]] = None) -> SOPResult:
        """
        执行标准化流程
        
        Args:
            task: 执行的任务
            team: 使用的智能体团队
            template: SOP模板名称
            custom_steps: 自定义步骤列表
            step_callbacks: 步骤回调函数字典
            
        Returns:
            SOPResult: 执行结果
        """
        import time
        start_time = time.time()
        
        steps_executed = []
        errors = []
        self._step_outputs = {}
        
        # 获取执行步骤
        if custom_steps:
            steps = custom_steps
        else:
            steps = SOPTemplate.get_template(template)
        
        # 使用提供的团队或默认团队
        execution_team = {agent.name: agent for agent in (team or self.team.list_agents())}
        
        # 执行每个步骤
        for step in steps:
            step_result = {
                "step_id": step.step_id,
                "name": step.name,
                "status": "pending",
                "output": None,
                "error": None
            }
            
            try:
                # 检查依赖
                if step.dependencies:
                    unmet_deps = [dep for dep in step.dependencies 
                                 if dep not in self._step_outputs]
                    if unmet_deps:
                        step_result["status"] = "skipped"
                        step_result["error"] = f"未满足依赖: {unmet_deps}"
                        errors.append(f"步骤 {step.step_id} 因依赖未满足而跳过")
                        steps_executed.append(step_result)
                        continue
                
                # 查找可用的智能体
                agent = None
                for team_agent in execution_team.values():
                    if team_agent.role == step.assigned_role:
                        agent = team_agent
                        break
                
                if not agent:
                    # 尝试从全局团队获取
                    agents = self.team.get_agents_by_role(step.assigned_role)
                    if agents:
                        agent = agents[0]
                
                if not agent:
                    step_result["status"] = "skipped"
                    step_result["error"] = f"未找到角色为 {step.assigned_role.value} 的智能体"
                    errors.append(f"步骤 {step.step_id} 因无合适智能体而跳过")
                    steps_executed.append(step_result)
                    continue
                
                # 准备输入
                input_data = self._prepare_input(step, task)
                
                # 执行步骤
                output = await self._execute_step(step, input_data, agent, step_callbacks)
                
                # 保存输出
                self._step_outputs[step.step_id] = output
                step_result["output"] = output
                step_result["status"] = "completed"
                step_result["agent"] = agent.name
                
            except Exception as e:
                step_result["status"] = "failed"
                step_result["error"] = str(e)
                errors.append(f"步骤 {step.step_id} 执行失败: {str(e)}")
            
            steps_executed.append(step_result)
        
        execution_time = time.time() - start_time
        
        # 生成最终输出
        final_output = self._generate_final_output(steps, steps_executed)
        
        # 构建结果
        result = SOPResult(
            success=len(errors) == 0,
            task=task,
            steps_executed=steps_executed,
            final_output=final_output,
            errors=errors,
            execution_time=execution_time,
            metadata={
                "template": template,
                "steps_count": len(steps),
                "completed_steps": len([s for s in steps_executed if s["status"] == "completed"]),
                "team_size": len(execution_team)
            }
        )
        
        self.execution_history.append(result)
        
        return result
    
    def _prepare_input(self, step: SOPStep, task: str) -> Dict[str, Any]:
        """准备步骤输入"""
        # 填充输入模板
        input_data = {"task": task}
        
        # 添加依赖步骤的输出
        for dep in step.dependencies:
            if dep in self._step_outputs:
                input_data[f"step_{dep}_output"] = self._step_outputs[dep]
        
        return input_data
    
    async def _execute_step(self, step: SOPStep, input_data: Dict[str, Any],
                           agent: Agent, 
                           callbacks: Optional[Dict[str, Callable]]) -> Dict[str, Any]:
        """执行单个SOP步骤"""
        
        # 如果有自定义执行函数，调用它
        if step.async_execute:
            return await step.async_execute(input_data, agent)
        
        # 如果有回调函数，调用它
        if callbacks and step.step_id in callbacks:
            callback = callbacks[step.step_id]
            if asyncio.iscoroutinefunction(callback):
                return await callback(input_data, agent)
            else:
                return callback(input_data, agent)
        
        # 默认执行逻辑 - 返回步骤信息
        return {
            "step_id": step.step_id,
            "step_name": step.name,
            "agent_name": agent.name,
            "agent_role": agent.role.value,
            "input": input_data,
            "timestamp": datetime.now().isoformat(),
            "output_type": "default",
            "content": f"由 {agent.name} ({agent.specialty}) 执行的 {step.name} 步骤"
        }
    
    def _generate_final_output(self, steps: List[SOPStep], 
                               executed: List[Dict]) -> Dict[str, Any]:
        """生成最终输出"""
        completed_steps = [s for s in executed if s["status"] == "completed"]
        
        return {
            "success": len(completed_steps) == len(steps),
            "completed_steps": len(completed_steps),
            "total_steps": len(steps),
            "execution_summary": {
                "step_outputs": self._step_outputs,
                "step_results": completed_steps
            },
            "recommendations": self._generate_recommendations(completed_steps),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, completed_steps: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        step_names = [s["name"] for s in completed_steps if s["status"] == "completed"]
        
        if "策略设计" in step_names:
            recommendations.append("建议后续进行方案推演以验证策略可行性")
        if "方案推演" in step_names:
            recommendations.append("建议进行风险评估以确保方案安全")
        if "风险评估" in step_names:
            recommendations.append("所有关键步骤已完成，建议进入实施阶段")
        
        return recommendations
    
    def get_execution_history(self) -> List[SOPResult]:
        """获取执行历史"""
        return self.execution_history
    
    def clear_history(self):
        """清空执行历史"""
        self.execution_history.clear()
        self._step_outputs.clear()


# 便捷函数

async def create_default_sop_engine() -> SOPEngine:
    """创建默认的SOP引擎"""
    engine = SOPEngine()
    return engine


async def create_quick_sop(task: str, engine: Optional[SOPEngine] = None) -> SOPResult:
    """快速执行SOP"""
    engine = engine or await create_default_sop_engine()
    return await engine.execute_sop(task, template="quick")


async def create_detailed_sop(task: str, engine: Optional[SOPEngine] = None) -> SOPResult:
    """详细执行SOP"""
    engine = engine or await create_default_sop_engine()
    return await engine.execute_sop(task, template="detailed")


# 示例使用

async def example_usage():
    """示例用法"""
    
    # 创建引擎
    engine = await create_default_sop_engine()
    
    # 定义新角色
    await engine.define_role(
        name="新智能体",
        specialty="数据分析",
        description="数据分析专家",
        capabilities=["数据处理", "统计分析"]
    )
    
    # 执行标准SOP
    result = await engine.execute_sop(
        task="制定产品发布策略",
        template="detailed"
    )
    
    print(f"执行成功: {result.success}")
    print(f"执行时间: {result.execution_time:.2f}秒")
    print(f"完成步骤: {result.metadata['completed_steps']}/{result.metadata['steps_count']}")
    
    return result


if __name__ == "__main__":
    # 同步运行示例
    result = asyncio.run(example_usage())
    print("\n最终输出:")
    print(json.dumps(result.final_output, ensure_ascii=False, indent=2))
