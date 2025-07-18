// 思维导图绘制管理器
class MindMapManager {
    constructor() {
        this.nodes = new Map(); // 存储所有节点
        this.connections = []; // 存储所有连接
        this.selectedNode = null; // 当前选中的节点
        this.connectingNode = null; // 正在连线的起始节点
        this.tempConnection = null; // 临时连接线
        this.mode = 'select'; // 当前模式：select, connect, cut
        this.draggingNode = null; // 正在拖拽的节点
        this.dragOffset = { x: 0, y: 0 };
        
        // 鼠标位置跟踪（用于惯性计算）
        this.currentMouseX = 0;
        this.currentMouseY = 0;
        this.lastMouseX = 0;
        this.lastMouseY = 0;
        
        // 切割模式相关
        this.isCutting = false; // 是否正在切割
        this.cutPath = []; // 切割路径点
        this.cutLine = null; // 切割线元素
        
        this.canvas = document.getElementById('mindmapCanvas');
        this.statusBar = document.getElementById('statusBar');
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.updateStatus('就绪 - 点击"添加节点"开始创建思维导图');
    }
    
    bindEvents() {
        // 工具栏按钮事件
        document.getElementById('addNodeBtn').addEventListener('click', () => this.showAddNodeModal());
        document.getElementById('connectBtn').addEventListener('click', () => this.setMode('connect'));
        document.getElementById('selectBtn').addEventListener('click', () => this.setMode('select'));
        document.getElementById('cutBtn').addEventListener('click', () => this.setMode('cut'));
        document.getElementById('clearBtn').addEventListener('click', () => this.clearAll());
        document.getElementById('exportBtn').addEventListener('click', () => this.exportMindMap());
        
        // 添加节点窗口事件
        document.getElementById('cancelAddBtn').addEventListener('click', () => this.hideAddNodeModal());
        document.getElementById('confirmAddBtn').addEventListener('click', () => this.addNode());
        
        // 画布事件
        this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        this.canvas.addEventListener('mousedown', (e) => this.handleCanvasMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleCanvasMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleCanvasMouseUp(e));
        
        // 键盘事件
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
    }
    
    // 显示添加节点窗口
    showAddNodeModal() {
        document.getElementById('addNodeModal').style.display = 'flex';
        document.getElementById('nodeTitle').focus();
        this.updateStatus('添加新节点 - 请输入节点信息');
    }
    
    // 隐藏添加节点窗口
    hideAddNodeModal() {
        document.getElementById('addNodeModal').style.display = 'none';
        document.getElementById('nodeTitle').value = '';
        document.getElementById('nodeContent').value = '';
        this.updateStatus('就绪');
    }
    
    // 添加新节点
    addNode() {
        const title = document.getElementById('nodeTitle').value.trim();
        const content = document.getElementById('nodeContent').value.trim();
        
        if (!title) {
            alert('请输入节点标题');
            return;
        }
        
        const nodeId = 'node_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const node = {
            id: nodeId,
            title: title,
            content: content,
            x: Math.random() * (window.innerWidth - 300) + 150,
            y: Math.random() * (window.innerHeight - 200) + 100
        };
        
