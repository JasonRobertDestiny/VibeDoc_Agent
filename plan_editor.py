"""
用户方案编辑器
允许用户对AI生成的开发计划进行分段编辑和修改
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class EditableSection:
    """可编辑的方案段落"""
    section_id: str
    title: str
    content: str
    section_type: str  # 'heading', 'paragraph', 'list', 'code', 'table'
    level: int  # 1-6 for headings, 0 for others
    start_line: int
    end_line: int
    is_editable: bool = True

class PlanEditor:
    """开发计划编辑器"""
    
    def __init__(self):
        self.sections: List[EditableSection] = []
        self.original_content = ""
        self.modified_content = ""
        self.edit_history: List[Dict] = []
    
    def parse_plan_content(self, content: str) -> List[EditableSection]:
        """解析开发计划内容为可编辑段落"""
        self.original_content = content
        self.sections = []
        
        lines = content.split('\n')
        current_section = None
        section_counter = 0
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 检测标题（# ## ### 等）
            if line.startswith('#') and not line.startswith('```'):
                level = len(line) - len(line.lstrip('#'))
                if level <= 6:  # 有效的标题级别
                    title = line.lstrip('#').strip()
                    
                    # 保存上一个段落
                    if current_section and current_section.content.strip():
                        self.sections.append(current_section)
                    
                    # 创建新的标题段落
                    section_counter += 1
                    current_section = EditableSection(
                        section_id=f"section_{section_counter}",
                        title=title,
                        content=line,
                        section_type='heading',
                        level=level,
                        start_line=i,
                        end_line=i,
                        is_editable=self._is_section_editable(title)
                    )
                    i += 1
                    continue
            
            # 检测代码块
            if line.startswith('```'):
                if current_section and current_section.content.strip():
                    self.sections.append(current_section)
                
                # 收集整个代码块
                code_content = [line]
                i += 1
                start_line = i - 1
                
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_content.append(lines[i])
                    i += 1
                
                if i < len(lines):  # 添加结束的```
                    code_content.append(lines[i])
                    i += 1
                
                section_counter += 1
                code_section = EditableSection(
                    section_id=f"code_{section_counter}",
                    title="代码块",
                    content='\n'.join(code_content),
                    section_type='code',
                    level=0,
                    start_line=start_line,
                    end_line=i - 1,
                    is_editable=True
                )
                self.sections.append(code_section)
                current_section = None
                continue
            
            # 检测表格
            if '|' in line and line.count('|') >= 2:
                if current_section and current_section.content.strip():
                    self.sections.append(current_section)
                
                # 收集整个表格
                table_content = [line]
                start_line = i
                i += 1
                
                while i < len(lines) and '|' in lines[i] and lines[i].count('|') >= 2:
                    table_content.append(lines[i])
                    i += 1
                
                section_counter += 1
                table_section = EditableSection(
                    section_id=f"table_{section_counter}",
                    title="表格",
                    content='\n'.join(table_content),
                    section_type='table',
                    level=0,
                    start_line=start_line,
                    end_line=i - 1,
                    is_editable=True
                )
                self.sections.append(table_section)
                current_section = None
                continue
            
            # 检测列表
            if line.startswith(('-', '*', '+')) or re.match(r'^\d+\.', line):
                if current_section and current_section.section_type != 'list':
                    if current_section.content.strip():
                        self.sections.append(current_section)
                    
                    section_counter += 1
                    current_section = EditableSection(
                        section_id=f"list_{section_counter}",
                        title="列表",
                        content=line,
                        section_type='list',
                        level=0,
                        start_line=i,
                        end_line=i,
                        is_editable=True
                    )
                elif current_section and current_section.section_type == 'list':
                    current_section.content += '\n' + line
                    current_section.end_line = i
                else:
                    section_counter += 1
                    current_section = EditableSection(
                        section_id=f"list_{section_counter}",
                        title="列表",
                        content=line,
                        section_type='list',
                        level=0,
                        start_line=i,
                        end_line=i,
                        is_editable=True
                    )
                i += 1
                continue
            
            # 普通段落
            if line:
                if current_section and current_section.section_type == 'paragraph':
                    current_section.content += '\n' + line
                    current_section.end_line = i
                elif current_section and current_section.section_type == 'heading':
                    # 标题后的第一个段落
                    section_counter += 1
                    new_section = EditableSection(
                        section_id=f"paragraph_{section_counter}",
                        title="段落",
                        content=line,
                        section_type='paragraph',
                        level=0,
                        start_line=i,
                        end_line=i,
                        is_editable=True
                    )
                    self.sections.append(current_section)
                    current_section = new_section
                else:
                    if current_section and current_section.content.strip():
                        self.sections.append(current_section)
                    
                    section_counter += 1
                    current_section = EditableSection(
                        section_id=f"paragraph_{section_counter}",
                        title="段落",
                        content=line,
                        section_type='paragraph',
                        level=0,
                        start_line=i,
                        end_line=i,
                        is_editable=True
                    )
            
            i += 1
        
        # 保存最后一个段落
        if current_section and current_section.content.strip():
            self.sections.append(current_section)
        
        logger.info(f"解析完成，共找到 {len(self.sections)} 个可编辑段落")
        return self.sections
    
    def _is_section_editable(self, title: str) -> bool:
        """判断段落是否可编辑"""
        non_editable_patterns = [
            r'生成时间',
            r'AI模型',
            r'基于用户创意',
            r'Agent应用',
            r'meta-info'
        ]
        
        title_lower = title.lower()
        return not any(re.search(pattern, title_lower) for pattern in non_editable_patterns)
    
    def get_editable_sections(self) -> List[Dict]:
        """获取可编辑段落列表（用于前端显示）"""
        editable_sections = []
        
        for section in self.sections:
            if section.is_editable:
                editable_sections.append({
                    'id': section.section_id,
                    'title': section.title,
                    'content': section.content,
                    'type': section.section_type,
                    'level': section.level,
                    'preview': self._get_section_preview(section.content)
                })
        
        return editable_sections
    
    def _get_section_preview(self, content: str, max_length: int = 100) -> str:
        """获取段落预览"""
        # 移除Markdown格式符号
        preview = re.sub(r'[#*`|]', '', content)
        preview = re.sub(r'\n+', ' ', preview).strip()
        
        if len(preview) > max_length:
            preview = preview[:max_length] + '...'
        
        return preview
    
    def update_section(self, section_id: str, new_content: str, user_comment: str = "") -> bool:
        """更新指定段落的内容"""
        try:
            # 查找目标段落
            target_section = None
            for section in self.sections:
                if section.section_id == section_id:
                    target_section = section
                    break
            
            if not target_section:
                logger.error(f"未找到段落 {section_id}")
                return False
            
            if not target_section.is_editable:
                logger.error(f"段落 {section_id} 不可编辑")
                return False
            
            # 记录编辑历史
            self.edit_history.append({
                'timestamp': datetime.now().isoformat(),
                'section_id': section_id,
                'old_content': target_section.content,
                'new_content': new_content,
                'user_comment': user_comment
            })
            
            # 更新内容
            target_section.content = new_content
            
            # 重新构建完整内容
            self._rebuild_content()
            
            logger.info(f"成功更新段落 {section_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新段落失败: {str(e)}")
            return False
    
    def _rebuild_content(self):
        """重新构建完整内容"""
        try:
            lines = self.original_content.split('\n')
            
            # 按行号排序段落
            sorted_sections = sorted(self.sections, key=lambda x: x.start_line)
            
            # 重新构建内容
            new_lines = []
            current_line = 0
            
            for section in sorted_sections:
                # 添加段落前的空行
                while current_line < section.start_line:
                    new_lines.append(lines[current_line])
                    current_line += 1
                
                # 添加更新后的段落内容
                new_lines.extend(section.content.split('\n'))
                
                # 跳过原始段落行
                current_line = section.end_line + 1
            
            # 添加剩余的行
            while current_line < len(lines):
                new_lines.append(lines[current_line])
                current_line += 1
            
            self.modified_content = '\n'.join(new_lines)
            
        except Exception as e:
            logger.error(f"重建内容失败: {str(e)}")
            self.modified_content = self.original_content
    
    def get_modified_content(self) -> str:
        """获取修改后的完整内容"""
        return self.modified_content if self.modified_content else self.original_content
    
    def get_edit_history(self) -> List[Dict]:
        """获取编辑历史"""
        return self.edit_history
    
    def get_edit_summary(self) -> Dict:
        """获取编辑摘要"""
        return {
            'total_sections': len(self.sections),
            'editable_sections': len([s for s in self.sections if s.is_editable]),
            'edited_sections': len(self.edit_history),
            'last_edit_time': self.edit_history[-1]['timestamp'] if self.edit_history else None
        }
    
    def reset_to_original(self):
        """重置到原始内容"""
        self.modified_content = self.original_content
        self.edit_history = []
        # 重新解析段落
        self.parse_plan_content(self.original_content)
        logger.info("已重置到原始内容")
    
    def export_edited_content(self, format_type: str = 'markdown') -> str:
        """导出编辑后的内容"""
        content = self.get_modified_content()
        
        if format_type == 'markdown':
            return content
        elif format_type == 'html':
            # 简单的Markdown到HTML转换
            import markdown
            return markdown.markdown(content)
        else:
            return content

# 全局编辑器实例
plan_editor = PlanEditor()