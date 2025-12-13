"""
Prompt Templates

This module contains prompt templates for LLM analysis.
All prompts instruct models to respond in Chinese.
"""

from typing import Dict, Any
import json


# System prompt for analyst models
ANALYST_PROMPT = """你是一位专业的跨境电商市场分析师。你将收到结构化的市场数据JSON，包括销售数据、用户评论和产品评价。

你的任务是基于这些数据进行深入分析，并用中文撰写详细的分析报告。

分析要点：
1. 市场格局：分析市场规模、竞争程度、价格分布、销量集中度
2. 用户洞察：总结用户购买理由、使用场景、目标人群
3. 产品机会：识别市场空白、未满足的需求、产品改进方向
4. 风险因素：总结常见问题、客户投诉、需要避免的陷阱
5. 建议策略：提供具体的产品定位、定价、营销建议

请基于数据进行分析，避免臆测。所有分析必须用中文输出。
"""


# System prompt for judge model
JUDGE_PROMPT = """你是一位资深的市场分析评审专家。你将收到两份由不同AI模型撰写的市场分析报告。

你的任务是：
1. 仔细阅读并比较两份报告
2. 识别两份报告的共同观点和分歧点
3. 评估每个观点的合理性和数据支撑
4. 综合两份报告的优点，输出一份最终的综合分析报告

最终报告应该：
- 明确指出哪些观点是两个模型都认同的
- 对于分歧点，说明你的判断和理由
- 整合两份报告中最有价值的洞察
- 保持逻辑清晰、结构完整

所有输出必须用中文。
"""


def get_analysis_prompt(data_summary: Dict[str, Any]) -> str:
    """
    Generate analysis prompt with data summary.
    
    Args:
        data_summary: Structured JSON data from all stages
        
    Returns:
        Formatted prompt for analyst model
    """
    # Convert data to formatted JSON string
    data_json = json.dumps(data_summary, ensure_ascii=False, indent=2)
    
    prompt = f"""请基于以下结构化的市场数据进行分析：

<市场数据>
{data_json}
</市场数据>

请按照以下结构撰写分析报告（用中文）：

## 一、市场概况
- 市场规模和趋势
- 竞争格局（红海/蓝海）
- 主流价格带和销量分布

## 二、用户洞察
- 主要购买理由
- 目标用户群体
- 典型使用场景

## 三、产品分析
- 热门产品特征
- 用户必需的关键因素
- 常见的产品问题和陷阱

## 四、机会识别
- 未被满足的需求
- 潜在的产品创新方向
- 市场空白点

## 五、策略建议
- 产品定位建议
- 定价策略建议
- 营销和运营建议
- 风险提示

请确保每个部分都有具体的数据支撑，避免空泛的描述。
"""
    
    return prompt


def get_judge_prompt(report1: str, provider1: str, report2: str, provider2: str) -> str:
    """
    Generate judge prompt with two reports.
    
    Args:
        report1: First analysis report
        provider1: Name of first provider
        report2: Second analysis report
        provider2: Name of second provider
        
    Returns:
        Formatted prompt for judge model
    """
    prompt = f"""请评审和综合以下两份市场分析报告：

<报告A - 来自{provider1}>
{report1}
</报告A>

<报告B - 来自{provider2}>
{report2}
</报告B>

请按照以下结构输出综合分析报告（用中文）：

## 评审总结

### 共同观点
列出两份报告都认同的关键观点

### 分歧点
列出两份报告存在分歧的地方，并说明你的判断

## 综合分析报告

### 一、市场概况
综合两份报告的市场分析

### 二、用户洞察
综合两份报告的用户分析

### 三、产品分析
综合两份报告的产品分析

### 四、机会识别
综合两份报告的机会识别

### 五、策略建议
综合两份报告的策略建议

### 六、风险提示
综合两份报告的风险提示

请确保综合报告既保留两份报告的优点，又有你自己的专业判断。
"""
    
    return prompt


# Prompt for data validation (optional)
DATA_VALIDATION_PROMPT = """请检查以下市场数据的完整性和合理性：

{data_json}

检查要点：
1. 数据字段是否完整
2. 数值是否在合理范围内
3. 是否存在明显的数据异常

如有问题，请用中文列出。如果数据正常，请回复"数据验证通过"。
"""
