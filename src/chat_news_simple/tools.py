from utils import create_session, extract_news_details, get_news_list
from llms import keyword_chain,answer_chain

async def generate_answer(question: str, news_context: list) -> str:
    # 将所有新闻拼接作为上下文传递
    combined_news = "\n\n".join(news_context)
    answer = answer_chain.invoke({"news": combined_news, "question": question})
    return answer

async def fetch_news(question: str) -> str:
    session = create_session()

    # 提取关键词
    keywords = keyword_chain.invoke({"question": question})
    print(f"提取的关键词: {keywords}")

    # 获取相关新闻列表
    news_list = get_news_list(session, keyword=keywords, time_range="d", page=1, max_news=5)
    if not news_list:
        return None, "未找到相关新闻，请尝试更换关键词。"

    # 提取每篇新闻的详细内容并拼接
    news_context = []
    for news in news_list:
        news_details = extract_news_details(session, news)
        if not news_details:
            continue

        title, link, source, final_time, summary, content_text = news_details
        full_news_content = (
            f"标题: {title}\n"
            f"来源: {source}\n"
            f"时间: {final_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"摘要: {summary}\n"
            f"正文: {content_text}\n"
            f"链接: {link}"
        )
        news_context.append(full_news_content)

    return news_context, "新闻已加载完成，可继续提问！"
