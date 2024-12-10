from datetime import datetime, timedelta
import chainlit as cl
from utils import create_session, extract_news_details, get_news_list
from tools import fetch_news, generate_answer  # 引入外部工具函数
# 定义新闻搜索工具
@cl.step(type="tool",name="search_news")
async def search_news(topic: str):
    session = create_session()
    await cl.Message(content="获取新闻列表中").send()
    news_list = get_news_list(session, keyword=topic, time_range="d", page=1, max_news=10)
    if not news_list:
        return "未找到相关新闻，请尝试更换关键词。"
    news_context = []
    for news in news_list:

        try:
            news_details = extract_news_details(session, news)
            if news_details:
                title, link, source, final_time, summary, content_text = news_details
                full_news_content = (
                    f"标题: {title}\n来源: {source}\n时间: {final_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"摘要: {summary}\n正文: {content_text}\n链接: {link}"
                )
                await cl.Message(content=f"获取到新闻：{title}").send()
                news_context.append(full_news_content)
        except Exception as e:
            print(f"Error extracting news details: {e}")
            continue

    return "\n\n".join(news_context)

@cl.on_chat_start
async def on_chat_start():
    # 当聊天开始时，初始化用户的会话数据
    cl.user_session.set("news_context", None)
    cl.user_session.set("last_activity", datetime.now())

# 处理用户消息
@cl.on_message
async def main(message: cl.Message):
    user_input = message.content.strip()
    
    # 获取当前会话中的数据
    news_context =cl.user_session.get("news_context")
    last_activity = cl.user_session.get("last_activity")
    
    # 判断是否是新对话的开始
    is_new_conversation = not news_context or (datetime.now() - last_activity) > timedelta(minutes=5)
    
    if is_new_conversation:
        # 如果是新对话，则使用用户输入作为搜索关键词进行新闻搜索
        try:
            news_context = await search_news(user_input)
            
            if news_context == "未找到相关新闻，请尝试更换关键词。":
                await cl.Message(content=news_context).send()
                return
            
            # 更新会话中的新闻上下文和最后活动时间
            cl.user_session.set("news_context", news_context)
            cl.user_session.set("last_activity", datetime.now())
            await cl.Message(content="新闻已加载完成，可继续提问！").send()
        except Exception as e:
            await cl.Message(content=f"发生错误: {str(e)}").send()
    else:
        # 如果不是新对话，则直接基于已有的新闻上下文生成回答
        answer = await generate_answer(message.content.strip(), news_context)
        await cl.Message(content=answer).send()