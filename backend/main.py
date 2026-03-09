from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
from typing import Dict, Any
import logging
from diagnostics.ping_test import PingTest
from diagnostics.dns_test import DNSTest
from diagnostics.packet_loss import PacketLossTest
from diagnostics.speed_test import SpeedTestDiagnostic
from analysis.root_cause_engine import RootCauseAnalyzer
from fastapi.responses import StreamingResponse
from utils.report_generator import generate_pdf_report
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
import uuid
from fastapi import Body

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FixMyInternet API",
    description="Network Diagnostics and Analysis Tool",
    version="1.0.0"
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NetworkDiagnostics:
    def __init__(self):
        self.ping_test = PingTest()
        self.dns_test = DNSTest()
        self.packet_loss_test = PacketLossTest()
        self.speed_test = SpeedTestDiagnostic()
        self.analyzer = RootCauseAnalyzer()
    
    async def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete network diagnostics"""
        results = {}
        
        try:
            # Run tests concurrently where possible
            logger.info("Starting network diagnostics...")
            
            # Latency test
            logger.info("Running latency test...")
            results['latency'] = await asyncio.to_thread(self.ping_test.run_test)
            
            # DNS test  
            logger.info("Running DNS test...")
            results['dns'] = await asyncio.to_thread(self.dns_test.run_test)
            
            # Packet loss test
            logger.info("Running packet loss test...")
            results['packet_loss'] = await asyncio.to_thread(self.packet_loss_test.run_test)
            
            # Speed test (usually takes longer)
            logger.info("Running speed test...")
            results['speed'] = await asyncio.to_thread(self.speed_test.run_test)
            
            # Analyze results
            logger.info("Analyzing results...")
            analysis = self.analyzer.analyze(results)
            
            return {
                'speed': results['speed'],
                'latency': results['latency'],
                'dns': results['dns'],
                'packet_loss': results['packet_loss'],
                'analysis': analysis,
                'timestamp': asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Diagnostic error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
diagnostics = NetworkDiagnostics()
reports_store = {}

@app.get("/")
async def root():
    return {"message": "FixMyInternet API - Network Diagnostics Tool"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/diagnostics/full-analysis")
@limiter.limit("10/minute")
async def full_analysis(request: Request):
    """Run complete network analysis"""
    try:
        results = await diagnostics.run_full_analysis()
        return JSONResponse(content=results)
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/diagnostics/export-pdf")
async def export_pdf(request: Request):
    data = await request.json()
    pdf = generate_pdf_report(data)

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=fixmyinternet-report.pdf"
        },
    )

@app.post("/diagnostics/share")
async def share_report(data: Dict[str, Any] = Body(...)):
    report_id = str(uuid.uuid4())[:8]
    reports_store[report_id] = data

    return {
        "share_url": f"/report/{report_id}"
    }

@app.get("/report/{report_id}")
async def get_shared_report(report_id: str):
    if report_id not in reports_store:
        raise HTTPException(status_code=404, detail="Report not found")

    return reports_store[report_id]