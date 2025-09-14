"""
提示词优化器模块
使用AI优化用户输入的创意描述，提升生成报告的质量
"""

import requests
import json
import logging
from typing import Tuple, Dict, Any, Optional
from config import config

logger = logging.getLogger(__name__)

class PromptOptimizer:
    """用户输入提示词优化器"""
    
    def __init__(self):
        self.api_key = config.ai_model.api_key
        self.api_url = config.ai_model.api_url
        self.model_name = config.ai_model.model_name
        
    def optimize_user_input(self, user_idea: str) -> Tuple[bool, str, str]:
        """
        优化用户输入的创意描述
        
        Args:
            user_idea: 用户原始输入
            
        Returns:
            Tuple[bool, str, str]: (成功状态, 优化后的描述, 优化建议)
        """
        if not self.api_key:
            return False, user_idea, "API密钥未配置，无法优化描述"
        
        if not user_idea or len(user_idea.strip()) < 5:
            return False, user_idea, "输入内容过短，无法优化"
        
        try:
            # 构建优化提示词
            optimization_prompt = self._build_optimization_prompt(user_idea)
            
            # 调用AI优化
            response = self._call_ai_service(optimization_prompt)
            
            if response['success']:
                result = self._parse_optimization_result(response['data'])
                return True, result['optimized_idea'], result['suggestions']
            else:
                logger.error(f"AI优化失败: {response['error']}")
                return False, user_idea, f"优化失败: {response['error']}"
                
        except Exception as e:
            logger.error(f"提示词优化异常: {e}")
            return False, user_idea, f"优化过程出错: {str(e)}"
    
    def _build_optimization_prompt(self, user_idea: str) -> str:
        """构建优化提示词"""
        return f"""你是一个专业的产品经理和技术顾问，擅长将用户的简单想法扩展为详细的产品描述。

用户原始输入：
{user_idea}

请帮助优化这个创意描述，使其更加详细、具体和专业。优化后的描述应该包含以下要素：

1. **核心功能**：明确产品的主要功能和价值
2. **目标用户**：定义产品的目标用户群体
3. **使用场景**：描述产品的典型使用场景
4. **技术特点**：提及可能需要的关键技术特性
5. **商业价值**：阐述产品的市场价值和竞争优势

请按以下JSON格式输出：
{{
    "optimized_idea": "优化后的详细产品描述",
    "key_improvements": [
        "改进点1",
        "改进点2",
        "改进点3"
    ],
    "suggestions": "进一步优化建议"
}}

要求：
- 保持原始创意的核心思想
- 使用专业但易懂的语言
- 长度控制在200-400字之间
- 突出产品的创新性和实用性"""

    def _call_ai_service(self, prompt: str) -> Dict[str, Any]:
        """调用AI服务"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=300  # 优化：创意描述优化超时时间为300秒（5分钟）
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                return {"success": True, "data": content}
            else:
                return {"success": False, "error": f"API调用失败: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_optimization_result(self, ai_response: str) -> Dict[str, Any]:
        """解析AI优化结果"""
        try:
            # 尝试解析JSON
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx]
                result = json.loads(json_str)
                
                return {
                    "optimized_idea": result.get("optimized_idea", ""),
                    "suggestions": result.get("suggestions", ""),
                    "key_improvements": result.get("key_improvements", [])
                }
            else:
                # 如果无法解析JSON，直接返回原始响应
                return {
                    "optimized_idea": ai_response,
                    "suggestions": "AI返回了优化建议，但格式需要调整",
                    "key_improvements": []
                }
                
        except json.JSONDecodeError:
            # JSON解析失败，返回原始响应
            return {
                "optimized_idea": ai_response,
                "suggestions": "AI返回了优化建议，但格式需要调整",
                "key_improvements": []
            }
    
    def get_optimization_examples(self) -> list:
        """获取优化示例"""
        return [
            {
                "original": "我想做一个购物网站",
                "optimized": "开发一个面向年轻消费者的智能购物平台，集成AI推荐系统、社交分享功能和个性化用户体验。平台将提供多品类商品展示、智能搜索、用户评价系统和便捷的移动支付功能，旨在为用户提供个性化的购物体验和高质量的商品推荐服务。",
                "improvements": ["明确目标用户", "定义核心功能", "突出技术特色"]
            },
            {
                "original": "想搞个学习系统",
                "optimized": "构建一个基于AI的个性化在线学习管理系统，支持多媒体内容展示、学习进度跟踪、智能题库管理和师生互动功能。系统将为教育机构和个人学习者提供完整的数字化学习解决方案，包括课程管理、作业批改、学习分析和成绩评估等功能。",
                "improvements": ["扩展功能描述", "明确应用场景", "增加技术亮点"]
            }
        ]

# 全局优化器实例
prompt_optimizer = PromptOptimizer()