        this.nodes.set(nodeId, node);
        this.createNodeElement(node);
        this.hideAddNodeModal();
        this.updateStatus(`已添加节点: ${title}`);
    }
    
    // 创建节点DOM元素
    createNodeElement(node) {
        const nodeElement = document.createElement('div');
        nodeElement.className = 'mindmap-node';
        nodeElement.dataset.nodeId = node.id;
        nodeElement.style.left = node.x + 'px';
        nodeElement.style.top = node.y + 'px';
        
        nodeElement.innerHTML = `
            <div class="node-title">${node.title}</div>
            <div class="node-content">${node.content}</div>
            <div class="node-actions">
                <button class="delete-btn" title="删除节点">×</button>
            </div>
        `;
        
        // 设置焦点状态（如果节点有焦点状态信息）
        if (node.is_focused) {
            nodeElement.classList.add('focused');
            console.log(`节点 ${node.title} 设置为焦点状态`);
        }
        
        // 绑定节点事件
        nodeElement.addEventListener('mousedown', (e) => this.handleNodeMouseDown(e, node));
        nodeElement.addEventListener('click', (e) => this.handleNodeClick(e, node));
        nodeElement.querySelector('.delete-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.deleteNode(node.id);
        });
        
        this.canvas.appendChild(nodeElement);
    }
    
    // 删除节点
    deleteNode(nodeId) {
        if (confirm('确定要删除这个节点吗？相关的连接线也会被删除。')) {
            // 删除相关连接
            this.connections = this.connections.filter(conn => 
                conn.from !== nodeId && conn.to !== nodeId
            );
            
            // 删除节点
            this.nodes.delete(nodeId);
            
            // 删除DOM元素
            const nodeElement = document.querySelector(`[data-node-id="${nodeId}"]`);
            if (nodeElement) {
                nodeElement.remove();
            }
            
            // 重新绘制连接线
            this.redrawConnections();
            
            this.updateStatus('节点已删除');
        }
    }
    
    // 设置模式
    setMode(mode) {
        this.mode = mode;
        
        // 更新按钮状态
        document.getElementById('connectBtn').classList.toggle('active', mode === 'connect');
        document.getElementById('selectBtn').classList.toggle('active', mode === 'select');
        document.getElementById('cutBtn').classList.toggle('active', mode === 'cut');
        
        // 清除选择状态
        this.clearSelection();
        
        if (mode === 'connect') {
            this.updateStatus('连线模式 - 点击一个节点开始连线，再点击另一个节点完成连线');
        } else if (mode === 'cut') {
            this.updateStatus('切割模式 - 按住鼠标左键并移动来切断连线');
        } else {
            this.updateStatus('选择模式 - 可以拖拽节点，双击编辑');
        }
    }
    
    // 处理节点点击
    handleNodeClick(e, node) {
        e.stopPropagation();
        
        if (this.mode === 'connect') {
            if (!this.connectingNode) {
                // 开始连线
                this.connectingNode = node;
                this.selectNode(node);
                this.updateStatus(`已选择起始节点: ${node.title} - 请点击目标节点`);
            } else if (this.connectingNode.id !== node.id) {
                // 完成连线
                this.createConnection(this.connectingNode.id, node.id);
                this.connectingNode = null;
                this.clearSelection();
                this.updateStatus('连线完成');
            }
        } else {
            // 选择模式
            this.selectNode(node);
        }
    }
    
    // 选择节点
    selectNode(node) {
        this.clearSelection();
        this.selectedNode = node;
        
        const nodeElement = document.querySelector(`[data-node-id="${node.id}"]`);
        if (nodeElement) {
            nodeElement.classList.add('selected');
        }
    }
    
    // 清除选择
    clearSelection() {
        if (this.selectedNode) {
            const nodeElement = document.querySelector(`[data-node-id="${this.selectedNode.id}"]`);
            if (nodeElement) {
                nodeElement.classList.remove('selected');
            }
            this.selectedNode = null;
        }
    }
    
    // 创建连接
    createConnection(fromId, toId) {
        // 检查是否已存在连接
        const existingConnection = this.connections.find(conn => 
            (conn.from === fromId && conn.to === toId) || 
            (conn.from === toId && conn.to === fromId)
        );
        
        if (existingConnection) {
            alert('这两个节点之间已经存在连接');
            return;
        }
        
        const connection = {
            id: 'conn_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
            from: fromId,
            to: toId
        };
        
        this.connections.push(connection);
        this.drawConnection(connection);
        this.updateStatus('连接已创建');
    }
    
    // 绘制连接线
    drawConnection(connection) {
        const fromNode = this.nodes.get(connection.from);
        const toNode = this.nodes.get(connection.to);
        
        if (!fromNode || !toNode) return;
        
        const line = document.createElement('div');
        line.className = 'connection-line';
        line.dataset.connectionId = connection.id;
        
        this.canvas.appendChild(line);
        this.updateConnectionPosition(connection);
    }
    
    // 更新连接线位置
    updateConnectionPosition(connection) {
        const fromNode = this.nodes.get(connection.from);
        const toNode = this.nodes.get(connection.to);
        
        if (!fromNode || !toNode) return;
        
        const line = document.querySelector(`[data-connection-id="${connection.id}"]`);
        if (!line) return;
        
        const fromElement = document.querySelector(`[data-node-id="${connection.from}"]`);
        const toElement = document.querySelector(`[data-node-id="${connection.to}"]`);
        
        if (!fromElement || !toElement) return;
        
        const fromRect = fromElement.getBoundingClientRect();
        const toRect = toElement.getBoundingClientRect();
        
        const fromX = fromRect.left + fromRect.width / 2;
        const fromY = fromRect.top + fromRect.height / 2;
        const toX = toRect.left + toRect.width / 2;
        const toY = toRect.top + toRect.height / 2;
        
        const length = Math.sqrt(Math.pow(toX - fromX, 2) + Math.pow(toY - fromY, 2));
        const angle = Math.atan2(toY - fromY, toX - fromX) * 180 / Math.PI;
        
        // 使用transform3d来获得更好的性能
        line.style.width = length + 'px';
        line.style.left = fromX + 'px';
        line.style.top = fromY + 'px';
        line.style.transform = `rotate3d(0, 0, 1, ${angle}deg)`;
    }
    
    // 重新绘制所有连接线
    redrawConnections() {
        // 清除所有连接线
        document.querySelectorAll('.connection-line').forEach(line => line.remove());
        
        // 重新绘制
        this.connections.forEach(connection => {
            this.drawConnection(connection);
        });
    }
    
    // 处理画布鼠标按下
    handleCanvasMouseDown(e) {
        if (this.mode === 'cut' && e.button === 0) { // 切割模式下的左键
            this.startCutting(e);
        }
    }
    
    // 开始切割
    startCutting(e) {
        this.isCutting = true;
        this.cutPath = [{ x: e.clientX, y: e.clientY }];
        
        // 创建切割线
        this.cutLine = document.createElement('div');
        this.cutLine.className = 'cut-line';
        this.canvas.appendChild(this.cutLine);
        
        this.updateStatus('切割中... 移动鼠标切断连线');
    }
    
    // 处理节点拖拽开始
    handleNodeMouseDown(e, node) {
        if (this.mode === 'select' && e.button === 0) { // 左键
            e.preventDefault();
            this.draggingNode = node;
            
            const nodeElement = e.currentTarget;
            const rect = nodeElement.getBoundingClientRect();
            this.dragOffset.x = e.clientX - rect.left;
            this.dragOffset.y = e.clientY - rect.top;
            
            nodeElement.classList.add('dragging');
            this.updateStatus('拖拽节点中...');
        }
    }
    
    // 处理画布鼠标移动
    handleCanvasMouseMove(e) {
        // 更新鼠标位置跟踪
        this.lastMouseX = this.currentMouseX;
        this.lastMouseY = this.currentMouseY;
        this.currentMouseX = e.clientX;
        this.currentMouseY = e.clientY;
        
        if (this.draggingNode) {
            const nodeElement = document.querySelector(`[data-node-id="${this.draggingNode.id}"]`);
            if (nodeElement) {
                const newX = e.clientX - this.dragOffset.x;
                const newY = e.clientY - this.dragOffset.y;
                
                // 边界检查
                const maxX = window.innerWidth - nodeElement.offsetWidth;
                const maxY = window.innerHeight - nodeElement.offsetHeight;
                
                this.draggingNode.x = Math.max(0, Math.min(newX, maxX));
                this.draggingNode.y = Math.max(0, Math.min(newY, maxY));
                
                nodeElement.style.left = this.draggingNode.x + 'px';
                nodeElement.style.top = this.draggingNode.y + 'px';
                
                // 实时更新相关连接线
                this.updateConnectionsForNode(this.draggingNode.id);
            }
        }
        
        // 处理切割模式
        if (this.isCutting) {
            this.updateCutting(e);
        }
    }
    
    // 处理画布鼠标释放
    handleCanvasMouseUp(e) {
        if (this.draggingNode) {
            const nodeElement = document.querySelector(`[data-node-id="${this.draggingNode.id}"]`);
            if (nodeElement) {
                // 添加惯性滑行效果
                this.applyInertiaEffect(nodeElement, this.draggingNode);
            }
            this.draggingNode = null;
        }
        
        // 处理切割结束
        if (this.isCutting) {
            this.endCutting();
        }
    }
    
    // 应用惯性滑行效果
    applyInertiaEffect(nodeElement, node) {
        // 移除拖拽状态，添加惯性状态
        nodeElement.classList.remove('dragging');
        nodeElement.classList.add('inertia');
        
        // 计算惯性滑行的目标位置
        const currentX = parseFloat(nodeElement.style.left);
        const currentY = parseFloat(nodeElement.style.top);
        
        // 计算鼠标移动速度来模拟更真实的惯性
        const velocityX = this.lastMouseX ? this.lastMouseX - this.currentMouseX : 0;
        const velocityY = this.lastMouseY ? this.lastMouseY - this.currentMouseY : 0;
        
        // 根据速度计算惯性偏移（速度越大，惯性越大）
        const inertiaDistance = Math.min(Math.abs(velocityX) + Math.abs(velocityY), 50);
        const inertiaX = currentX + (velocityX * 0.3);
        const inertiaY = currentY + (velocityY * 0.3);
        
        // 边界检查
        const maxX = window.innerWidth - nodeElement.offsetWidth;
        const maxY = window.innerHeight - nodeElement.offsetHeight;
        
        const finalX = Math.max(0, Math.min(inertiaX, maxX));
        const finalY = Math.max(0, Math.min(inertiaY, maxY));
        
        // 更新节点位置
        node.x = finalX;
        node.y = finalY;
        
        nodeElement.style.left = finalX + 'px';
        nodeElement.style.top = finalY + 'px';
        
        // 在过渡动画期间持续更新连接线
        this.updateConnectionsDuringInertia(node.id, 400); // 400ms是CSS过渡时间
        
        // 动画结束后清理
        setTimeout(() => {
            nodeElement.classList.remove('inertia');
            this.updateStatus('节点位置已更新');
        }, 400);
    }
    
    // 在惯性动画期间持续更新连接线
    updateConnectionsDuringInertia(nodeId, duration) {
        const startTime = Date.now();
        
        const updateConnections = () => {
            const elapsed = Date.now() - startTime;
            
            if (elapsed < duration) {
                // 更新相关连接线
                this.updateConnectionsForNode(nodeId);
                requestAnimationFrame(updateConnections);
            } else {
                // 动画结束，最终更新一次
                this.updateConnectionsForNode(nodeId);
            }
        };
        
        // 立即开始更新
        updateConnections();
    }
    
    // 更新指定节点的所有连接线
    updateConnectionsForNode(nodeId) {
        this.connections.forEach(connection => {
            if (connection.from === nodeId || connection.to === nodeId) {
                this.updateConnectionPosition(connection);
                
                // 在动画期间添加视觉反馈
                const line = document.querySelector(`[data-connection-id="${connection.id}"]`);
                if (line) {
                    line.classList.add('animating');
                    // 短暂后移除动画类
                    setTimeout(() => {
                        line.classList.remove('animating');
                    }, 100);
                }
            }
        });
    }
    
    // 处理画布点击
    handleCanvasClick(e) {
        if (e.target === this.canvas) {
            this.clearSelection();
            if (this.mode === 'connect' && this.connectingNode) {
                this.connectingNode = null;
                this.updateStatus('连线已取消');
            }
        }
    }
    
    // 处理键盘事件
    handleKeyDown(e) {
        if (e.key === 'Escape') {
            this.clearSelection();
            if (this.connectingNode) {
                this.connectingNode = null;
                this.updateStatus('连线已取消');
            }
        } else if (e.key === 'Delete' && this.selectedNode) {
            this.deleteNode(this.selectedNode.id);
        }
    }
    
    // 清空所有内容
    clearAll() {
        if (confirm('确定要清空所有节点和连接吗？此操作不可撤销。')) {
            this.nodes.clear();
            this.connections = [];
            this.selectedNode = null;
            this.connectingNode = null;
            
            // 清除DOM元素
            this.canvas.innerHTML = '';
            
            this.updateStatus('已清空所有内容');
        }
    }
    
    // 导出思维导图
    exportMindMap() {
        const data = {
            nodes: Array.from(this.nodes.values()),
            connections: this.connections,
            exportTime: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `mindmap_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.updateStatus('思维导图已导出');
    }
    
    // 更新状态栏
    updateStatus(message) {
        this.statusBar.textContent = message;
    }
    
    // 更新切割
    updateCutting(e) {
        // 添加新的切割点
        this.cutPath.push({ x: e.clientX, y: e.clientY });
        
        // 更新切割线显示
        this.updateCutLine();
        
        // 检查是否切断了任何连接线
        this.checkCutConnections();
    }
    
    // 更新切割线显示
    updateCutLine() {
        if (this.cutPath.length < 2) return;
        
        const start = this.cutPath[0];
        const end = this.cutPath[this.cutPath.length - 1];
        
        const length = Math.sqrt(Math.pow(end.x - start.x, 2) + Math.pow(end.y - start.y, 2));
        const angle = Math.atan2(end.y - start.y, end.x - start.x) * 180 / Math.PI;
        
        this.cutLine.style.width = length + 'px';
        this.cutLine.style.left = start.x + 'px';
        this.cutLine.style.top = start.y + 'px';
        this.cutLine.style.transform = `rotate3d(0, 0, 1, ${angle}deg)`;
    }
    
    // 检查切割连接线
    checkCutConnections() {
        if (this.cutPath.length < 2) return;
        
        this.connections.forEach((connection, index) => {
            if (this.isConnectionCut(connection)) {
                this.cutConnection(connection, index);
            }
        });
    }
    
    // 判断连接线是否被切割
    isConnectionCut(connection) {
        const fromElement = document.querySelector(`[data-node-id="${connection.from}"]`);
        const toElement = document.querySelector(`[data-node-id="${connection.to}"]`);
        
        if (!fromElement || !toElement) return false;
        
        const fromRect = fromElement.getBoundingClientRect();
        const toRect = toElement.getBoundingClientRect();
        
        const fromX = fromRect.left + fromRect.width / 2;
        const fromY = fromRect.top + fromRect.height / 2;
        const toX = toRect.left + toRect.width / 2;
        const toY = toRect.top + toRect.height / 2;
        
        // 检查切割路径是否与连接线相交
        for (let i = 1; i < this.cutPath.length; i++) {
            const cutStart = this.cutPath[i - 1];
            const cutEnd = this.cutPath[i];
            
            if (this.linesIntersect(
                cutStart.x, cutStart.y, cutEnd.x, cutEnd.y,
                fromX, fromY, toX, toY
            )) {
                return true;
            }
        }
        
        return false;
    }
    
    // 判断两条线段是否相交
    linesIntersect(x1, y1, x2, y2, x3, y3, x4, y4) {
        const denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1);
        if (denom === 0) return false;
        
        const ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom;
        const ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom;
        
        return ua >= 0 && ua <= 1 && ub >= 0 && ub <= 1;
    }
    
    // 切断连接线
    cutConnection(connection, index) {
        // 添加切割动画效果
        const line = document.querySelector(`[data-connection-id="${connection.id}"]`);
        if (line) {
            line.classList.add('cut');
            
            // 动画结束后删除连接线
            setTimeout(() => {
                line.remove();
            }, 500);
        }
        
        // 从数据中移除连接
        this.connections.splice(index, 1);
        
        this.updateStatus(`已切断连接: ${connection.from} → ${connection.to}`);
    }
    
    // 结束切割
    endCutting() {
        this.isCutting = false;
        this.cutPath = [];
        
        // 移除切割线
        if (this.cutLine) {
            this.cutLine.remove();
            this.cutLine = null;
        }
        
        this.updateStatus('切割完成');
    }
}

// 初始化思维导图管理器
let mindMapManager;

document.addEventListener('DOMContentLoaded', () => {
    mindMapManager = new MindMapManager();
    window.mindMapManager = mindMapManager; // 设置为全局变量，供聊天系统使用
});

// 思维导图系统已准备就绪
console.log('思维导图绘制系统已加载'); 