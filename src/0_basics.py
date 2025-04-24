import os
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage

os.environ["AZURE_OPENAI_API_KEY"]="api_key"
os.environ["AZURE_OPENAI_ENDPOINT"]="endpoint"

# Standalone invocation of an LLM without being part of a graph
def invoke_llm_with_messages_list():
    from pprint import pprint

    prompts = [AIMessage(content=f"So you said you were researching ocean mammals?", name="Model")]
    prompts.append(HumanMessage(content=f"Yes, that's right.",name="Lance"))
    prompts.append(AIMessage(content=f"Great, what would you like to learn about.", name="Model"))
    prompts.append(HumanMessage(content=f"I want to learn about the best place to see Orcas in the US.", name="Lance"))

    for m in prompts:
        m.pretty_print()
    
    llm = AzureChatOpenAI(
        azure_deployment="gpt-4o",
        api_version="2025-03-01-preview",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )
    result = llm.invoke(prompts)
    print(result)    

if __name__ == '__main__':
    # Standalone llm invocation
    invoke_llm_with_messages_list()


