from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import sys
from dotenv import load_dotenv
import json

load_dotenv()

PROJECT_ROOT = r"C:\Users\deepa\OneDrive\Desktop\engagement-risk-platform"

sys.path.append(os.path.join(PROJECT_ROOT, "app", "database"))

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

try:
    from vector_db import PlayerVectorDB
    vector_db = PlayerVectorDB()
    print("Vector DB initialized.")
except Exception as e:
    print(f"Vector DB not available: {e}")
    vector_db = None

app = FastAPI(title="Risk Intelligence Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_data():
    try:
        users_path = os.path.join(PROJECT_ROOT, "app", "data", "users.csv")
        trans_path = os.path.join(PROJECT_ROOT, "app", "data", "transactions.csv")
        
        users_df = pd.read_csv(users_path)
        trans_df = pd.read_csv(trans_path)
        
        users_df = users_df.replace({float('nan'): None})
        trans_df = trans_df.replace({float('nan'): None})
        
        print(f"Loaded {len(users_df)} users, {len(trans_df)} transactions")
        return users_df, trans_df
    except Exception as e:
        print(f"ERROR: {e}")
        return None, None

users_df, transactions_df = load_data()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    try:
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7, api_key=GROQ_API_KEY)
        print("Groq LLM ready.")
    except Exception as e:
        print(f"Groq error: {e}")
        llm = None
else:
    llm = None
    print("GROQ_API_KEY not set.")

class RecommendationRequest(BaseModel):
    user_id: int

class RecommendationResponse(BaseModel):
    user_id: int
    risk_level: str
    recommendation: str
    intervention_strategy: str

@app.get("/")
async def root():
    return {"message": "Risk Intelligence Platform API", "status": "running"}

@app.get("/users")
async def get_users():
    if users_df is None:
        return {"error": "Data not loaded"}
    try:
        return users_df.to_dict(orient='records')
    except Exception as e:
        print(f"Error in /users: {e}")
        return {"error": str(e)}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if users_df is None:
        return {"error": "Data not loaded"}
    user = users_df[users_df['user_id'] == user_id]
    if user.empty:
        raise HTTPException(status_code=404, detail="User not found")
    return user.iloc[0].to_dict()

@app.get("/users/risk/high")
async def get_high_risk_users():
    if users_df is None:
        return {"error": "Data not loaded"}
    high_risk = users_df[users_df['risk_level'] == 'High']
    return high_risk.to_dict(orient='records')

@app.get("/stats")
async def get_stats():
    if users_df is None:
        return {"error": "Data not loaded"}
    return {
        "total_users": len(users_df),
        "risk_levels": users_df['risk_level'].value_counts().to_dict(),
        "avg_risk_score": round(users_df['risk_score'].mean(), 2),
        "avg_spend": round(users_df['total_spend'].mean(), 2),
        "total_transactions": len(transactions_df) if transactions_df is not None else 0
    }

@app.get("/demographics")
async def get_demographics():
    if users_df is None:
        return {"error": "Data not loaded"}
    try:
        demo_data = users_df[['state', 'median_income']].drop_duplicates().to_dict(orient='records')
        return {
            "states": demo_data,
            "total_users": len(users_df),
            "avg_income": round(users_df['median_income'].mean(), 2)
        }
    except Exception as e:
        print(f"Error in /demographics: {e}")
        return {"error": str(e)}

