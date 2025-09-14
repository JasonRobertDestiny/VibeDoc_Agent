#!/usr/bin/env python3
"""
增强版MCP直接客户端 - 支持魔塔平台异步MCP服务
处理HTTP 202异步响应，通过SSE获取结果
"""

import requests
import json
import time
import threading
import queue
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

@dataclass
class AsyncMCPResult:
    """异步MCP调用结果"""
    success: bool
    data: str
    service_name: str
    execution_time: float
    session_id: Optional[str] = None
    error_message: Optional[str] = None

class AsyncMCPClient:
    """异步MCP客户端 - 专为魔塔平台优化"""
    
    def __init__(self):
        self.timeout = 60
        self.result_timeout = 30  # 等待异步结果的超时时间
        
        # 魔塔MCP服务配置
        self.mcp_services = {
            "fetch": {
                "url": "https://mcp.api-inference.modelscope.net/6ec508e067dc41/sse",
                "name": "Fetch MCP",
                "enabled": True,
                "tools": {
                    "fetch": {
                        "url": "string",
                        "max_length": "integer", 
                        "start_index": "integer",
                        "raw": "boolean"
                    }
                }
            },
            "deepwiki": {
                "url": "https://mcp.api-inference.modelscope.net/d4ed08072d2846/sse",
                "name": "DeepWiki MCP", 
                "enabled": True,
                "tools": {
                    "deepwiki_fetch": {
                        "url": "string",
                        "mode": "string",
                        "maxDepth": "integer"
                    }
                }
            }
        }
    
    def _get_sse_endpoint(self, service_url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """获取SSE endpoint和session_id"""
        try:
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            }
            
            logger.info(f"🔗 连接SSE: {service_url}")
            response = requests.get(service_url, headers=headers, timeout=15, stream=True)
            
            if response.status_code != 200:
                logger.error(f"❌ SSE连接失败: HTTP {response.status_code}")
                return False, None, None
            
            # 解析SSE事件
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    data = line[6:]  # 去掉 'data: ' 前缀
                    if '/messages/' in data and 'session_id=' in data:
                        session_id = data.split('session_id=')[1]
                        logger.info(f"✅ 获取session_id: {session_id}")
                        response.close()
                        return True, data, session_id
                elif line == "":
                    break
            
            response.close()
            logger.error("❌ 未获取到有效的endpoint")
            return False, None, None
            
        except Exception as e:
            logger.error(f"💥 SSE连接异常: {str(e)}")
            return False, None, None
    
    def _listen_for_result(self, service_url: str, session_id: str, result_queue: queue.Queue):
        """监听SSE流获取异步结果"""
        try:
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            }
            
            logger.info(f"👂 开始监听结果...")
            response = requests.get(service_url, headers=headers, timeout=self.result_timeout, stream=True)
            
            if response.status_code != 200:
                result_queue.put(("error", f"监听连接失败: HTTP {response.status_code}"))
                return
            
            # 监听SSE事件
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    data_str = line[6:]
                    try:
                        # 尝试解析JSON数据
                        data = json.loads(data_str)
                        if isinstance(data, dict):
                            # 检查是否是MCP响应
                            if "result" in data or "error" in data:
                                logger.info("✅ 收到MCP响应")
                                result_queue.put(("success", data))
                                break
                            elif "id" in data:  # 可能是MCP响应
                                result_queue.put(("success", data))
                                break
                    except json.JSONDecodeError:
                        # 非JSON数据，可能是纯文本结果
                        if len(data_str.strip()) > 10:
                            logger.info("✅ 收到文本响应")
                            result_queue.put(("success", {"result": {"text": data_str}}))
                            break
                elif line.startswith('event: '):
                    event_type = line[7:]
                    logger.debug(f"📨 SSE事件: {event_type}")
            
            response.close()
            
        except requests.exceptions.Timeout:
            logger.warning("⏰ 结果监听超时")
            result_queue.put(("timeout", "等待结果超时"))
        except Exception as e:
            logger.error(f"💥 监听异常: {str(e)}")
            result_queue.put(("error", f"监听异常: {str(e)}"))
    
    def call_mcp_service_async(
        self,
        service_key: str,
        tool_name: str,
        tool_args: Dict[str, Any]
    ) -> AsyncMCPResult:
        """异步调用MCP服务"""
        
        if service_key not in self.mcp_services:
            return AsyncMCPResult(
                success=False,
                data="",
                service_name=service_key,
                execution_time=0.0,
                error_message=f"未知服务: {service_key}"
            )
        
        service_config = self.mcp_services[service_key]
        service_url = service_config["url"]
        service_name = service_config["name"]
        
        start_time = time.time()
        
        logger.info(f"🚀 开始调用 {service_name}")
        logger.info(f"📊 工具: {tool_name}")
        logger.info(f"📋 参数: {json.dumps(tool_args, ensure_ascii=False)}")
        
        # 步骤1: 获取SSE endpoint
        success, endpoint_path, session_id = self._get_sse_endpoint(service_url)
        if not success:
            return AsyncMCPResult(
                success=False,
                data="",
                service_name=service_name,
                execution_time=time.time() - start_time,
                error_message="获取endpoint失败"
            )
        
        # 步骤2: 启动结果监听器
        result_queue = queue.Queue()
        listener_thread = threading.Thread(
            target=self._listen_for_result,
            args=(service_url, session_id, result_queue)
        )
        listener_thread.daemon = True
        listener_thread.start()
        
        # 等待一小段时间确保监听器就绪
        time.sleep(0.5)
        
        # 步骤3: 发送MCP请求
        try:
            base_url = service_url.replace('/sse', '')
            full_endpoint = urljoin(base_url, endpoint_path)
            
            mcp_request = {
                "jsonrpc": "2.0",
                "id": int(time.time() * 1000),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": tool_args
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            logger.info(f"📤 发送请求到: {full_endpoint}")
            response = requests.post(full_endpoint, json=mcp_request, headers=headers, timeout=10)
            
            logger.info(f"📊 请求响应: HTTP {response.status_code}")
            
            if response.status_code == 202:  # Accepted - 异步处理
                logger.info("✅ 请求已接受，等待异步结果...")
                
                # 步骤4: 等待异步结果
                try:
                    result_type, result_data = result_queue.get(timeout=self.result_timeout)
                    
                    execution_time = time.time() - start_time
                    
                    if result_type == "success":
                        # 解析结果数据
                        content = self._extract_content_from_response(result_data)
                        if content and len(content.strip()) > 10:
                            logger.info(f"✅ {service_name} 异步调用成功!")
                            return AsyncMCPResult(
                                success=True,
                                data=content,
                                service_name=service_name,
                                execution_time=execution_time,
                                session_id=session_id
                            )
                        else:
                            return AsyncMCPResult(
                                success=False,
                                data="",
                                service_name=service_name,
                                execution_time=execution_time,
                                session_id=session_id,
                                error_message="响应内容为空"
                            )
                    else:
                        return AsyncMCPResult(
                            success=False,
                            data="",
                            service_name=service_name,
                            execution_time=execution_time,
                            session_id=session_id,
                            error_message=str(result_data)
                        )
                        
                except queue.Empty:
                    return AsyncMCPResult(
                        success=False,
                        data="",
                        service_name=service_name,
                        execution_time=time.time() - start_time,
                        session_id=session_id,
                        error_message="等待异步结果超时"
                    )
            
            elif response.status_code == 200:
                # 同步响应
                try:
                    data = response.json()
                    content = self._extract_content_from_response(data)
                    execution_time = time.time() - start_time
                    
                    return AsyncMCPResult(
                        success=bool(content and len(content.strip()) > 10),
                        data=content or "",
                        service_name=service_name,
                        execution_time=execution_time,
                        session_id=session_id,
                        error_message=None if content else "响应内容为空"
                    )
                except json.JSONDecodeError:
                    content = response.text
                    return AsyncMCPResult(
                        success=len(content.strip()) > 10,
                        data=content,
                        service_name=service_name,
                        execution_time=time.time() - start_time,
                        session_id=session_id
                    )
            else:
                return AsyncMCPResult(
                    success=False,
                    data="",
                    service_name=service_name,
                    execution_time=time.time() - start_time,
                    session_id=session_id,
                    error_message=f"HTTP {response.status_code}: {response.text[:200]}"
                )
                
        except Exception as e:
            return AsyncMCPResult(
                success=False,
                data="",
                service_name=service_name,
                execution_time=time.time() - start_time,
                session_id=session_id,
                error_message=f"请求异常: {str(e)}"
            )
    
    def _extract_content_from_response(self, response_data: Any) -> Optional[str]:
        """从响应中提取内容"""
        try:
            if isinstance(response_data, str):
                return response_data
            
            if isinstance(response_data, dict):
                # 检查标准MCP响应格式
                if "result" in response_data:
                    result = response_data["result"]
                    
                    # 检查content数组
                    if "content" in result and isinstance(result["content"], list):
                        contents = []
                        for item in result["content"]:
                            if isinstance(item, dict) and "text" in item:
                                contents.append(item["text"])
                            elif isinstance(item, str):
                                contents.append(item)
                        if contents:
                            return "\n".join(contents)
                    
                    # 检查其他字段
                    for field in ["text", "data", "message"]:
                        if field in result and result[field]:
                            return str(result[field])
                    
                    # 如果result本身是字符串
                    if isinstance(result, str):
                        return result
                
                # 检查错误
                if "error" in response_data:
                    error = response_data["error"]
                    if isinstance(error, dict) and "message" in error:
                        return f"错误: {error['message']}"
                    else:
                        return f"错误: {str(error)}"
                
                # 检查直接的字段
                for field in ["content", "data", "text", "message", "response"]:
                    if field in response_data and response_data[field]:
                        content = response_data[field]
                        if isinstance(content, list):
                            return "\n".join(str(item) for item in content if item)
                        else:
                            return str(content)
            
            # 如果都没有匹配，返回JSON字符串
            return json.dumps(response_data, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.warning(f"⚠️ 内容提取失败: {e}")
            return str(response_data) if response_data else None

# 全局实例
async_mcp_client = AsyncMCPClient()

# 便捷函数
def call_fetch_mcp_async(url: str, max_length: int = 5000) -> AsyncMCPResult:
    """异步调用Fetch MCP服务"""
    return async_mcp_client.call_mcp_service_async(
        "fetch",
        "fetch",
        {"url": url, "max_length": max_length}
    )

def call_deepwiki_mcp_async(url: str, mode: str = "aggregate") -> AsyncMCPResult:
    """异步调用DeepWiki MCP服务"""
    return async_mcp_client.call_mcp_service_async(
        "deepwiki",
        "deepwiki_fetch", 
        {"url": url, "mode": mode}
    )

if __name__ == "__main__":
    # 测试异步MCP客户端
    print("🧪 测试异步MCP客户端")
    print("=" * 50)
    
    # 测试Fetch MCP
    print("测试Fetch MCP...")
    result = call_fetch_mcp_async("https://example.com")
    print(f"成功: {result.success}")
    print(f"内容长度: {len(result.data) if result.data else 0}")
    print(f"执行时间: {result.execution_time:.2f}s")
    if result.error_message:
        print(f"错误: {result.error_message}")
    
    print("\n" + "-" * 30)
    
    # 测试DeepWiki MCP
    print("测试DeepWiki MCP...")
    result = call_deepwiki_mcp_async("https://deepwiki.org/openai/openai-python")
    print(f"成功: {result.success}")
    print(f"内容长度: {len(result.data) if result.data else 0}")
    print(f"执行时间: {result.execution_time:.2f}s")
    if result.error_message:
        print(f"错误: {result.error_message}")
    
    print("\n✅ 异步MCP客户端测试完成")