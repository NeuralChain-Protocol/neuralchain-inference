# ========================================
# File: api/main.py
# NeuralChain Inference API
# ========================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
import time
from typing import Optional

# Initialize FastAPI app
app = FastAPI(
    title="NeuralChain Inference API",
    description="Decentralized AI inference powered by Solana",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI model (sentiment analysis)
print("Loading AI model...")
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)
print("Model loaded successfully!")

# Request/Response models
class AnalysisRequest(BaseModel):
    text: str
    wallet_address: Optional[str] = None

class AnalysisResponse(BaseModel):
    sentiment: str
    confidence: float
    cost_sol: float
    processing_time: float
    transaction_id: Optional[str] = None

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "NeuralChain Inference API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "analyze": "/api/v1/analyze",
            "health": "/health",
            "docs": "/docs"
        }
    }

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": True,
        "timestamp": time.time()
    }

# Main inference endpoint
@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_sentiment(request: AnalysisRequest):
    """
    Analyze sentiment of text using AI model
    
    - **text**: Text to analyze
    - **wallet_address**: Optional Solana wallet address for payment
    """
    try:
        start_time = time.time()
        
        # Validate input
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 1000:
            raise HTTPException(
                status_code=400, 
                detail="Text too long. Maximum 1000 characters"
            )
        
        # Run AI inference
        result = sentiment_analyzer(request.text)[0]
        
        # Calculate cost (0.001 SOL per request)
        cost = 0.001
        
        # Mock transaction ID (in production, this would be real Solana tx)
        tx_id = f"mock_tx_{int(time.time() * 1000)}" if request.wallet_address else None
        
        processing_time = time.time() - start_time
        
        return AnalysisResponse(
            sentiment=result['label'].lower(),
            confidence=round(result['score'], 4),
            cost_sol=cost,
            processing_time=round(processing_time, 3),
            transaction_id=tx_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Batch analysis endpoint
@app.post("/api/v1/analyze/batch")
async def analyze_batch(texts: list[str], wallet_address: Optional[str] = None):
    """
    Analyze multiple texts in batch
    """
    if len(texts) > 10:
        raise HTTPException(
            status_code=400, 
            detail="Maximum 10 texts per batch"
        )
    
    results = []
    for text in texts:
        request = AnalysisRequest(text=text, wallet_address=wallet_address)
        result = await analyze_sentiment(request)
        results.append(result)
    
    return {
        "results": results,
        "total_cost_sol": sum(r.cost_sol for r in results),
        "count": len(results)
    }

# Model information
@app.get("/api/v1/model/info")
async def model_info():
    return {
        "name": "DistilBERT Sentiment Analysis",
        "type": "Text Classification",
        "languages": ["English"],
        "max_length": 512,
        "accuracy": 0.91,
        "cost_per_inference": 0.001,
        "average_latency_ms": 200
    }

# Pricing information
@app.get("/api/v1/pricing")
async def pricing():
    return {
        "sentiment_analysis": {
            "cost_sol": 0.001,
            "cost_usd": 0.15,  # Approximate
            "response_time_ms": 200
        },
        "batch_discount": {
            "10_requests": "5% off",
            "100_requests": "10% off",
            "1000_requests": "20% off"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