@app.post("/search/semantic")
async def semantic_search(request: dict):
    """
    Semantic search with automatic filter detection for:
    - Risk Level: high-risk, medium-risk, low-risk
    - Segment: casual, regular, frequent, high-value, vip
    - State: any US state name
    - Age: young, old, age range
    - Spend: high-spend, low-spend
    """
    query = request.get("query", "")
    n_results = request.get("n_results", 10)
    
    # Explicit filters from frontend dropdowns
    risk_level = request.get("risk_level", None)
    segment = request.get("segment", None)
    
    if not query:
        return {"error": "Query is required"}
    
    if vector_db is None:
        return {"error": "Vector database is not available"}
    
    try:
        query_lower = query.lower()
        
        # Build metadata filters
        filters = {}
        
        # 1. RISK LEVEL DETECTION
        if risk_level:
            filters['risk_level'] = risk_level
        else:
            if "high-risk" in query_lower or "high risk" in query_lower:
                filters['risk_level'] = "High"
            elif "medium-risk" in query_lower or "medium risk" in query_lower:
                filters['risk_level'] = "Medium"
            elif "low-risk" in query_lower or "low risk" in query_lower:
                filters['risk_level'] = "Low"
        
        # 2. SEGMENT DETECTION
        if segment:
            filters['segment'] = segment
        else:
            if "high-value" in query_lower or "high value" in query_lower:
                filters['segment'] = "High-Value"
            elif "vip" in query_lower:
                filters['segment'] = "VIP"
            elif "frequent" in query_lower:
                filters['segment'] = "Frequent"
            elif "regular" in query_lower:
                filters['segment'] = "Regular"
            elif "casual" in query_lower:
                filters['segment'] = "Casual"
        
        # 3. STATE DETECTION
        if users_df is not None:
            all_states = users_df['state'].unique().tolist()
            detected_state = None
            for state in all_states:
                if state.lower() in query_lower:
                    detected_state = state
                    break
            
            if detected_state:
                filters['state'] = detected_state
        
        # Perform search with filters
        if filters:
            print(f"Applying filters: {filters}")
            results = vector_db.search_with_filters(query, n_results, filters=filters)
        else:
            print(f"No filters applied")
            results = vector_db.search(query, n_results)
        
        players = []
        for meta in results['metadatas'][0]:
            players.append({
                'user_id': meta['user_id'],
                'age': meta['age'],
                'state': meta['state'],
                'segment': meta['segment'],
                'total_spend': meta['total_spend'],
                'visit_frequency': meta['visit_frequency'],
                'risk_score': meta['risk_score'],
                'risk_level': meta['risk_level']
            })
        
        return {
            "results": players,
            "query": query,
            "filters_applied": filters,
            "total_found": len(players)
        }
    except Exception as e:
        print(f"Search error: {e}")
        return {"error": str(e)}

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendation(request: RecommendationRequest):
    user_id = request.user_id
    if users_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    user = users_df[users_df['user_id'] == user_id]
    if user.empty:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.iloc[0]

    if llm is None:
        return RecommendationResponse(
            user_id=user_id,
            risk_level=user_data['risk_level'],
            recommendation="LLM not available. Please check GROQ_API_KEY.",
            intervention_strategy="Manual review recommended."
        )

    prompt = PromptTemplate(
        input_variables=["age", "state", "risk_level", "risk_score", "total_spend", "visit_frequency", "segment", "game_types"],
        template="""You are a responsible engagement analyst. A user has been flagged for risk monitoring.
        
        User Profile:
        - Age: {age}
        - State: {state}
        - Risk Level: {risk_level}
        - Risk Score: {risk_score}/100
        - Total Spend: ${total_spend}
        - Days Since Last Visit: {visit_frequency}
        - Segment: {segment}
        - Game Types: {game_types}
        
        Based on this profile, provide:
        1. A brief recommendation (1 sentence) explaining the risk.
        2. A detailed intervention strategy (2-3 sentences).
        
        Format:
        RECOMMENDATION: ...
        INTERVENTION: ..."""
    )
    
    chain = prompt | llm | StrOutputParser()
    try:
        response = chain.invoke({
            "age": user_data['age'],
            "state": user_data['state'],
            "risk_level": user_data['risk_level'],
            "risk_score": user_data['risk_score'],
            "total_spend": user_data['total_spend'],
            "visit_frequency": user_data['visit_frequency'],
            "segment": user_data['segment'],
            "game_types": user_data['game_types']
        })
        rec = ""
        inter = ""
        if "RECOMMENDATION:" in response:
            parts = response.split("INTERVENTION:")
            rec = parts[0].replace("RECOMMENDATION:", "").strip()
            inter = parts[1].strip() if len(parts) > 1 else ""
        if not rec:
            rec = response[:200]
            inter = response[200:400] if len(response) > 200 else "Follow up."
    except Exception as e:
        rec = f"Error: {str(e)}"
        inter = "Please check the model or API key."

    return RecommendationResponse(
        user_id=user_id,
        risk_level=user_data['risk_level'],
        recommendation=rec,
        intervention_strategy=inter
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)