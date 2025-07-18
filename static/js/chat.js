// 聊天功能管理
class ChatManager {
    constructor() {
        this.currentSessionId = null;
        this.conversationRounds = 0;
        this.init();
    }

    init() {
        // 绑定事件监听器
        this.bindEvents();
    }

    bindEvents() {
        // 绑定发送按钮事件
        const sendButton = document.querySelector('.chat-input button');
        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }

        // 绑定输入框回车事件
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.addEventListener('keypress', (event) => this.handleKeyPress(event));
        }

        // 绑定清空对话按钮
        const clearButton = document.querySelector('.chat-actions button[onclick="clearChat()"]');
        if (clearButton) {
            clearButton.onclick = () => this.clearChat();
        }

        // 绑定会话信息按钮
        const infoButton = document.querySelector('.chat-actions button[onclick="showChatInfo()"]');
        if (infoButton) {
            infoButton.onclick = () => this.showChatInfo();
        }

        // 绑定聊天面板关闭按钮
        const chatCloseButton = document.querySelector('.chat-widget .close-btn');
        if (chatCloseButton) {
            chatCloseButton.onclick = () => this.toggleChat();
        }
    }

    // 生成会话ID
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // 初始化会话
    initSession() {
        if (!this.currentSessionId) {
            this.currentSessionId = this.generateSessionId();
            this.conversationRounds = 0;
        }
    }

    // 切换聊天窗口显示状态
    toggleChat() {
        const widget = document.getElementById('chatWidget');
        const closeBtn = document.querySelector('.close-btn');
        if (widget.classList.contains('minimized')) {
            widget.classList.remove('minimized');
            closeBtn.textContent = '−';
        } else {
            widget.classList.add('minimized');
            closeBtn.textContent = '+';
        }
    }

    // 发送消息
    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        if (!message) return;

        // 初始化会话
        this.initSession();

        this.addMessage(message, 'user');
        input.value = '';

        // 显示加载状态
        const loadingDiv = this.addMessage('正在思考...', 'bot');
        loadingDiv.classList.add('loading');

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.currentSessionId
                })
            });

            if (!response.ok) {
                throw new Error('网络请求失败');
            }

            loadingDiv.remove();
            const botMessageDiv = this.addMessage('', 'bot');

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                let lines = buffer.split('\n');
                buffer = lines.pop(); // 可能有半截数据

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                                                            if (data.type === 'chunk') {
                                    botMessageDiv.textContent += data.content;
                                } else if (data.type === 'mindmap_node') {
                                    // 显示思维导图节点
                                    this.showMindMapNode(data.node);
                                } else if (data.type === 'end') {
                                    // 对话完成，更新轮数
                                    this.conversationRounds++;
                                } else if (data.type === 'error') {
                                    botMessageDiv.textContent = '抱歉，处理您的请求时出现了错误。';
                                }
                        } catch (e) {
                            console.error('解析响应数据失败:', e);
                        }
                    }
                }
            }

        } catch (error) {
            console.error('发送消息失败:', error);
            loadingDiv.remove();
            this.addMessage('抱歉，连接服务器时出现了问题。', 'bot');
        }
    }

    // 添加消息到聊天界面
    addMessage(text, sender) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = text;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return messageDiv; // 返回创建的元素，以便后续操作
    }

    // 清空对话
    async clearChat() {
        if (!this.currentSessionId) return;

        try {
            const response = await fetch('/chat/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ session_id: this.currentSessionId })
            });

            if (response.ok) {
                // 清空前端显示
                const messagesContainer = document.getElementById('chatMessages');
                messagesContainer.innerHTML = '<div class="message bot">Hey! I\'m Eure. What can I serve you?</div>';

                // 重置轮数
                this.conversationRounds = 0;

                alert('对话历史已清空');
            }
        } catch (error) {
            console.error('清空对话失败:', error);
            alert('清空对话失败');
        }
    }

    // 显示会话信息
    async showChatInfo() {
        if (!this.currentSessionId) {
            alert('当前没有活跃的会话');
            return;
        }

        try {
            const response = await fetch(`/chat/info/${this.currentSessionId}`);
            const info = await response.json();

            if (response.ok) {
                alert(`会话信息:\n会话ID: ${info.session_id}\n当前轮数: ${info.current_rounds}/${info.max_rounds}\n总消息数: ${info.total_messages}`);
            } else {
                alert('获取会话信息失败');
            }
        } catch (error) {
            console.error('获取会话信息失败:', error);
            alert('获取会话信息失败');
        }
    }

    // 显示思维导图节点
    showMindMapNode(nodeData) {
        console.log('显示思维导图节点:', nodeData);
        
        const container = document.getElementById('mindmapContainer');
        const titleElement = document.getElementById('nodeTitle');
        const contentElement = document.getElementById('nodeContent');
        const typeElement = document.getElementById('nodeType');
        const childrenContainer = document.getElementById('mindmapChildren');
        const connectionsContainer = document.getElementById('mindmapConnections');
        const nodeElement = document.getElementById('mindmapNode');
        
        // 设置主节点内容（简化显示）
        titleElement.textContent = nodeData.title;
        contentElement.textContent = nodeData.content;
        typeElement.textContent = nodeData.node_type;
        
        // 主节点不是焦点
        nodeElement.classList.remove('focused');
        
        // 显示容器
        container.style.display = 'block';
        console.log('思维导图容器已显示');
        
        // 创建子节点
        if (nodeData.children && nodeData.children.length > 0) {
            childrenContainer.innerHTML = ''; // 清空现有子节点
            connectionsContainer.innerHTML = ''; // 清空现有连接线
            
            // 计算放射状布局的角度
            const totalChildren = nodeData.children.length;
            const angleStep = 360 / totalChildren;
            const radius = 200; // 放射状半径
            
            nodeData.children.forEach((childData, index) => {
                const childElement = document.createElement('div');
                childElement.className = 'mindmap-child-node';
                childElement.dataset.nodeId = childData.node_id;
                childElement.dataset.index = index;
                
                // 设置焦点状态
                if (childData.is_focused) {
                    childElement.classList.add('focused');
                    console.log(`子节点 ${childData.title} 设置为焦点状态`);
                }
                
                childElement.innerHTML = `
                    <div class="child-title">${childData.title}</div>
                    <div class="child-content">${childData.content}</div>
                `;
                
                // 添加点击事件（可选）
                childElement.addEventListener('click', () => {
                    console.log(`点击子节点: ${childData.title}`);
                    // 这里可以添加子节点点击逻辑
                });
                
                childrenContainer.appendChild(childElement);
            });
            
            childrenContainer.style.display = 'flex';
            
            // 在下一帧应用放射状布局和绘制连接线
            setTimeout(() => {
                applyRadialLayout();
                drawConnectionLines();
            }, 100);
        } else {
            childrenContainer.style.display = 'none';
            connectionsContainer.innerHTML = '';
        }
        
        // 添加思维导图节点关闭按钮事件
        const closeBtn = document.getElementById('nodeCloseBtn');
        
        // 移除之前的事件监听器（如果有的话）
        const oldHideNode = nodeElement._hideNodeFunction;
        if (oldHideNode) {
            console.log('清除之前的隐藏函数和定时器');
            closeBtn.removeEventListener('click', oldHideNode);
            clearTimeout(nodeElement._hideTimeout);
        }
        
        const hideNode = () => {
            console.log('手动隐藏思维导图节点');
            container.style.display = 'none';
            closeBtn.removeEventListener('click', hideNode);
            nodeElement._hideNodeFunction = null;
            nodeElement._hideTimeout = null;
        };
        
        // 保存引用以便后续移除
        nodeElement._hideNodeFunction = hideNode;
        
        // 只有关闭按钮可以隐藏节点
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // 阻止事件冒泡
            e.preventDefault(); // 阻止默认行为
            console.log('用户点击关闭按钮');
            hideNode();
        });
        
        // 防止节点点击事件冒泡到聊天面板
        nodeElement.addEventListener('click', (e) => {
            e.stopPropagation();
        });
        
        // 完全禁用自动隐藏 - 节点将一直显示直到用户手动关闭
        console.log('自动隐藏已禁用，节点将永久显示');
        
        // 确保没有定时器在运行
        if (nodeElement._hideTimeout) {
            clearTimeout(nodeElement._hideTimeout);
            nodeElement._hideTimeout = null;
            console.log('清除任何可能存在的定时器');
        }
        
        // 如果需要自动隐藏，可以设置更长时间，比如5分钟：
        // nodeElement._hideTimeout = setTimeout(hideNode, 300000);
    }
    
    // 应用放射状布局
    applyRadialLayout() {
        const mainNode = document.getElementById('mindmapNode');
        const childrenContainer = document.getElementById('mindmapChildren');
        const childNodes = childrenContainer.querySelectorAll('.mindmap-child-node');
        
        if (!mainNode || childNodes.length === 0) {
            return;
        }
        
        const mainRect = mainNode.getBoundingClientRect();
        const containerRect = childrenContainer.getBoundingClientRect();
        
        // 主节点中心点
        const mainCenterX = mainRect.left + mainRect.width / 2;
        const mainCenterY = mainRect.top + mainRect.height / 2;
        
        const totalChildren = childNodes.length;
        const angleStep = 360 / totalChildren;
        const radius = 250; // 放射状半径
        
        childNodes.forEach((childNode, index) => {
            // 计算角度（从顶部开始，顺时针）
            const angle = (index * angleStep - 90) * (Math.PI / 180);
            
            // 计算位置
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            
            // 设置子节点位置
            childNode.style.position = 'absolute';
            childNode.style.left = `${x}px`;
            childNode.style.top = `${y}px`;
            childNode.style.transform = 'translate(-50%, -50%)';
            
            console.log(`子节点 ${index}: 角度=${angle * 180 / Math.PI}°, x=${x}, y=${y}`);
        });
        
        // 调整容器样式以支持绝对定位
        childrenContainer.style.position = 'relative';
        childrenContainer.style.width = `${radius * 2 + 100}px`;
        childrenContainer.style.height = `${radius * 2 + 100}px`;
        childrenContainer.style.margin = '0 auto';
    }
    
    // 绘制连接线
    drawConnectionLines() {
        const mainNode = document.getElementById('mindmapNode');
        const childrenContainer = document.getElementById('mindmapChildren');
        const connectionsContainer = document.getElementById('mindmapConnections');
        const childNodes = childrenContainer.querySelectorAll('.mindmap-child-node');
        
        if (!mainNode || !childrenContainer || childNodes.length === 0) {
            return;
        }
        
        // 获取主节点位置
        const mainRect = mainNode.getBoundingClientRect();
        const containerRect = childrenContainer.getBoundingClientRect();
        
        // 主节点中心点
        const mainCenterX = mainRect.left + mainRect.width / 2;
        const mainCenterY = mainRect.top + mainRect.height / 2;
        
        childNodes.forEach((childNode, index) => {
            const childRect = childNode.getBoundingClientRect();
            
            // 子节点中心点
            const childCenterX = childRect.left + childRect.width / 2;
            const childCenterY = childRect.top + childRect.height / 2;
            
            // 计算连接线
            const startX = mainCenterX - containerRect.left;
            const startY = mainCenterY - containerRect.top;
            const endX = childCenterX - containerRect.left;
            const endY = childCenterY - containerRect.top;
            
            // 创建连接线元素
            const line = document.createElement('div');
            line.className = 'connection-line';
            
            // 计算线的长度和角度
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            const length = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
            const angle = Math.atan2(deltaY, deltaX) * 180 / Math.PI;
            
            // 设置线的样式
            line.style.left = startX + 'px';
            line.style.top = startY + 'px';
            line.style.width = length + 'px';
            line.style.transform = `rotate(${angle}deg)`;
            
            console.log(`连接线 ${index}: 长度=${length}px, 角度=${angle}°`);
            
            connectionsContainer.appendChild(line);
        });
    }
    
    // 处理键盘事件
    handleKeyPress(event) {
        if (event.key === 'Enter') {
            this.sendMessage();
        }
    }
}

// 全局函数，用于HTML中的onclick调用
let chatManager;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    chatManager = new ChatManager();
    window.chatManager = chatManager; // 设置为全局变量，供思维导图系统使用
});

// 全局函数，保持与HTML的兼容性
function toggleChat() {
    if (chatManager) chatManager.toggleChat();
}

function sendMessage() {
    if (chatManager) chatManager.sendMessage();
}

function clearChat() {
    if (chatManager) chatManager.clearChat();
}

function showChatInfo() {
    if (chatManager) chatManager.showChatInfo();
}

function handleKeyPress(event) {
    if (chatManager) chatManager.handleKeyPress(event);
} 