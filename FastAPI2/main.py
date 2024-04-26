from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import re
from typing import List, Union
import json
from dotenv import load_dotenv
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import BaseChatPromptTemplate
from langchain import LLMChain, SerpAPIWrapper
from langchain_community.chat_models import ChatOpenAI # type: ignore
from langchain_community.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import AgentAction, AgentFinish, HumanMessage, SystemMessage
from pinecone import Pinecone as pcone
from langchain_pinecone import Pinecone
from langchain.chains import RetrievalQA


load_dotenv(override=True)

serpapi_key = os.getenv('SERPAPI_API_KEY')
pinecone_api_key = os.getenv('PINECONE_API_KEY')

os.environ['SERPAPI_API_KEY'] = serpapi_key # type: ignore

app = FastAPI()

template_with_history="""You are SearchGPT, a professional search engine who provides informative answers to users. Answer the following questions as best you can. You have access to the following tools:
 
{tools}
 
Use the following format:
 
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat 2 times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question
 
Begin! Remember to give detailed, informative answers
 
Previous conversation history:
[{history}]
 
New question: {input}
{agent_scratchpad}"""


# Initialize Pinecone retriever
def initialize_pinecone_retriever():

    index_name = os.getenv('PINECONE_INDEX')
    os.environ['PINECONE_API_KEY'] = serpapi_key # type: ignore
    os.environ['PINECONE_ENVIRONMENT'] = 'us-east-1'  

    pc = pcone(api_key=pinecone_api_key)  
    
    index = pc.Index(index_name) # type: ignore
    print(index.describe_index_stats())
    embeddings = OpenAIEmbeddings()
    docsearch = Pinecone(index, embeddings, text_key='chunk_text') # type: ignore
    retrieval_llm = OpenAI(temperature=0)
    retriever = RetrievalQA.from_chain_type(llm=retrieval_llm, chain_type="stuff", retriever=docsearch.as_retriever())
    return retriever

retriever = initialize_pinecone_retriever()


# Langchain setup
search = SerpAPIWrapper()



class ChatRequest(BaseModel):
    user_input: str
    history: str

class CustomPromptTemplate(BaseChatPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

    def format_messages(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)

        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "

        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts

        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])

        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        formatted = self.template.format(**kwargs)
        return [HumanMessage(content=formatted)] # type: ignore


class CustomOutputParser(AgentOutputParser):
 
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
 
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
 
        # Parse out the action and action input
        regex = r"Action: (.*?)[\n]*Action Input:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
 
        # If it can't parse the output it raises an error
        # You can add your own logic here to handle errors in a different way i.e. pass to a human, give a canned response
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
 
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)

output_parser = CustomOutputParser()


tools = [
    Tool(
        name="Search", 
        func=search.run, 
        description="useful for when you need to answer questions about current events"),
    Tool(
        name = 'Knowledge Base',
        func=retriever.run,
        description="Useful for general questions about how to do things and for details on interesting topics. Input should be a fully formed question."
    )
]

llm = ChatOpenAI(temperature=0)

prompt_with_history = CustomPromptTemplate(
    template=template_with_history,
    tools=tools,
    input_variables=["input", "intermediate_steps", "history"]
)
llm_chain = LLMChain(llm=llm, prompt=prompt_with_history)
multi_tool_names = [tool.name for tool in tools]
multi_tool_agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=output_parser,
    stop=["\nObservation:"],
    allowed_tools=multi_tool_names # type: ignore
)


memory = ConversationBufferWindowMemory(k=2)
agent_executor = AgentExecutor.from_agent_and_tools(agent=multi_tool_agent, tools=tools, verbose=True, memory=memory)

    


@app.post("/chat/")
async def chat(request: ChatRequest):
    agent_output = agent_executor.run(input=request.user_input, history=request.history)
    return {"response": agent_output}

