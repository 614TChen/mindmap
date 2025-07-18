from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
import uuid
import asyncio
from typing import AsyncGenerator
from dotenv import load_dotenv
from message_manager import MessageManager
from agents.starter import run_starter_agent
from nodes import MindMapNode, MindMapManager

# 加载环境变量
load_dotenv()

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载模板目录
templates = Jinja2Templates(directory="templates")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 初始化消息管理器
message_manager = MessageManager(max_rounds=10)

# 初始化思维导图管理器
mindmap_manager = MindMapManager()
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_endpoint(request: Request):
    """聊天API端点，使用starter_agent处理"""
    try:
        data = await request.json()
        user_message = data.get("message", "")
        session_id = data.get("session_id", str(uuid.uuid4()))
        
        if not user_message:
            return {"error": "消息不能为空"}
        
        # 添加用户消息到历史
        message_manager.add_message(session_id, "user", user_message)
        
        # 返回流式响应
        return StreamingResponse(
            stream_starter_agent_response(user_message, session_id),
            media_type="text/plain"
        )
        
    except Exception as e:
        return {"error": f"处理请求时出错: {str(e)}"}

@app.post("/chat/clear")
async def clear_chat(request: Request):
    """清空指定会话的聊天历史"""
    try:
        data = await request.json()
        session_id = data.get("session_id")
        
        if session_id:
            message_manager.clear_conversation(session_id)
            return {"message": "聊天历史已清空"}
        else:
            return {"error": "缺少session_id"}
            
    except Exception as e:
        return {"error": f"清空聊天历史时出错: {str(e)}"}

@app.get("/chat/info/{session_id}")
async def get_chat_info(session_id: str):
    """获取会话信息"""
    try:
        info = message_manager.get_conversation_info(session_id)
        return info
    except Exception as e:
        return {"error": f"获取会话信息时出错: {str(e)}"}

async def stream_starter_agent_response(user_message: str, session_id: str) -> AsyncGenerator[str, None]:
    """使用starter_agent的流式响应生成器"""
    try:
        # 在线程池中运行starter_agent（因为它是同步的）
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_starter_agent, user_message)
        
        if result is None:
            yield f"data: {json.dumps({'error': 'Agent处理失败', 'type': 'error'})}\n\n"
            return
        
        # 构建响应文本
        response_text = result.reply
        
        # 模拟流式输出（逐字符发送）
        for char in response_text:
            yield f"data: {json.dumps({'content': char, 'type': 'chunk'})}\n\n"
            await asyncio.sleep(0.01)  # 模拟打字效果
        
        # 添加助手回复到历史
        message_manager.add_message(session_id, "assistant", response_text)
        
        # 如果启动思维导图，发送节点创建指令给前端
        if result.start_mindmap:
            # 构建节点创建指令
            mindmap_instruction = {
                "type": "create_mindmap_nodes",
                "main_node": {
                    "title": result.node_description,
                    "content": result.idea_description,
                    "node_type": "idea"
                },
                "child_nodes": [],
                "suggested_focus": result.dicuss_next
            }
            
            # 添加子节点信息
            if result.new_node_list:
                for node_info in result.new_node_list:
                    mindmap_instruction["child_nodes"].append({
                        "title": node_info.name,
                        "content": node_info.description or "",
                        "node_type": "subtask"
                    })
            
            yield f"data: {json.dumps(mindmap_instruction)}\n\n"
        
        # 发送完成信号
        yield f"data: {json.dumps({'content': '', 'type': 'end'})}\n\n"
        
    except Exception as e:
        # 发送错误信息
        print(f"Starter agent error: {str(e)}")
        yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 