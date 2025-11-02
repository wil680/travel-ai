from dotenv import load_dotenv
from pydantic import BaseModel 
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

load_dotenv() 

#llm = ChatOpenAI(model="gpt-4o-mini")
#llm2 = ChatAnthropic(model="claude-2")
llm3 = ChatGroq(model="llama-3.3-70b-versatile")



result = llm3.invoke("I want to travel to Japan in spring. What are some must-see places and tips for my trip?")

print(result)

