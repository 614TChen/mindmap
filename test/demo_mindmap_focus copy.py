#!/usr/bin/env python3
"""
思维导图焦点节点功能演示
"""

from nodes.mindmap_node import MindMapNode
from nodes.mindmap_manager import MindMapManager

def demo_mindmap_focus():
    """演示思维导图焦点节点功能"""
    print("🚀 思维导图焦点节点功能演示")
    print("=" * 50)
    
    # 创建思维导图管理器
    manager = MindMapManager("demo_project")
    
    # 模拟starter agent创建主节点和子节点
    print("\n1️⃣ 创建主节点和子节点")
    print("-" * 30)
    
    # 主节点
    main_node = MindMapNode(
        title="Rocket Building Project",
        content="A comprehensive rocket building project with multiple phases",
        node_type="idea"
    )
    manager.add_node(main_node)
    print(f"✅ 主节点: {main_node.title}")
    
    # 子节点列表
    child_nodes_data = [
        ("Design Phase", "Plan the rocket design and specifications"),
        ("Materials", "Select and source required materials"),
        ("Assembly", "Build and assemble the rocket components"),
        ("Testing", "Test the rocket systems and safety"),
        ("Launch", "Prepare and execute the rocket launch")
    ]
    
    child_nodes = []
    for title, description in child_nodes_data:
        child_node = MindMapNode(
            title=title,
            content=description,
            node_type="subtask",
            parent_id=main_node.node_id
        )
        manager.add_node(child_node)
        child_nodes.append(child_node)
        print(f"   📋 子节点: {child_node.title}")
    
    # 设置建议讨论的节点为焦点
    suggested_node_name = "Design Phase"
    suggested_focus_node = None
    
    for child_node in child_nodes:
        if child_node.title == suggested_node_name:
            suggested_focus_node = child_node
            break
    
    if suggested_focus_node:
        manager.set_focus_node(suggested_focus_node.node_id)
        print(f"\n🎯 设置焦点节点: {suggested_focus_node.title}")
        print(f"   建议讨论: {suggested_node_name}")
    
    print(f"\n2️⃣ 思维导图状态")
    print("-" * 30)
    
    # 显示统计信息
    stats = manager.get_statistics()
    print(f"📊 总节点数: {stats['total_nodes']}")
    print(f"🌳 根节点数: {stats['root_nodes']}")
    print(f"🍃 叶子节点数: {stats['leaf_nodes']}")
    print(f"📏 最大深度: {stats['max_depth']}")
    print(f"🎯 焦点节点: {manager.get_focus_node().title if manager.get_focus_node() else '无'}")
    
    print(f"\n3️⃣ 焦点节点操作演示")
    print("-" * 30)
    
    # 演示向焦点节点添加子节点
    focus_node = manager.get_focus_node()
    if focus_node:
        print(f"当前焦点节点: {focus_node.title}")
        
        # 向焦点节点添加子节点
        sub_task1 = MindMapNode("Aerodynamics", "Design aerodynamic shape", "subtask")
        sub_task2 = MindMapNode("Propulsion", "Design propulsion system", "subtask")
        
        manager.add_child_to_focus_node(sub_task1)
        manager.add_child_to_focus_node(sub_task2)
        
        print(f"✅ 向焦点节点添加了 2 个子节点:")
        for child in focus_node.get_children(manager.nodes):
            print(f"   🔸 {child.title}")
    
    print(f"\n4️⃣ 切换焦点节点演示")
    print("-" * 30)
    
    # 切换到另一个节点
    new_focus_name = "Materials"
    for child_node in child_nodes:
        if child_node.title == new_focus_name:
            manager.set_focus_node(child_node.node_id)
            print(f"🔄 切换焦点节点到: {child_node.title}")
            print(f"   之前的焦点节点状态: {suggested_focus_node.is_focus_node()}")
            print(f"   新的焦点节点状态: {child_node.is_focus_node()}")
            break
    
    print(f"\n5️⃣ 序列化测试")
    print("-" * 30)
    
    # 测试序列化
    data = manager.export_to_dict()
    print(f"💾 序列化成功，数据大小: {len(str(data))} 字符")
    
    # 反序列化
    new_manager = MindMapManager.from_dict(data)
    restored_focus = new_manager.get_focus_node()
    print(f"📤 反序列化后焦点节点: {restored_focus.title if restored_focus else '无'}")
    
    print(f"\n6️⃣ 前端显示数据示例")
    print("-" * 30)
    
    # 模拟前端显示数据
    current_focus = manager.get_focus_node()
    if current_focus:
        node_data = {
            "node_id": current_focus.node_id,
            "title": current_focus.title,
            "content": current_focus.content,
            "node_type": current_focus.node_type,
            "position": current_focus.position,
            "is_focused": current_focus.is_focus_node(),
            "parent_node": main_node.node_id if current_focus != main_node else None,
            "suggested_next": suggested_node_name,
            "total_children": len(current_focus.get_children(manager.nodes))
        }
        
        print("📱 前端将显示以下信息:")
        print(f"   标题: {node_data['title']}")
        print(f"   内容: {node_data['content']}")
        print(f"   类型: {node_data['node_type']}")
        print(f"   焦点状态: {'🎯 焦点节点' if node_data['is_focused'] else '普通节点'}")
        print(f"   建议讨论: {node_data['suggested_next']}")
        print(f"   子节点数: {node_data['total_children']}")
    
    print(f"\n🎉 演示完成！")
    print("=" * 50)
    print("💡 功能特点:")
    print("   • 自动创建主节点和子节点")
    print("   • 智能设置焦点节点")
    print("   • 支持焦点节点切换")
    print("   • 向焦点节点添加子节点")
    print("   • 完整的序列化支持")
    print("   • 前端视觉标识")

if __name__ == "__main__":
    demo_mindmap_focus() 