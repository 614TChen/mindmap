from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class MindMapNode:
    """
    思维导图节点类
    包含节点信息、子节点和父节点的管理
    """
    
    def __init__(
        self,
        title: str,
        content: str = "",
        node_type: str = "idea",
        parent_id: Optional[str] = None,
        node_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        初始化思维导图节点
        
        Args:
            title: 节点标题
            content: 节点内容描述
            node_type: 节点类型 (idea, task, note, etc.)
            parent_id: 父节点ID
            node_id: 节点唯一ID，如果不提供则自动生成
            metadata: 额外的元数据
        """
        self.node_id = node_id or str(uuid.uuid4())
        self.title = title
        self.content = content
        self.node_type = node_type
        self.parent_id = parent_id
        self.metadata = metadata or {}
        
        # 时间戳
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # 节点关系
        self.children: List[str] = []  # 子节点ID列表
        self.siblings: List[str] = []  # 兄弟节点ID列表
        
        # 节点状态
        self.is_expanded: bool = True
        self.is_visible: bool = True
        self.priority: int = 0  # 优先级，数字越大优先级越高
        self.is_focused: bool = False  # 是否为当前讨论的焦点节点
        
        # 样式信息
        self.color: Optional[str] = None
        self.icon: Optional[str] = None
        self.position: Dict[str, float] = {"x": 0, "y": 0}
    
    def add_child(self, child_node: 'MindMapNode') -> bool:
        """
        添加子节点
        
        Args:
            child_node: 要添加的子节点
            
        Returns:
            是否添加成功
        """
        if child_node.node_id not in self.children:
            self.children.append(child_node.node_id)
            child_node.parent_id = self.node_id
            child_node.updated_at = datetime.now()
            self.updated_at = datetime.now()
            return True
        return False
    
    def remove_child(self, child_id: str) -> bool:
        """
        移除子节点
        
        Args:
            child_id: 要移除的子节点ID
            
        Returns:
            是否移除成功
        """
        if child_id in self.children:
            self.children.remove(child_id)
            self.updated_at = datetime.now()
            return True
        return False
    
    def add_sibling(self, sibling_node: 'MindMapNode') -> bool:
        """
        添加兄弟节点
        
        Args:
            sibling_node: 要添加的兄弟节点
            
        Returns:
            是否添加成功
        """
        if sibling_node.node_id not in self.siblings:
            self.siblings.append(sibling_node.node_id)
            sibling_node.siblings.append(self.node_id)
            sibling_node.parent_id = self.parent_id
            sibling_node.updated_at = datetime.now()
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_children(self, node_map: Dict[str, 'MindMapNode']) -> List['MindMapNode']:
        """
        获取所有子节点对象
        
        Args:
            node_map: 节点ID到节点对象的映射
            
        Returns:
            子节点对象列表
        """
        return [node_map[child_id] for child_id in self.children if child_id in node_map]
    
    def get_siblings(self, node_map: Dict[str, 'MindMapNode']) -> List['MindMapNode']:
        """
        获取所有兄弟节点对象
        
        Args:
            node_map: 节点ID到节点对象的映射
            
        Returns:
            兄弟节点对象列表
        """
        return [node_map[sibling_id] for sibling_id in self.siblings if sibling_id in node_map]
    
    def get_parent(self, node_map: Dict[str, 'MindMapNode']) -> Optional['MindMapNode']:
        """
        获取父节点对象
        
        Args:
            node_map: 节点ID到节点对象的映射
            
        Returns:
            父节点对象，如果没有则返回None
        """
        return node_map.get(self.parent_id)
    
    def get_ancestors(self, node_map: Dict[str, 'MindMapNode']) -> List['MindMapNode']:
        """
        获取所有祖先节点
        
        Args:
            node_map: 节点ID到节点对象的映射
            
        Returns:
            祖先节点列表（从根节点到当前节点的路径）
        """
        ancestors = []
        current = self.get_parent(node_map)
        while current:
            ancestors.append(current)
            current = current.get_parent(node_map)
        return list(reversed(ancestors))  # 返回从根到叶的顺序
    
    def get_descendants(self, node_map: Dict[str, 'MindMapNode']) -> List['MindMapNode']:
        """
        获取所有后代节点
        
        Args:
            node_map: 节点ID到节点对象的映射
            
        Returns:
            后代节点列表
        """
        descendants = []
        for child_id in self.children:
            if child_id in node_map:
                child = node_map[child_id]
                descendants.append(child)
                descendants.extend(child.get_descendants(node_map))
        return descendants
    
    def get_depth(self, node_map: Dict[str, 'MindMapNode']) -> int:
        """
        获取节点深度（根节点深度为0）
        
        Args:
            node_map: 节点ID到节点对象的映射
            
        Returns:
            节点深度
        """
        depth = 0
        current = self.get_parent(node_map)
        while current:
            depth += 1
            current = current.get_parent(node_map)
        return depth
    
    def get_level(self, node_map: Dict[str, 'MindMapNode']) -> int:
        """
        获取节点层级（从0开始）
        
        Args:
            node_map: 节点ID到节点对象的映射
            
        Returns:
            节点层级
        """
        return self.get_depth(node_map)
    
    def is_root(self) -> bool:
        """
        判断是否为根节点
        
        Returns:
            是否为根节点
        """
        return self.parent_id is None
    
    def is_leaf(self) -> bool:
        """
        判断是否为叶子节点
        
        Returns:
            是否为叶子节点
        """
        return len(self.children) == 0
    
    def update_content(self, new_content: str) -> None:
        """
        更新节点内容
        
        Args:
            new_content: 新的内容
        """
        self.content = new_content
        self.updated_at = datetime.now()
    
    def update_title(self, new_title: str) -> None:
        """
        更新节点标题
        
        Args:
            new_title: 新的标题
        """
        self.title = new_title
        self.updated_at = datetime.now()
    
    def set_position(self, x: float, y: float) -> None:
        """
        设置节点位置
        
        Args:
            x: X坐标
            y: Y坐标
        """
        self.position = {"x": x, "y": y}
        self.updated_at = datetime.now()
    
    def set_style(self, color: Optional[str] = None, icon: Optional[str] = None) -> None:
        """
        设置节点样式
        
        Args:
            color: 节点颜色
            icon: 节点图标
        """
        if color is not None:
            self.color = color
        if icon is not None:
            self.icon = icon
        self.updated_at = datetime.now()
    
    def set_focus(self, focused: bool = True) -> None:
        """
        设置节点焦点状态
        
        Args:
            focused: 是否为焦点节点
        """
        self.is_focused = focused
        self.updated_at = datetime.now()
    
    def is_focus_node(self) -> bool:
        """
        判断是否为焦点节点
        
        Returns:
            是否为焦点节点
        """
        return self.is_focused
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将节点转换为字典格式
        
        Returns:
            节点字典表示
        """
        return {
            "node_id": self.node_id,
            "title": self.title,
            "content": self.content,
            "node_type": self.node_type,
            "parent_id": self.parent_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "children": self.children,
            "siblings": self.siblings,
            "is_expanded": self.is_expanded,
            "is_visible": self.is_visible,
            "priority": self.priority,
            "is_focused": self.is_focused,
            "color": self.color,
            "icon": self.icon,
            "position": self.position
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MindMapNode':
        """
        从字典创建节点
        
        Args:
            data: 节点数据字典
            
        Returns:
            节点对象
        """
        node = cls(
            title=data["title"],
            content=data.get("content", ""),
            node_type=data.get("node_type", "idea"),
            parent_id=data.get("parent_id"),
            node_id=data["node_id"],
            metadata=data.get("metadata", {})
        )
        
        # 恢复时间戳
        if "created_at" in data:
            node.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            node.updated_at = datetime.fromisoformat(data["updated_at"])
        
        # 恢复关系
        node.children = data.get("children", [])
        node.siblings = data.get("siblings", [])
        
        # 恢复状态
        node.is_expanded = data.get("is_expanded", True)
        node.is_visible = data.get("is_visible", True)
        node.priority = data.get("priority", 0)
        node.is_focused = data.get("is_focused", False)
        
        # 恢复样式
        node.color = data.get("color")
        node.icon = data.get("icon")
        node.position = data.get("position", {"x": 0, "y": 0})
        
        return node
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"MindMapNode(id={self.node_id}, title='{self.title}', type={self.node_type})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"MindMapNode(node_id='{self.node_id}', title='{self.title}', content='{self.content[:50]}...', parent_id='{self.parent_id}', children_count={len(self.children)})" 