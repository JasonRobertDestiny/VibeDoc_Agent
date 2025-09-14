"""
VibeDoc Agent应用配置文件
支持多环境、多MCP服务配置
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

@dataclass
class MCPServiceConfig:
    """MCP服务配置"""
    name: str
    url: Optional[str]
    api_key: Optional[str] = None
    timeout: int = 30
    enabled: bool = True
    health_check_path: str = "/health"

@dataclass
class AIModelConfig:
    """AI模型配置"""
    provider: str = "siliconflow"
    model_name: str = "Qwen/Qwen2.5-72B-Instruct"
    api_key: str = ""
    api_url: str = "https://api.siliconflow.cn/v1/chat/completions"
    max_tokens: int = 8000
    temperature: float = 0.7
    timeout: int = 300  # 增加到300秒（5分钟）解决超时问题

class AppConfig:
    """应用总配置类"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.port = int(os.getenv("PORT", "7860"))
        
        # AI模型配置
        self.ai_model = AIModelConfig(
            api_key=os.getenv("SILICONFLOW_API_KEY", ""),
            timeout=int(os.getenv("API_TIMEOUT", "300"))
        )
        
        # 简化MCP服务配置 - 直接使用内置URL，避免环境变量复杂性
        self.mcp_services = {
            "deepwiki": MCPServiceConfig(
                name="DeepWiki MCP",
                url="https://mcp.api-inference.modelscope.net/d4ed08072d2846/sse",
                timeout=int(os.getenv("MCP_TIMEOUT", "60")),
                enabled=True  # 默认启用，简化配置
            ),
            "fetch": MCPServiceConfig(
                name="Fetch MCP", 
                url="https://mcp.api-inference.modelscope.net/6ec508e067dc41/sse",
                timeout=int(os.getenv("MCP_TIMEOUT", "60")),
                enabled=True  # 默认启用，简化配置
            )
        }
        
        # 应用功能配置
        self.features = {
            "external_knowledge": any(service.enabled for service in self.mcp_services.values()),
            "multi_mcp_fusion": sum(service.enabled for service in self.mcp_services.values()) > 1
        }
        
        # 日志配置
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    def get_enabled_mcp_services(self) -> List[MCPServiceConfig]:
        """获取已启用的MCP服务列表"""
        return [service for service in self.mcp_services.values() if service.enabled]
    
    def get_mcp_service(self, service_key: str) -> Optional[MCPServiceConfig]:
        """获取指定的MCP服务配置"""
        return self.mcp_services.get(service_key)
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == "production"
    
    def validate_config(self) -> Dict[str, str]:
        """验证配置完整性"""
        errors = {}
        
        # 验证AI模型配置
        if not self.ai_model.api_key:
            errors["ai_model"] = "SILICONFLOW_API_KEY 未配置"
        
        # 验证MCP服务配置
        enabled_services = self.get_enabled_mcp_services()
        if not enabled_services:
            errors["mcp_services"] = "未配置任何MCP服务，某些功能将受限"
        
        return errors
    
    def get_config_summary(self) -> Dict:
        """获取配置摘要信息"""
        enabled_services = self.get_enabled_mcp_services()
        
        return {
            "environment": self.environment,
            "debug": self.debug,
            "port": self.port,
            "ai_model": {
                "provider": self.ai_model.provider,
                "model": self.ai_model.model_name,
                "configured": bool(self.ai_model.api_key)
            },
            "mcp_services": {
                "total": len(self.mcp_services),
                "enabled": len(enabled_services),
                "services": [service.name for service in enabled_services]
            },
            "features": self.features
        }

# 全局配置实例
config = AppConfig()

# 常用配置常量
EXAMPLE_CONFIGURATIONS = {
    "single_mcp": {
        "description": "单MCP服务示例 - 贴近大众生活",
        "examples": [
            {
                "idea": "开发一个智能投资助手，提供股票基金分析和个性化投资建议",
                "reference_url": "https://docs.deepwiki.org/finance/investment-analysis",
                "expected_services": ["deepwiki"]
            },
            {
                "idea": "创建一个在线学习平台，支持课程管理和学习进度跟踪",
                "reference_url": "https://docs.deepwiki.org/education/online-learning",
                "expected_services": ["deepwiki"]
            }
        ]
    },
    "dual_mcp": {
        "description": "双MCP服务协作示例 - 实用场景", 
        "examples": [
            {
                "idea": "构建一个智能健康管理系统，包含运动记录和健康分析功能",
                "reference_url": "https://github.com/microsoft/healthcare-bot",
                "expected_services": ["fetch", "deepwiki"]
            },
            {
                "idea": "开发一个家庭理财规划工具，支持预算管理和投资建议",
                "reference_url": "https://github.com/firefly-iii/firefly-iii",
                "expected_services": ["fetch", "deepwiki"]
            }
        ]
    },
    "triple_mcp": {
        "description": "双MCP服务完整协作示例",
        "examples": [
            {
                "idea": "构建数字藏品交易平台，集成NFT展示和社区功能",
                "reference_url": "https://docs.deepwiki.org/blockchain/nft-marketplace",
                "expected_services": ["deepwiki", "fetch"]
            },
            {
                "idea": "创建智能教育助手，结合AI答疑和学习资源推荐",
                "reference_url": "https://docs.deepwiki.org/ai/education-assistant",
                "expected_services": ["deepwiki", "fetch"]
            }
        ]
    }
}