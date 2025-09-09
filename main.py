from langchain.google_genai import GoogleGenAI
from langchain import PromptTemplate, LLMChain
from langchain.graphs import Graph, Node, Edge
from pydantic import BaseModel
from dotenv import load_dotenv
import os
#start of the code
from fastapi import FastAPI, Request
from typing import Dict
from tools.json_reader import classify_prd
from tools.web_search import duckduckgo_search
from graph.risk_workflow import run_risk_workflow

app = FastAPI()

class PRDRequest(BaseModel):
    prd_json: Dict

@app.post("/analyze-risk")
async def analyze_risk(request: PRDRequest):
    prd_json = request.prd_json
    sector, category, enriched_prd = classify_prd(prd_json)
    search_results = duckduckgo_search(f"{sector} {category} risk 2025")

    result = run_risk_workflow(enriched_prd, sector, category, search_results)
    return result
