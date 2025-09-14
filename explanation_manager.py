"""
AI可解释性管理器
提供处理链条透明度和结合SOP的可解释性功能
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ProcessingStage(Enum):
    """处理阶段枚举"""
    INPUT_VALIDATION = "input_validation"
    PROMPT_OPTIMIZATION = "prompt_optimization"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    AI_GENERATION = "ai_generation"
    QUALITY_ASSESSMENT = "quality_assessment"
    CONTENT_FORMATTING = "content_formatting"
    RESULT_VALIDATION = "result_validation"

@dataclass
class ProcessingStep:
    """处理步骤数据结构"""
    stage: ProcessingStage
    title: str
    description: str
    timestamp: str
    duration: float
    success: bool
    details: Dict[str, Any]
    quality_score: Optional[float] = None
    evidence: Optional[str] = None

class ExplanationManager:
    """AI可解释性管理器"""
    
    def __init__(self):
        self.processing_steps: List[ProcessingStep] = []
        self.sop_guidelines = self._load_sop_guidelines()
        self.quality_metrics = {}
        
    def start_processing(self):
        """开始处理过程"""
        self.processing_steps.clear()
        self.quality_metrics.clear()
        logger.info("🔄 开始处理链条追踪")
    
    def add_processing_step(self, 
                          stage: ProcessingStage,
                          title: str,
                          description: str,
                          success: bool,
                          details: Dict[str, Any],
                          duration: float = 0.0,
                          quality_score: Optional[float] = None,
                          evidence: Optional[str] = None):
        """添加处理步骤"""
        step = ProcessingStep(
            stage=stage,
            title=title,
            description=description,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            duration=duration,
            success=success,
            details=details,
            quality_score=quality_score,
            evidence=evidence
        )
        
        self.processing_steps.append(step)
        logger.info(f"📝 记录处理步骤: {title} - {'✅' if success else '❌'}")
    
    def get_processing_explanation(self) -> str:
        """获取处理过程的详细说明"""
        if not self.processing_steps:
            return "暂无处理记录"
        
        explanation = self._generate_explanation_header()
        explanation += self._generate_sop_compliance_report()
        explanation += self._generate_processing_steps_report()
        explanation += self._generate_quality_metrics_report()
        explanation += self._generate_evidence_summary()
        
        return explanation
    
    def _generate_explanation_header(self) -> str:
        """生成说明头部"""
        total_steps = len(self.processing_steps)
        successful_steps = sum(1 for step in self.processing_steps if step.success)
        success_rate = (successful_steps / total_steps * 100) if total_steps > 0 else 0
        
        return f"""
# 🔍 AI生成过程详细说明

## 📊 处理概览
- **总处理步骤**: {total_steps}
- **成功步骤**: {successful_steps}
- **成功率**: {success_rate:.1f}%
- **处理时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

"""
    
    def _generate_sop_compliance_report(self) -> str:
        """生成SOP合规报告"""
        return f"""
## 📋 SOP (标准操作程序) 合规报告

### 🎯 质量保证标准
{self._format_sop_guidelines()}

### ✅ 合规性检查
- **输入验证**: {'✅ 通过' if self._check_sop_compliance('input_validation') else '❌ 未通过'}
- **知识获取**: {'✅ 通过' if self._check_sop_compliance('knowledge_retrieval') else '❌ 未通过'}
- **AI生成**: {'✅ 通过' if self._check_sop_compliance('ai_generation') else '❌ 未通过'}
- **质量评估**: {'✅ 通过' if self._check_sop_compliance('quality_assessment') else '❌ 未通过'}
- **内容格式化**: {'✅ 通过' if self._check_sop_compliance('content_formatting') else '❌ 未通过'}

---

"""
    
    def _generate_processing_steps_report(self) -> str:
        """生成处理步骤报告"""
        report = "## 🔄 详细处理步骤\n\n"
        
        for i, step in enumerate(self.processing_steps, 1):
            status_icon = "✅" if step.success else "❌"
            quality_info = f" (质量分: {step.quality_score:.1f})" if step.quality_score else ""
            
            report += f"""
### 步骤 {i}: {step.title} {status_icon}

- **阶段**: {self._get_stage_name(step.stage)}
- **时间**: {step.timestamp}
- **耗时**: {step.duration:.2f}秒{quality_info}
- **描述**: {step.description}

**详细信息**:
{self._format_step_details(step.details)}

