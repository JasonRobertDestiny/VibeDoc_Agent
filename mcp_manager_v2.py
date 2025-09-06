import asyncio
import json
import os
import logging
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from dataclasses import dataclass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPConfig:
    """MCP服务配置"""
    url: str
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}

class MCPClient:
    """
    MCP客户端，基于魔塔MCP服务的SSE实现
    参考le-agent项目的架构
    """
    
    def __init__(self, name: str, config: MCPConfig):
        self.name = name
        self.config = config
        self.timeout = 30
        self.is_connected = False
        self.error = None
        self.tool_info = []
        self.session_id = None
        self.messages_endpoint = None
        
    async def _connect_sse(self) -> bool:
        """建立SSE连接并获取消息端点"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.config.url, 
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        # 读取SSE流来获取endpoint信息
                        async for line in response.content:
                            line_str = line.decode('utf-8').strip()
                            
                            if line_str.startswith('event: endpoint'):
                                continue
                            elif line_str.startswith('data: '):
                                endpoint_path = line_str[6:].strip()
                                if endpoint_path.startswith('/messages/'):
                                    # 提取session_id
                                    match = re.search(r'session_id=([a-f0-9-]+)', endpoint_path)
                                    if match:
                                        self.session_id = match.group(1)
                                        # 构建完整的messages端点URL
                                        base_url = self.config.url.replace('/sse', '')
                                        self.messages_endpoint = f"{base_url}{endpoint_path}"
                                        logger.info(f"Connected to {self.name}: {self.messages_endpoint}")
                                        self.is_connected = True
                                        return True
                                break
                    else:
                        logger.error(f"Failed to connect to {self.name}: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error connecting to {self.name}: {e}")
            self.error = e
            return False
        
        return False
        
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """调用MCP工具"""
        try:
            # 确保已连接
            if not self.is_connected:
                if not await self._connect_sse():
                    logger.error(f"Failed to connect to {self.name}")
                    return None
            
            if not self.messages_endpoint:
                logger.error(f"No messages endpoint available for {self.name}")
                return None
                
            import aiohttp
            
            # 构建MCP协议消息
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                **self.config.headers
            }
            
            logger.info(f"Calling {self.name}.{tool_name} with arguments: {arguments}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.messages_endpoint,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        result_data = await response.json()
                        
                        # 解析MCP响应
                        if 'result' in result_data:
                            result = result_data['result']
                            if 'content' in result and isinstance(result['content'], list):
                                text_parts = []
                                for item in result['content']:
                                    if isinstance(item, dict) and item.get('type') == 'text':
                                        text_parts.append(item.get('text', ''))
                                if text_parts:
                                    result_text = '\n'.join(text_parts)
                                    logger.info(f"Successfully got {len(result_text)} characters from {self.name}")
                                    return result_text
                                    
                        elif 'error' in result_data:
                            error_msg = result_data['error'].get('message', 'Unknown error')
                            logger.error(f"MCP service error: {error_msg}")
                            return None
                            
                        logger.warning(f"Unexpected response format from {self.name}: {result_data}")
                        return None
                    else:
                        error_text = await response.text()
                        logger.error(f"HTTP {response.status} from {self.name}: {error_text}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error(f"Timeout calling {self.name}.{tool_name}")
            return None
        except Exception as e:
            logger.error(f"Error calling {self.name}.{tool_name}: {str(e)}")
            return None

class MCPManager:
    """MCP管理器，基于le-agent架构优化"""
    
    def __init__(self, config_path: str = ".mcp-config.json"):
        self.config_path = config_path
        self.clients: Dict[str, MCPClient] = {}
        self.is_initialized = False
        self._load_config()
        
    def _load_config(self):
        """加载MCP配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                for name, config in config_data.items():
                    mcp_config = MCPConfig(
                        url=config['url'],
                        headers=config.get('headers', {})
                    )
                    self.clients[name] = MCPClient(name, mcp_config)
                    
                logger.info(f"Loaded {len(self.clients)} MCP clients: {list(self.clients.keys())}")
                self.is_initialized = True
            else:
                logger.warning(f"MCP config file not found: {self.config_path}")
                
        except Exception as e:
            logger.error(f"Error loading MCP config: {str(e)}")
    
    def get_service_for_url(self, url: str) -> Optional[str]:
        """根据URL模式确定使用哪个MCP服务"""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Wikipedia相关 - 使用deepwiki
            if any(wiki in domain for wiki in ['wikipedia.org', 'wiki']):
                return 'mcp-deepwiki' if 'mcp-deepwiki' in self.clients else None
            
            # 默认使用fetch服务
            return 'fetch' if 'fetch' in self.clients else None
            
        except Exception as e:
            logger.error(f"Error determining service for URL {url}: {str(e)}")
            return 'fetch' if 'fetch' in self.clients else None
    
    async def fetch_content(self, url: str) -> Optional[str]:
        """从URL获取内容，使用适当的MCP服务"""
        try:
            service_name = self.get_service_for_url(url)
            if not service_name:
                logger.error(f"No suitable MCP service found for URL: {url}")
                return None
            
            client = self.clients.get(service_name)
            if not client:
                logger.error(f"MCP client '{service_name}' not available")
                return None
            
            logger.info(f"Using MCP service '{service_name}' for URL: {url}")
            
            if service_name == 'mcp-deepwiki':
                # 使用DeepWiki服务
                result = await client.call_tool(
                    tool_name='search_articles',
                    arguments={'query': url}
                )
            else:
                # 使用Fetch服务
                result = await client.call_tool(
                    tool_name='fetch',
                    arguments={'url': url}
                )
            
            if result:
                logger.info(f"Successfully fetched {len(result)} characters from {url}")
                return result
            else:
                logger.warning(f"No content returned from MCP service for {url}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {str(e)}")
            return None

    def get_client_info(self) -> List[Dict[str, Any]]:
        """获取所有客户端信息"""
        info = []
        for name, client in self.clients.items():
            info.append({
                "name": name,
                "status": "connected" if client.is_connected else "disconnected",
                "error": str(client.error) if client.error else None,
                "endpoint": client.messages_endpoint
            })
        return info

    async def test_connection(self) -> Dict[str, Dict[str, Any]]:
        """测试所有MCP服务连接"""
        results = {}
        for name, client in self.clients.items():
            try:
                # 尝试连接
                success = await client._connect_sse()
                results[name] = {
                    "success": success,
                    "endpoint": client.messages_endpoint,
                    "error": str(client.error) if client.error else None
                }
            except Exception as e:
                results[name] = {
                    "success": False,
                    "endpoint": None,
                    "error": str(e)
                }
        return results

# 创建全局实例
mcp_manager = MCPManager()
