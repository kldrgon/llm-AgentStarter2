from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_community.llms.tongyi import Tongyi
from langchain_core.output_parsers import StrOutputParser

tongyi_qwenplus_llm = Tongyi(model="qwen-plus")

# 定义 Prompt 模板
keyword_prompt_template = "从以下问题中提取关键词，用于新闻检索，只输出使用逗号间隔的关键词：\n问题：{question}\n"
keyword_prompt = PromptTemplate(
    input_variables=["question"], template=keyword_prompt_template
)

# 初始化模型
llm = tongyi_qwenplus_llm  # 替换为所需模型
# 构建 Runnables Pipeline
keyword_chain = keyword_prompt | llm | StrOutputParser()

# 定义回答的 Prompt 模板
answer_prompt_template = (
    "根据以下新闻内容和问题，生成一个详细的回答,注意不要脱离新闻内容，不要回复与用户问题不相关的回复：\n"
    "新闻内容：\n{news}\n\n"
    "问题：{question}\n\n"
    "回答："
)
answer_prompt = PromptTemplate(
    input_variables=["news", "question"], template=answer_prompt_template
)

# 构建 Runnables Pipeline
answer_chain = answer_prompt | llm | StrOutputParser()

