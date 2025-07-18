#!/usr/bin/env python3
"""
测试放射状布局和连接线
"""

from nodes.mindmap_node import MindMapNode
from nodes.mindmap_manager import MindMapManager
import math

def test_radial_layout():
    """测试放射状布局和连接线"""
    print("=== 测试放射状布局和连接线 ===")
    print()
    
    # 创建思维导图管理器
    manager = MindMapManager("test_radial")
    
    # 创建主节点
    main_node = MindMapNode(
        title="Rocket Building Project",
        content="A comprehensive rocket building project with multiple phases",
        node_type="idea"
    )
    manager.add_node(main_node)
    
    # 创建子节点
    child_nodes_data = [
        ("Design Phase", "Plan the rocket design and specifications"),
        ("Materials", "Select and source required materials"),
        ("Assembly", "Build and assemble the rocket components"),
        ("Testing", "Test the rocket systems and safety"),
        ("Launch", "Prepare and execute the rocket launch")
    ]
    
    child_nodes = []
    suggested_focus_node = None
    suggested_node_name = "Design Phase"
    
    for title, description in child_nodes_data:
        child_node = MindMapNode(
            title=title,
            content=description,
            node_type="subtask",
            parent_id=main_node.node_id
        )
        manager.add_node(child_node)
        child_nodes.append(child_node)
        
        # 检查是否为建议讨论的节点
        if title == suggested_node_name:
            suggested_focus_node = child_node
    
    # 设置焦点节点
    if suggested_focus_node:
        manager.set_focus_node(suggested_focus_node.node_id)
    
    print("1. 节点创建完成:")
    print(f"   主节点: {main_node.title}")
    print(f"   子节点数量: {len(child_nodes)}")
    print(f"   建议讨论节点: {suggested_node_name}")
    print()
    
    # 模拟放射状布局计算
    print("2. 放射状布局计算:")
    total_children = len(child_nodes)
    angle_step = 360 / total_children
    radius = 250
    
    print(f"   总子节点数: {total_children}")
    print(f"   角度步长: {angle_step}°")
    print(f"   放射半径: {radius}px")
    print()
    
    for i, child in enumerate(child_nodes):
        # 计算角度（从顶部开始，顺时针）
        angle = (i * angle_step - 90) * (math.pi / 180)
        
        # 计算位置
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        
        focus_status = "🎯 焦点" if child == suggested_focus_node else "普通"
        print(f"   子节点 {i+1}: {child.title} - {focus_status}")
        print(f"     角度: {angle * 180 / math.pi:.1f}°")
        print(f"     位置: x={x:.1f}, y={y:.1f}")
        print()
    
    # 模拟前端显示数据
    print("3. 前端显示数据:")
    node_data = {
        "node_id": main_node.node_id,
        "title": main_node.title,
        "content": main_node.content,
        "node_type": main_node.node_type,
        "position": main_node.position,
        "is_focused": False,
        "parent_node": None,
        "suggested_next": suggested_node_name,
        "total_children": len(child_nodes),
        "focus_node_id": suggested_focus_node.node_id if suggested_focus_node else None,
        "focus_node_title": suggested_focus_node.title if suggested_focus_node else None,
        "children": [
            {
                "node_id": child.node_id,
                "title": child.title,
                "content": child.content,
                "node_type": child.node_type,
                "is_focused": child.node_id == (suggested_focus_node.node_id if suggested_focus_node else None)
            }
            for child in child_nodes
        ]
    }
    
    print(f"   主节点标题: {node_data['title']}")
    print(f"   主节点焦点状态: {node_data['is_focused']}")
    print(f"   子节点数量: {node_data['total_children']}")
    print()
    
    print("4. 预期显示效果:")
    print("   📱 页面中心显示主节点")
    print("   🔗 子节点以放射状排列在主节点周围")
    print("   📐 子节点均匀分布在360度圆周上")
    print("   🎯 子节点'Design Phase'有焦点样式")
    print("   ➖ 主节点到每个子节点都有明显的连接线")
    print("   📏 连接线从主节点中心到子节点中心")
    
    print("\n5. 布局特点:")
    print("   • 真正的思维导图放射状布局")
    print("   • 连接线清晰可见（3px宽度，带阴影）")
    print("   • 子节点悬停效果")
    print("   • 焦点节点突出显示")
    print("   • 响应式设计，支持不同数量的子节点")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_radial_layout() 