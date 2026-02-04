"""
🚀 Trading Bot Web Dashboard - FastAPI Server
Railway.app deployment ready with WebSocket support
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

# Import bot components
from config.config import Config

# Note: Import bots dynamically to avoid startup errors
# from bots.aggressive_recovery_bot import AggressiveRecoveryBot
# from bots.daily_scalping_bot import DailyScalpingBot

# Database (optional - SQLite fallback)
try:
    from database.db import SessionLocal, engine, init_db
    from database.models import Trade, BotConfig as DBBotConfig, User
    DATABASE_AVAILABLE = True
except Exception as e:
    DATABASE_AVAILABLE = False
    print(f"⚠️ Database not initialized: {e}")


# ==================== GLOBAL STATE ====================
bot_instance = None
bot_task = None
bot_status = {
    "running": False,
    "mode": "DEMO" if Config.DEMO_MODE else "LIVE",
    "bot_type": "aggressive",  # or "scalping"
    "uptime": 0,
    "total_trades": 0,
    "profit_loss": 0.0,
    "active_positions": 0,
    "last_update": None
}

# WebSocket connections
active_connections: List[WebSocket] = []

# Logging buffer for WebSocket
import logging
from collections import deque

log_buffer = deque(maxlen=500)  # Keep last 500 logs

class WebSocketLogHandler(logging.Handler):
    """Custom logging handler to send logs via WebSocket"""
    def emit(self, record):
        try:
            log_entry = self.format(record)
            log_buffer.append(log_entry)
            # Don't block here - will be sent by WebSocket manager
        except Exception:
            self.handleError(record)


# ==================== PYDANTIC MODELS ====================
class BotConfig(BaseModel):
    bot_type: str  # "aggressive" or "scalping"
    demo_mode: bool
    max_positions: int
    daily_profit_target: float


class TradeResponse(BaseModel):
    id: int
    symbol: str
    side: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    profit_loss: Optional[float]
    status: str
    timestamp: str


class StartBotRequest(BaseModel):
    bot_type: str = "aggressive"  # "aggressive" or "scalping"


# ==================== LIFESPAN MANAGEMENT ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🚀 Starting Trading Bot Web Server...")
    print(f"📊 Mode: {bot_status['mode']}")
    print(f"🌐 Environment: Local/Cloud")
    
    # Setup WebSocket logging handler
    ws_handler = WebSocketLogHandler()
    ws_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
    ws_handler.setFormatter(formatter)
    
    # Add to root logger
    logging.getLogger().addHandler(ws_handler)
    
    # Startup: Initialize database if available
    if DATABASE_AVAILABLE:
        try:
            init_db()
            print("✅ Database initialized")
        except Exception as e:
            print(f"⚠️ Database init failed: {e}")
    
    yield
    
    # Shutdown: Stop bot gracefully
    if bot_instance and hasattr(bot_instance, 'stop'):
        print("⏹️  Stopping bot gracefully...")
        bot_instance.stop()


# ==================== FASTAPI APP ====================
app = FastAPI(
    title="Binance Trading Bot API",
    description="Professional Trading Bot with Web Dashboard",
    version="3.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ในการใช้งานจริงควร specify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ==================== MOUNT API ROUTERS ====================
# Import and mount authentication and config management routers
try:
    print("[ ] Starting to import routers...")
    from api.auth import router as auth_router
    print("[OK] auth_router imported")
    from api.configs import router as configs_router
    print("[OK] configs_router imported")
    from routers.bot import router as bot_router
    print("[OK] bot_router imported")
    
    app.include_router(auth_router)
    print("[OK] auth_router mounted")
    app.include_router(configs_router)
    print("[OK] configs_router mounted")
    app.include_router(bot_router)
    print("[OK] bot_router mounted")
    print("[SUCCESS] All routers successfully mounted!")
except Exception as e:
    import traceback
    print(f"[ERROR] Failed to mount routers: {e}")
    print(f"[ERROR] Traceback: {traceback.format_exc()}")


# ==================== WEBSOCKET MANAGER ====================
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket connected. Total: {len(self.active_connections)}")
        
        # Send recent logs to new connection
        for log_entry in log_buffer:
            try:
                await websocket.send_json({
                    "type": "log",
                    "message": log_entry
                })
            except:
                pass

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"❌ WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)
    
    async def broadcast_log(self, log_message: str):
        """Broadcast log message to all clients"""
        await self.broadcast({
            "type": "log",
            "message": log_message
        })


manager = ConnectionManager()


# ==================== BACKGROUND TASKS ====================
async def run_bot_background(bot_type: str):
    """Run trading bot in background"""
    global bot_instance, bot_status
    
    try:
        # Import bots here to avoid circular imports
        from bots.aggressive_recovery_bot import AggressiveRecoveryBot
        from bots.daily_scalping_bot import DailyScalpingBot
        
        # Create bot instance
        if bot_type == "aggressive":
            bot_instance = AggressiveRecoveryBot()
        else:
            bot_instance = DailyScalpingBot()
        
        bot_status["running"] = True
        bot_status["bot_type"] = bot_type
        
        # Broadcast start notification
        await manager.broadcast({
            "type": "bot_status",
            "status": "started",
            "bot_type": bot_type
        })
        
        # Run bot in a separate thread to avoid blocking
        import threading
        def run_bot_thread():
            try:
                bot_instance.run()
            except Exception as e:
                print(f"❌ Bot thread error: {e}")
            finally:
                bot_status["running"] = False
        
        bot_thread = threading.Thread(target=run_bot_thread, daemon=True)
        bot_thread.start()
        
        # Keep async task alive
        while bot_status["running"]:
            await asyncio.sleep(1)
        
    except Exception as e:
        print(f"❌ Bot error: {e}")
        import traceback
        traceback.print_exc()
        bot_status["running"] = False
        await manager.broadcast({
            "type": "error",
            "message": str(e)
        })


# ==================== HTML PAGE ROUTES ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect to login page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="0; url=/login">
    </head>
    <body>
        <p>Redirecting to login...</p>
    </body>
    </html>
    """

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login and signup page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Main dashboard page (requires authentication via JS)"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


