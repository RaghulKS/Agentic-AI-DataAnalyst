import uvicorn
import config

def run_api():
    host = getattr(config, 'API_HOST', '0.0.0.0')
    port = getattr(config, 'API_PORT', 8000)
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    run_api()