"""
            
            if step.evidence:
                report += f"**证据**: {step.evidence}\n\n"
        
        return report + "---\n\n"
    
    def _generate_quality_metrics_report(self) -> str:
        """生成质量指标报告"""
        if not self.quality_metrics:
            return ""
        
        report = "## 📈 质量指标详情\n\n"
        
        for metric_name, metric_value in self.quality_metrics.items():
            report += f"- **{metric_name}**: {metric_value}\n"
        
        return report + "\n---\n\n"
    
    def _generate_evidence_summary(self) -> str:
        """生成证据总结"""
        evidence_steps = [step for step in self.processing_steps if step.evidence]
        
        if not evidence_steps:
            return ""
        
        report = "## 🧾 证据总结\n\n"
        
        for i, step in enumerate(evidence_steps, 1):
            report += f"**{i}. {step.title}**\n{step.evidence}\n\n"
        
        return report
    
    def _load_sop_guidelines(self) -> Dict[str, Any]:
        """加载SOP指导原则"""
        return {
            "input_validation": {
                "title": "输入验证标准",
                "requirements": [
                    "用户输入长度 >= 10字符",
                    "输入内容包含产品描述",
                    "无恶意内容和敏感信息"
                ]
            },
            "knowledge_retrieval": {
                "title": "外部知识获取",
                "requirements": [
                    "MCP服务连接状态检查",
                    "参考链接有效性验证",
                    "知识内容相关性评估"
                ]
            },
            "ai_generation": {
                "title": "AI内容生成",
                "requirements": [
                    "使用专业的系统提示词",
                    "生成内容结构完整",
                    "包含必要的技术细节"
                ]
            },
            "quality_assessment": {
                "title": "质量评估标准",
                "requirements": [
                    "内容完整性检查",
                    "Mermaid图表语法验证",
                    "链接有效性检查",
                    "日期准确性验证"
                ]
            },
            "content_formatting": {
                "title": "内容格式化",
                "requirements": [
                    "Markdown格式规范",
                    "添加时间戳和元信息",
                    "增强提示词显示效果"
                ]
            }
        }
    
    def _format_sop_guidelines(self) -> str:
        """格式化SOP指导原则"""
        formatted = ""
        for key, guideline in self.sop_guidelines.items():
            formatted += f"**{guideline['title']}**:\n"
            for requirement in guideline['requirements']:
                formatted += f"- {requirement}\n"
            formatted += "\n"
        return formatted
    
    def _check_sop_compliance(self, stage_name: str) -> bool:
        """检查SOP合规性"""
        relevant_steps = [step for step in self.processing_steps 
                         if step.stage.value == stage_name]
        return len(relevant_steps) > 0 and all(step.success for step in relevant_steps)
    
    def _get_stage_name(self, stage: ProcessingStage) -> str:
        """获取阶段名称"""
        stage_names = {
            ProcessingStage.INPUT_VALIDATION: "输入验证",
            ProcessingStage.PROMPT_OPTIMIZATION: "提示词优化",
            ProcessingStage.KNOWLEDGE_RETRIEVAL: "知识获取",
            ProcessingStage.AI_GENERATION: "AI生成",
            ProcessingStage.QUALITY_ASSESSMENT: "质量评估",
            ProcessingStage.CONTENT_FORMATTING: "内容格式化",
            ProcessingStage.RESULT_VALIDATION: "结果验证"
        }
        return stage_names.get(stage, stage.value)
    
    def _format_step_details(self, details: Dict[str, Any]) -> str:
        """格式化步骤详情"""
        formatted = ""
        for key, value in details.items():
            if isinstance(value, dict):
                formatted += f"  - **{key}**: {self._format_nested_dict(value)}\n"
            elif isinstance(value, list):
                formatted += f"  - **{key}**: {', '.join(str(item) for item in value)}\n"
            else:
                formatted += f"  - **{key}**: {value}\n"
        return formatted
    
    def _format_nested_dict(self, nested_dict: Dict[str, Any]) -> str:
        """格式化嵌套字典"""
        items = []
        for key, value in nested_dict.items():
            items.append(f"{key}={value}")
        return f"{{{', '.join(items)}}}"
    
    def update_quality_metrics(self, metrics: Dict[str, Any]):
        """更新质量指标"""
        self.quality_metrics.update(metrics)
        
    def get_trust_score(self) -> float:
        """计算信任分数"""
        if not self.processing_steps:
            return 0.0
        
        # 基于成功率和质量分数计算信任分数
        success_rate = sum(1 for step in self.processing_steps if step.success) / len(self.processing_steps)
        
        quality_scores = [step.quality_score for step in self.processing_steps if step.quality_score]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5
        
        # 信任分数 = 成功率 * 0.6 + 平均质量分数 * 0.4
        trust_score = success_rate * 0.6 + (avg_quality / 100) * 0.4
        
        return round(trust_score * 100, 1)

# 全局可解释性管理器实例
explanation_manager = ExplanationManager()