# ==================== API ENDPOINTS ====================
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading Bot Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .card {
                background: white;
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            h1 { color: white; text-align: center; margin-bottom: 30px; }
            h2 { color: #333; margin-bottom: 16px; }
            .stats { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 16px; 
            }
            .stat-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }
            .stat-value { font-size: 32px; font-weight: bold; }
            .stat-label { font-size: 14px; opacity: 0.9; margin-top: 8px; }
            .btn {
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s;
            }
            .btn-start { background: #10b981; color: white; }
            .btn-stop { background: #ef4444; color: white; }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
            .status { 
                display: inline-block; 
                padding: 6px 12px; 
                border-radius: 20px; 
                font-size: 14px;
                font-weight: 600;
            }
            .status.running { background: #10b981; color: white; }
            .status.stopped { background: #6b7280; color: white; }
            #logs {
                background: #0d1117;
                color: #c9d1d9;
                padding: 16px;
                border-radius: 8px;
                height: 500px;
                overflow-y: auto;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.5;
                border: 1px solid #30363d;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            #logs::-webkit-scrollbar {
                width: 8px;
            }
            #logs::-webkit-scrollbar-track {
                background: #161b22;
            }
            #logs::-webkit-scrollbar-thumb {
                background: #30363d;
                border-radius: 4px;
            }
            #logs::-webkit-scrollbar-thumb:hover {
                background: #484f58;
            }
            .log-success { color: #3fb950; }
            .log-error { color: #f85149; }
            .log-warning { color: #d29922; }
            .log-info { color: #58a6ff; }
            .log-emoji { color: #ffa657; }
            .log-separator { color: #484f58; border-top: 1px solid #21262d; margin: 4px 0; padding-top: 4px; }
            .control-panel { display: flex; gap: 12px; margin-top: 16px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Trading Bot Dashboard</h1>
            
            <div class="card">
                <h2>Bot Status: <span id="bot-status" class="status stopped">STOPPED</span></h2>
                <div class="control-panel">
                    <button class="btn btn-start" onclick="startBot('aggressive')">🔥 Start Aggressive Bot</button>
                    <button class="btn btn-start" onclick="startBot('scalping')">⚡ Start Scalping Bot</button>
                    <button class="btn btn-stop" onclick="stopBot()">⏹️ Stop Bot</button>
                </div>
            </div>
            
            <div class="card">
                <h2>Performance Statistics</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value" id="profit">$0.00</div>
                        <div class="stat-label">Total P&L</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="trades">0</div>
                        <div class="stat-label">Total Trades</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="positions">0</div>
                        <div class="stat-label">Active Positions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="uptime">0h 0m</div>
                        <div class="stat-label">Uptime</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>Live Logs <button class="btn" style="float: right; padding: 6px 12px; font-size: 12px; background: #6b7280;" onclick="clearLogs()">🗑️ Clear</button></h2>
                <div id="logs">Waiting for connection...</div>
            </div>
        </div>
        
        <script>
            let ws = null;
            let reconnectAttempts = 0;
            const maxReconnectAttempts = 5;
            
            function connectWebSocket() {
                try {
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    const wsUrl = `${protocol}//${window.location.host}/ws`;
                    
                    console.log('Connecting to WebSocket:', wsUrl);
                    addLog(`🔌 Connecting to ${wsUrl}...`);
                    
                    ws = new WebSocket(wsUrl);
                    
                    ws.onopen = () => {
                        console.log('WebSocket connected');
                        addLog('✅ Connected to server');
                        reconnectAttempts = 0;
                    };
                    
                    ws.onmessage = (event) => {
                        try {
                            const data = JSON.parse(event.data);
                            console.log('Received:', data);
                            handleMessage(data);
                        } catch (error) {
                            console.error('Message parse error:', error);
                        }
                    };
                    
                    ws.onerror = (error) => {
                        console.error('WebSocket error:', error);
                        addLog('❌ Connection error');
                    };
                    
                    ws.onclose = () => {
                        console.log('WebSocket disconnected');
                        addLog('⚠️ Disconnected. Reconnecting...');
                        
                        if (reconnectAttempts < maxReconnectAttempts) {
                            reconnectAttempts++;
                            setTimeout(connectWebSocket, 3000);
                        } else {
                            addLog('❌ Failed to reconnect after ' + maxReconnectAttempts + ' attempts');
                        }
                    };
                } catch (error) {
                    console.error('WebSocket connection error:', error);
                    addLog('❌ Failed to connect: ' + error.message);
                }
            }
            
            function handleMessage(data) {
                console.log('Handling message type:', data.type);
                
                if (data.type === 'bot_status') {
                    updateBotStatus(data);
                } else if (data.type === 'stats') {
                    updateStats(data);
                } else if (data.type === 'log') {
                    addLog(data.message);
                } else if (data.type === 'error') {
                    addLog('❌ ERROR: ' + data.message);
                } else {
                    console.log('Unknown message type:', data);
                }
            }
            
            function updateBotStatus(data) {
                const statusEl = document.getElementById('bot-status');
                if (data.status === 'started') {
                    statusEl.textContent = 'RUNNING';
                    statusEl.className = 'status running';
                    addLog(`🚀 ${data.bot_type.toUpperCase()} BOT STARTED`);
                } else {
                    statusEl.textContent = 'STOPPED';
                    statusEl.className = 'status stopped';
                    addLog('⏹️ Bot stopped');
                }
            }
            
            function updateStats(data) {
                document.getElementById('profit').textContent = `$${data.profit.toFixed(2)}`;
                document.getElementById('trades').textContent = data.trades;
                document.getElementById('positions').textContent = data.positions;
                document.getElementById('uptime').textContent = data.uptime;
            }
            
            function addLog(message) {
                const logsEl = document.getElementById('logs');
                
                // Clear "Waiting for connection" message on first log
                if (logsEl.textContent.includes('Waiting for connection')) {
                    logsEl.innerHTML = '';
                }
                
                // Apply syntax highlighting
                let formattedMsg = message;
                
                // Color coding for different log types
                if (message.includes('✅') || message.includes('SUCCESS') || message.includes('ENTRY')) {
                    formattedMsg = `<span class="log-success">${escapeHtml(message)}</span>`;
                } else if (message.includes('❌') || message.includes('ERROR') || message.includes('EXIT') || message.includes('SL')) {
                    formattedMsg = `<span class="log-error">${escapeHtml(message)}</span>`;
                } else if (message.includes('⚠️') || message.includes('WARNING') || message.includes('CAUTION')) {
                    formattedMsg = `<span class="log-warning">${escapeHtml(message)}</span>`;
                } else if (message.includes('ℹ️') || message.includes('INFO') || message.includes('Cycle')) {
                    formattedMsg = `<span class="log-info">${escapeHtml(message)}</span>`;
                } else if (message.includes('═') || message.includes('─')) {
                    formattedMsg = `<span class="log-separator">${escapeHtml(message)}</span>`;
                } else {
                    formattedMsg = escapeHtml(message);
                }
                
                logsEl.innerHTML += formattedMsg + '\n';
                logsEl.scrollTop = logsEl.scrollHeight;
                
                // Keep only last 1000 lines
                const lines = logsEl.innerHTML.split('\n');
                if (lines.length > 1000) {
                    logsEl.innerHTML = lines.slice(-1000).join('\n');
                }
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            async function startBot(botType) {
                try {
                    console.log('Starting bot:', botType);
                    addLog(`🚀 Starting ${botType} bot...`);
                    
                    const response = await fetch('/api/bot/start', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ bot_type: botType })
                    });
                    
                    console.log('Response status:', response.status);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    console.log('Response data:', data);
                    addLog('✅ ' + data.message);
                    
                } catch (error) {
                    console.error('Start bot error:', error);
                    addLog(`❌ Error: ${error.message}`);
                    alert('Failed to start bot: ' + error.message);
                }
            }
            
            async function stopBot() {
                try {
                    console.log('Stopping bot...');
                    addLog('🛑 Stopping bot...');
                    
                    const response = await fetch('/api/bot/stop', { method: 'POST' });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    console.log('Stop response:', data);
                    addLog('✅ ' + data.message);
                    
                } catch (error) {
                    console.error('Stop bot error:', error);
                    addLog(`❌ Error: ${error.message}`);
                    alert('Failed to stop bot: ' + error.message);
                }
            }
            
            function clearLogs() {
                document.getElementById('logs').innerHTML = '📝 Logs cleared. Waiting for new messages...\n';
            }
            
            // Connect on page load
            connectWebSocket();
            
            // Update stats every 5 seconds
            setInterval(() => {
                fetch('/api/stats').then(r => r.json()).then(updateStats);
            }, 5000);
        </script>
    </body>
    </html>
    """


@app.get("/api/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": bot_status["mode"]
    }


@app.get("/api/stats")
async def get_stats():
    """Get current bot statistics"""
    return {
        "profit": bot_status["profit_loss"],
        "trades": bot_status["total_trades"],
        "positions": bot_status["active_positions"],
        "uptime": f"{bot_status['uptime']//3600}h {(bot_status['uptime']%3600)//60}m"
    }


@app.post("/api/bot/start")
async def start_bot(request: StartBotRequest, background_tasks: BackgroundTasks):
    """Start the trading bot"""
    global bot_task
    
    if bot_status["running"]:
        raise HTTPException(status_code=400, detail="Bot is already running")
    
    # Run bot in background
    bot_task = asyncio.create_task(run_bot_background(request.bot_type))
    
    return {
        "message": f"{request.bot_type.upper()} bot started successfully",
        "bot_type": request.bot_type,
        "mode": bot_status["mode"]
    }


@app.post("/api/bot/stop")
async def stop_bot():
    """Stop the trading bot"""
    global bot_instance, bot_task
    
    if not bot_status["running"]:
        raise HTTPException(status_code=400, detail="Bot is not running")
    
    # Stop bot
    if bot_instance:
        bot_instance.stop()
        bot_instance = None
    
    if bot_task:
        bot_task.cancel()
        bot_task = None
    
    bot_status["running"] = False
    
    await manager.broadcast({
        "type": "bot_status",
        "status": "stopped"
    })
    
    return {"message": "Bot stopped successfully"}


@app.get("/api/config")
async def get_config():
    """Get current bot configuration"""
    return {
        "demo_mode": Config.DEMO_MODE,
        "max_positions": Config.MAX_TOTAL_POSITIONS,
        "symbols": Config.SYMBOL_POOL,
        "daily_target": Config.DAILY_PROFIT_TARGET
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        last_log_count = len(log_buffer)
        
        while True:
            # Send new logs
            current_log_count = len(log_buffer)
            if current_log_count > last_log_count:
                # Send new logs
                for log_entry in list(log_buffer)[last_log_count:]:
                    await websocket.send_json({
                        "type": "log",
                        "message": log_entry
                    })
                last_log_count = current_log_count
            
            # Keep connection alive and send updates
            await asyncio.sleep(0.5)  # Check more frequently for logs
            bot_status["uptime"] += 1
            
            # Send periodic stats
            if bot_status["uptime"] % 10 == 0:  # Every 5 seconds (0.5s * 10)
                await websocket.send_json({
                    "type": "stats",
                    "profit": bot_status["profit_loss"],
                    "trades": bot_status["total_trades"],
                    "positions": bot_status["active_positions"],
                    "uptime": f"{bot_status['uptime']//7200}h {(bot_status['uptime']//120)%60}m"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ==================== MAIN ====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    print("="*60)
    print("🚀 Starting Trading Bot Web Server")
    print(f"📍 Port: {port}")
    print(f"🌐 Railway Cloud Deployment")
    print("="*60)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable in production
        log_level="info"
    )
