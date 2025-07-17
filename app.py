from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
import uuid
from typing import AsyncGenerator
from llama_index.llms.deepseek import DeepSeek
from llama_index.core.llms import ChatMessage
from dotenv import load_dotenv
from message_manager import MessageManager

os.environ["DEEPSEEK_API_KEY"] = "sk-5f8e86349f4d4f13a616426ef9328074"


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

# 初始化DeepSeek LLM
llm = DeepSeek(model="deepseek-chat", api_key="sk-5f8e86349f4d4f13a616426ef9328074")

# 初始化消息管理器
message_manager = MessageManager(max_rounds=10)
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_endpoint(request: Request):
    """聊天API端点，支持流式响应和对话历史管理"""
    try:
        data = await request.json()
        user_message = data.get("message", "")
        session_id = data.get("session_id", str(uuid.uuid4()))
        
        if not user_message:
            return {"error": "消息不能为空"}
        
        # 添加用户消息到历史
        message_manager.add_message(session_id, "user", user_message)
        
        # 获取完整上下文消息
        context_messages = message_manager.get_context_messages(session_id)
        
        # 返回流式响应
        return StreamingResponse(
            stream_chat_response(context_messages, session_id),
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

async def stream_chat_response(messages, session_id: str) -> AsyncGenerator[str, None]:
    """聊天响应生成器"""
    try:
        # 使用stream_chat方法，参考example4
        response_stream = llm.stream_chat(messages)
        
        full_response = ""
        for chunk in response_stream:
            if chunk.delta:
                full_response += chunk.delta
                # 发送每个响应块
                yield f"data: {json.dumps({'content': chunk.delta, 'type': 'chunk'})}\n\n"
        
        # 添加助手回复到历史
        if full_response:
            message_manager.add_message(session_id, "assistant", full_response)
        
        # 发送完成信号
        yield f"data: {json.dumps({'content': '', 'type': 'end'})}\n\n"
        
    except Exception as e:
        # 发送错误信息
        print(str(e))
        yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True) 