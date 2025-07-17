from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from .mindmap_node import MindMapNode


class MindMapManager:
    """
    思维导图管理器
    管理整个思维导图的节点和关系
    """
    
    def __init__(self, mindmap_id: Optional[str] = None):
        """
        初始化思维导图管理器
        
        Args:
            mindmap_id: 思维导图ID，如果不提供则自动生成
        """
        self.mindmap_id = mindmap_id or f"mindmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.nodes: Dict[str, MindMapNode] = {}
        self.root_nodes: List[str] = []  # 根节点ID列表
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.metadata: Dict[str, Any] = {}
    
    def add_node(self, node: MindMapNode) -> bool:
        """
        添加节点到思维导图
        
        Args:
            node: 要添加的节点
            
        Returns:
            是否添加成功
        """
        if node.node_id not in self.nodes:
            self.nodes[node.node_id] = node
            
            # 如果是根节点，添加到根节点列表
            if node.is_root():
                if node.node_id not in self.root_nodes:
                    self.root_nodes.append(node.node_id)
            
            # 如果有父节点，建立父子关系
            if node.parent_id and node.parent_id in self.nodes:
                parent = self.nodes[node.parent_id]
                parent.add_child(node)
            
            self.updated_at = datetime.now()
            return True
        return False
    
    def remove_node(self, node_id: str) -> bool:
        """
        移除节点
        
        Args:
            node_id: 要移除的节点ID
            
        Returns:
            是否移除成功
        """
        if node_id not in self.nodes:
            return False
        
        node = self.nodes[node_id]
        
        # 移除父子关系
        if node.parent_id and node.parent_id in self.nodes:
            parent = self.nodes[node.parent_id]
            parent.remove_child(node_id)
        
        # 处理子节点（可以选择删除或重新分配）
        for child_id in node.children[:]:  # 复制列表避免修改迭代
            child = self.nodes.get(child_id)
            if child:
                # 将子节点提升为根节点
                child.parent_id = None
                if child_id not in self.root_nodes:
                    self.root_nodes.append(child_id)
        
        # 从根节点列表中移除
        if node_id in self.root_nodes:
            self.root_nodes.remove(node_id)
        
        # 删除节点
        del self.nodes[node_id]
        self.updated_at = datetime.now()
        return True
    
    def get_node(self, node_id: str) -> Optional[MindMapNode]:
        """
        获取节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            节点对象，如果不存在则返回None
        """
        return self.nodes.get(node_id)
    
    def get_root_nodes(self) -> List[MindMapNode]:
        """
        获取所有根节点
        
        Returns:
            根节点列表
        """
        return [self.nodes[root_id] for root_id in self.root_nodes if root_id in self.nodes]
    
    def get_all_nodes(self) -> List[MindMapNode]:
        """
        获取所有节点
        
        Returns:
            所有节点列表
        """
        return list(self.nodes.values())
    
    def find_nodes_by_type(self, node_type: str) -> List[MindMapNode]:
        """
        根据类型查找节点
        
        Args:
            node_type: 节点类型
            
        Returns:
            匹配的节点列表
        """
        return [node for node in self.nodes.values() if node.node_type == node_type]
    
    def find_nodes_by_title(self, title: str, case_sensitive: bool = False) -> List[MindMapNode]:
        """
        根据标题查找节点
        
        Args:
            title: 标题关键词
            case_sensitive: 是否区分大小写
            
        Returns:
            匹配的节点列表
        """
        if case_sensitive:
            return [node for node in self.nodes.values() if title in node.title]
        else:
            return [node for node in self.nodes.values() if title.lower() in node.title.lower()]
    
    def find_nodes_by_content(self, content: str, case_sensitive: bool = False) -> List[MindMapNode]:
        """
        根据内容查找节点
        
        Args:
            content: 内容关键词
            case_sensitive: 是否区分大小写
            
        Returns:
            匹配的节点列表
        """
        if case_sensitive:
            return [node for node in self.nodes.values() if content in node.content]
        else:
            return [node for node in self.nodes.values() if content.lower() in node.content.lower()]
    
    def get_node_path(self, node_id: str) -> List[MindMapNode]:
        """
        获取节点路径（从根节点到指定节点的路径）
        
        Args:
            node_id: 节点ID
            
        Returns:
            节点路径列表
        """
        if node_id not in self.nodes:
            return []
        
        node = self.nodes[node_id]
        return node.get_ancestors(self.nodes) + [node]
    
    def get_subtree(self, node_id: str) -> List[MindMapNode]:
        """
        获取子树（指定节点及其所有后代）
        
        Args:
            node_id: 节点ID
            
        Returns:
            子树节点列表
        """
        if node_id not in self.nodes:
            return []
        
        node = self.nodes[node_id]
        return [node] + node.get_descendants(self.nodes)
    
    def move_node(self, node_id: str, new_parent_id: Optional[str]) -> bool:
        """
        移动节点到新的父节点
        
        Args:
            node_id: 要移动的节点ID
            new_parent_id: 新的父节点ID，None表示移动到根级别
            
        Returns:
            是否移动成功
        """
        if node_id not in self.nodes:
            return False
        
        node = self.nodes[node_id]
        old_parent_id = node.parent_id
        
        # 从旧父节点移除
        if old_parent_id and old_parent_id in self.nodes:
            old_parent = self.nodes[old_parent_id]
            old_parent.remove_child(node_id)
        
        # 从根节点列表移除（如果之前是根节点）
        if node_id in self.root_nodes:
            self.root_nodes.remove(node_id)
        
        # 设置新的父节点
        if new_parent_id:
            if new_parent_id not in self.nodes:
                return False
            
            new_parent = self.nodes[new_parent_id]
            new_parent.add_child(node)
        else:
            # 移动到根级别
            node.parent_id = None
            if node_id not in self.root_nodes:
                self.root_nodes.append(node_id)
        
        self.updated_at = datetime.now()
        return True
    
    def duplicate_node(self, node_id: str, new_parent_id: Optional[str] = None) -> Optional[str]:
        """
        复制节点
        
        Args:
            node_id: 要复制的节点ID
            new_parent_id: 新节点的父节点ID
            
        Returns:
            新节点的ID，如果失败则返回None
        """
        if node_id not in self.nodes:
            return None
        
        original = self.nodes[node_id]
        
        # 创建新节点
        new_node = MindMapNode(
            title=f"{original.title} (Copy)",
            content=original.content,
            node_type=original.node_type,
            parent_id=new_parent_id,
            metadata=original.metadata.copy()
        )
        
        # 复制样式
        new_node.color = original.color
        new_node.icon = original.icon
        new_node.priority = original.priority
        
        # 添加新节点
        if self.add_node(new_node):
            return new_node.node_id
        
        return None
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        导出思维导图为字典格式
        
        Returns:
            思维导图字典表示
        """
        return {
            "mindmap_id": self.mindmap_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "root_nodes": self.root_nodes,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MindMapManager':
        """
        从字典创建思维导图管理器
        
        Args:
            data: 思维导图数据字典
            
        Returns:
            思维导图管理器对象
        """
        manager = cls(mindmap_id=data["mindmap_id"])
        
        # 恢复时间戳
        if "created_at" in data:
            manager.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            manager.updated_at = datetime.fromisoformat(data["updated_at"])
        
        # 恢复元数据
        manager.metadata = data.get("metadata", {})
        
        # 恢复根节点列表
        manager.root_nodes = data.get("root_nodes", [])
        
        # 恢复所有节点
        nodes_data = data.get("nodes", {})
        for node_id, node_data in nodes_data.items():
            node = MindMapNode.from_dict(node_data)
            manager.nodes[node_id] = node
        
        return manager
    
    def save_to_file(self, filepath: str) -> bool:
        """
        保存思维导图到文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            是否保存成功
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.export_to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存思维导图失败: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> Optional['MindMapManager']:
        """
        从文件加载思维导图
        
        Args:
            filepath: 文件路径
            
        Returns:
            思维导图管理器对象，如果失败则返回None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"加载思维导图失败: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取思维导图统计信息
        
        Returns:
            统计信息字典
        """
        total_nodes = len(self.nodes)
        root_nodes = len(self.root_nodes)
        leaf_nodes = sum(1 for node in self.nodes.values() if node.is_leaf())
        
        # 按类型统计
        type_counts = {}
        for node in self.nodes.values():
            type_counts[node.node_type] = type_counts.get(node.node_type, 0) + 1
        
        # 计算最大深度
        max_depth = 0
        for node in self.nodes.values():
            depth = node.get_depth(self.nodes)
            max_depth = max(max_depth, depth)
        
        return {
            "total_nodes": total_nodes,
            "root_nodes": root_nodes,
            "leaf_nodes": leaf_nodes,
            "max_depth": max_depth,
            "type_counts": type_counts,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        stats = self.get_statistics()
        return f"MindMapManager(id={self.mindmap_id}, nodes={stats['total_nodes']}, roots={stats['root_nodes']})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"MindMapManager(mindmap_id='{self.mindmap_id}', nodes_count={len(self.nodes)}, root_nodes_count={len(self.root_nodes)})" 