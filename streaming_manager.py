"""
VibeDoc 流式响应管理器
将100秒等待转化为引人入胜的"AI工作秀"
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, Generator, List
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class StreamMessageType(Enum):
    """流式消息类型"""
    PROGRESS = "progress"      # 进度更新
    THOUGHT = "thought"        # AI思考过程
    ACTION = "action"          # 执行行动
    CONTENT = "content"        # 内容生成
    COMPLETE = "complete"      # 步骤完成
    ERROR = "error"           # 错误信息
    FINAL = "final"           # 最终完成

class GenerationStage(Enum):
    """生成阶段枚举"""
    VALIDATION = "validation"      # 创意验证 (0-10%)
    KNOWLEDGE = "knowledge"        # 知识收集 (10-25%)  
    ANALYSIS = "analysis"          # 智能分析 (25-45%)
    GENERATION = "generation"      # 方案生成 (45-75%)
    FORMATTING = "formatting"      # 内容美化 (75-90%)
    FINALIZATION = "finalization"  # 最终输出 (90-100%)

@dataclass
class StreamMessage:
    """流式消息数据结构"""
    type: StreamMessageType
    stage: GenerationStage
    step: int                    # 步骤编号 1-6
    title: str                   # 步骤标题
    progress: float              # 进度百分比 0-100
    timestamp: str               # 时间戳
    data: Dict[str, Any]         # 具体数据
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        data_dict = asdict(self)
        data_dict['type'] = self.type.value
        data_dict['stage'] = self.stage.value
        return json.dumps(data_dict, ensure_ascii=False)
    
    @classmethod
    def create_progress(cls, stage: GenerationStage, step: int, title: str, 
                       progress: float, **kwargs) -> 'StreamMessage':
        """创建进度消息"""
        return cls(
            type=StreamMessageType.PROGRESS,
            stage=stage,
            step=step,
            title=title,
            progress=progress,
            timestamp=datetime.now().isoformat(),
            data=kwargs
        )
    
    @classmethod
    def create_thought(cls, stage: GenerationStage, thought: str, **kwargs) -> 'StreamMessage':
        """创建思考消息"""
        return cls(
            type=StreamMessageType.THOUGHT,
            stage=stage,
            step=0,  # 思考不属于特定步骤
            title="AI思考中...",
            progress=0,
            timestamp=datetime.now().isoformat(),
            data={'thought': thought, **kwargs}
        )
    
    @classmethod  
    def create_action(cls, stage: GenerationStage, action: str, **kwargs) -> 'StreamMessage':
        """创建行动消息"""
        return cls(
            type=StreamMessageType.ACTION,
            stage=stage,
            step=0,
            title="执行中...",
            progress=0,
            timestamp=datetime.now().isoformat(),
            data={'action': action, **kwargs}
        )
    
    @classmethod
    def create_content(cls, stage: GenerationStage, content: str, 
                      section: str, **kwargs) -> 'StreamMessage':
        """创建内容消息"""
        return cls(
            type=StreamMessageType.CONTENT,
            stage=stage,
            step=0,
            title=f"生成{section}内容",
            progress=0,
            timestamp=datetime.now().isoformat(),
            data={'content': content, 'section': section, **kwargs}
        )

class ProgressTracker:
    """步骤状态管理器"""
    
    # 6个关键步骤定义
    STAGES = [
        {
            'stage': GenerationStage.VALIDATION,
            'step': 1,
            'title': '🔍 创意验证',
            'description': '解析并验证用户输入的创意',
            'progress_start': 0,
            'progress_end': 10
        },
        {
            'stage': GenerationStage.KNOWLEDGE,
            'step': 2, 
            'title': '📚 知识收集',
            'description': '调用MCP服务获取外部参考资料',
            'progress_start': 10,
            'progress_end': 25
        },
        {
            'stage': GenerationStage.ANALYSIS,
            'step': 3,
            'title': '🧠 智能分析', 
            'description': 'AI深度分析创意可行性和技术方案',
            'progress_start': 25,
            'progress_end': 45
        },
        {
            'stage': GenerationStage.GENERATION,
            'step': 4,
            'title': '⚡ 方案生成',
            'description': '生成完整的开发计划和架构设计',
            'progress_start': 45,
            'progress_end': 75
        },
        {
            'stage': GenerationStage.FORMATTING,
            'step': 5,
            'title': '✨ 内容美化',
            'description': '格式化内容并生成图表',
            'progress_start': 75,
            'progress_end': 90
        },
        {
            'stage': GenerationStage.FINALIZATION,
            'step': 6,
            'title': '🎯 最终输出',
            'description': '创建文件并提取AI编程提示词',
            'progress_start': 90,
            'progress_end': 100
        }
    ]
    
    def __init__(self):
        self.current_stage_index = 0
        self.stage_start_time = time.time()
        self.total_start_time = time.time()
        
    def get_current_stage(self) -> Dict[str, Any]:
        """获取当前阶段信息"""
        if self.current_stage_index < len(self.STAGES):
            return self.STAGES[self.current_stage_index]
        return self.STAGES[-1]  # 返回最后一个阶段
    
    def get_stage_progress(self, internal_progress: float = 0) -> float:
        """计算当前阶段的全局进度"""
        current = self.get_current_stage()
        stage_range = current['progress_end'] - current['progress_start']
        return current['progress_start'] + (stage_range * internal_progress / 100)
    
    def move_to_next_stage(self) -> bool:
        """移动到下一个阶段"""
        if self.current_stage_index < len(self.STAGES) - 1:
            self.current_stage_index += 1
            self.stage_start_time = time.time()
            return True
        return False
    
    def get_estimated_remaining_time(self) -> int:
        """估算剩余时间（秒）"""
        elapsed = time.time() - self.total_start_time
        total_progress = self.get_stage_progress(0)
        
        if total_progress > 0:
            estimated_total = elapsed * 100 / total_progress
            remaining = max(0, estimated_total - elapsed)
            return int(remaining)
        
        # 默认估算：按100秒总时长计算
        return max(0, 100 - int(elapsed))
    
    def create_progress_message(self, internal_progress: float = 0, 
                               **kwargs) -> StreamMessage:
        """创建当前阶段的进度消息"""
        stage_info = self.get_current_stage()
        global_progress = self.get_stage_progress(internal_progress)
        
        return StreamMessage.create_progress(
            stage=stage_info['stage'],
            step=stage_info['step'],
            title=stage_info['title'],
            progress=global_progress,
            description=stage_info['description'],
            estimated_remaining=self.get_estimated_remaining_time(),
            stage_internal_progress=internal_progress,
            **kwargs
        )

class StreamingGenerator:
    """流式生成器 - 核心流式响应管理器"""
    
    def __init__(self):
        self.tracker = ProgressTracker()
        self.messages: List[StreamMessage] = []
        
    def emit(self, message: StreamMessage) -> StreamMessage:
        """发送流式消息"""
        self.messages.append(message)
        logger.info(f"🔥 Stream: {message.type.value} - {message.title}")
        return message
    
    def emit_progress(self, internal_progress: float = 0, **kwargs) -> StreamMessage:
        """发送进度消息"""
        message = self.tracker.create_progress_message(internal_progress, **kwargs)
        return self.emit(message)
    
    def emit_thought(self, thought: str, **kwargs) -> StreamMessage:
        """发送思考消息"""
        stage_info = self.tracker.get_current_stage()
        message = StreamMessage.create_thought(stage_info['stage'], thought, **kwargs)
        return self.emit(message)
    
    def emit_action(self, action: str, **kwargs) -> StreamMessage:
        """发送行动消息"""
        stage_info = self.tracker.get_current_stage()
        message = StreamMessage.create_action(stage_info['stage'], action, **kwargs)
        return self.emit(message)
    
    def emit_content(self, content: str, section: str, **kwargs) -> StreamMessage:
        """发送内容消息"""
        stage_info = self.tracker.get_current_stage()
        message = StreamMessage.create_content(stage_info['stage'], content, section, **kwargs)
        return self.emit(message)
    
    def next_stage(self, **kwargs) -> StreamMessage:
        """移动到下一阶段"""
        moved = self.tracker.move_to_next_stage()
        if moved:
            return self.emit_progress(0, stage_changed=True, **kwargs)
        else:
            # 最终完成
            return self.emit(StreamMessage(
                type=StreamMessageType.FINAL,
                stage=GenerationStage.FINALIZATION,
                step=6,
                title="🎉 生成完成",
                progress=100,
                timestamp=datetime.now().isoformat(),
                data={'completed': True, **kwargs}
            ))
    
    def get_all_messages(self) -> List[Dict[str, Any]]:
        """获取所有消息（用于调试）"""
        return [json.loads(msg.to_json()) for msg in self.messages]

# 示例用法和测试函数
def demo_streaming_flow():
    """演示流式响应流程"""
    generator = StreamingGenerator()
    
    # 第1阶段：创意验证
    generator.emit_thought("开始分析用户的产品创意...")
    generator.emit_progress(20, detail="正在解析创意描述")
    generator.emit_action("验证创意完整性和可行性")
    generator.emit_progress(80, detail="创意验证通过")
    generator.next_stage()
    
    # 第2阶段：知识收集
    generator.emit_thought("需要收集外部参考资料来丰富方案")
    generator.emit_action("调用MCP服务获取GitHub参考")
    generator.emit_progress(60, detail="成功获取参考资料")
    generator.next_stage()
    
    # 演示完整流程...
    return generator.get_all_messages()

if __name__ == "__main__":
    # 测试流式数据格式
    demo_messages = demo_streaming_flow()
    for msg in demo_messages[:5]:  # 显示前5条消息
        print(json.dumps(msg, indent=2, ensure_ascii=False))