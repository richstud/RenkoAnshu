import { jsxs as _jsxs, jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect, useRef } from 'react';
export default function RenkoChart({ symbol: initialSymbol, brickSize: initialBrickSize, accountId, onAddToWatchlist }) {
    const [symbol, setSymbol] = useState(initialSymbol || 'GOLD');
    // Use symbol-aware default brick size: Gold/XAUUSD → 5.0, JPY pairs → 0.05, everything else → 0.005
    const getDefaultBrickSize = (sym) => {
        const s = sym.toUpperCase();
        if (s === 'GOLD' || s === 'XAUUSD')
            return 5.0;
        if (s === 'BTCUSD' || s === 'BITCOIN')
            return 100.0;
        if (s.includes('JPY'))
            return 0.05;
        return 0.005;
    };
    const [brickSize, setBrickSize] = useState(initialBrickSize || getDefaultBrickSize(initialSymbol || 'GOLD'));
    const [timeframe, setTimeframe] = useState(1); // 1 or 5 minutes
    const [bricks, setBricks] = useState([]);
    const [currentPrice, setCurrentPrice] = useState(0);
    const [bid, setBid] = useState(0);
    const [ask, setAsk] = useState(0);
    const [loading, setLoading] = useState(true);
    const [calculating, setCalculating] = useState(false); // Show when Renko calc in progress
    const [error, setError] = useState(null);
    const [availableSymbols, setAvailableSymbols] = useState([]);
    const [chartData, setChartData] = useState({ symbol: '', brick_size: 0, current_direction: 'long', total_bricks: 0 });
    const canvasRef = useRef(null);
    const bricksRef = useRef([]);
    const priceRef = useRef(0);
    const bidRef = useRef(0);
    const askRef = useRef(0);
    const wsRef = useRef(null);
    const reconnectTimerRef = useRef(0);
    const reconnectDelayRef = useRef(1000);
    // Refs for crosshair - using refs avoids destroying/recreating the draw interval on every mouse move
    const mousePosRef = useRef(null);
    const crosshairPriceRef = useRef(null);
    const crosshairTimeRef = useRef(null); // Unix timestamp at crosshair X position
    const showCrosshairRef = useRef(false);
    const [symbolSearch, setSymbolSearch] = useState('');
    const [showDropdown, setShowDropdown] = useState(false);
    const [addedToWatchlist, setAddedToWatchlist] = useState(null);
    const filteredSymbols = availableSymbols.filter(s => s.toLowerCase().includes(symbolSearch.toLowerCase())).slice(0, 30);
    // Fetch ALL available symbols from MT5 on mount
    useEffect(() => {
        const fetchSymbols = async () => {
            try {
                const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/mt5/symbols`);
                if (res.ok) {
                    const data = await res.json();
                    const symbols = data.symbols || [];
                    setAvailableSymbols(symbols);
                }
            }
            catch (err) {
                console.error('Failed to fetch symbols:', err);
                // Fallback to tickers endpoint
                try {
                    const res2 = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/tickers`);
                    if (res2.ok) {
                        const response = await res2.json();
                        const tickers = response.data || response;
                        setAvailableSymbols(tickers.map((t) => t.symbol));
                    }
                }
                catch { }
            }
        };
        fetchSymbols();
    }, []);
    // Update symbol and reset brick size to symbol-appropriate default when prop changes
    useEffect(() => {
        setSymbol(initialSymbol);
        if (!initialBrickSize) {
            setBrickSize(getDefaultBrickSize(initialSymbol));
        }
    }, [initialSymbol]);
    // WebSocket-based chart streaming — replaces REST polling + bid/ask polling
    useEffect(() => {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const WS_BASE = API_URL.replace(/^https/, 'wss').replace(/^http/, 'ws');
        const url = `${WS_BASE}/api/renko/stream/${symbol}?brick_size=${brickSize}`;
        reconnectDelayRef.current = 1000;
        // `active` flag prevents the old onclose from scheduling a reconnect
        // after the effect cleanup intentionally closes the socket (e.g. when
        // brick_size or symbol changes). Without this flag, the old closure races
        // with the new effect, reopening a socket with the OLD brick_size.
        let active = true;
        const connect = () => {
            if (!active)
                return;
            const ws = new WebSocket(url);
            wsRef.current = ws;
            ws.onopen = () => {
                setError(null);
                setLoading(true);
                reconnectDelayRef.current = 1000;
            };
            ws.onmessage = (event) => {
                if (!active)
                    return;
                try {
                    const data = JSON.parse(event.data);
                    if (data.error) {
                        setError(data.error);
                        setLoading(false);
                        return;
                    }
                    // Stop loading on ANY valid message from server
                    setLoading(false);
                    if (data.bid) {
                        bidRef.current = data.bid;
                        setBid(data.bid);
                    }
                    if (data.ask) {
                        askRef.current = data.ask;
                        setAsk(data.ask);
                    }
                    if (data.current_price) {
                        priceRef.current = data.current_price;
                        setCurrentPrice(data.current_price);
                    }
                    if (data.bricks && data.bricks.length > 0) {
                        bricksRef.current = data.bricks;
                        setBricks(data.bricks);
                        setCalculating(false);
                        setChartData({
                            symbol: data.symbol || symbol,
                            // Use server-provided brick_size if valid, else keep the user-set value
                            brick_size: (data.brick_size && data.brick_size > 0) ? data.brick_size : brickSize,
                            current_direction: data.current_direction || 'long',
                            total_bricks: data.total_bricks || data.bricks.length,
                        });
                    }
                }
                catch { /* ignore parse errors */ }
            };
            ws.onclose = () => {
                if (!active)
                    return; // intentional close — don't reconnect
                reconnectTimerRef.current = window.setTimeout(() => {
                    reconnectDelayRef.current = Math.min(reconnectDelayRef.current * 1.5, 8000);
                    connect();
                }, reconnectDelayRef.current);
            };
            ws.onerror = () => { };
        };
        setLoading(true);
        setBricks([]);
        bricksRef.current = [];
        connect();
        return () => {
            active = false; // prevent onclose from triggering reconnect
            clearTimeout(reconnectTimerRef.current);
            wsRef.current?.close();
            wsRef.current = null;
        };
    }, [symbol, brickSize, timeframe]);
    // Canvas drawing - uses refs so it redraws WITHOUT state updates
    useEffect(() => {
        const drawChart = () => {
            if (!canvasRef.current || bricksRef.current.length === 0)
                return;
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');
            if (!ctx)
                return;
            // Set canvas size - CRITICAL for proper rendering
            const rect = canvas.parentElement?.getBoundingClientRect();
            if (rect && (canvas.width !== rect.width || canvas.height !== rect.height)) {
                canvas.width = rect.width;
                canvas.height = rect.height;
            }
            const width = canvas.width;
            const height = canvas.height;
            if (width === 0 || height === 0)
                return;
            const leftPadding = 80;
            const rightPadding = 30;
            const topPadding = 50;
            const bottomPadding = 50;
            const chartWidth = width - leftPadding - rightPadding;
            const chartHeight = height - topPadding - bottomPadding;
            // Clear with dark background
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(0, 0, width, height);
            const bricks = bricksRef.current;
            if (bricks.length === 0)
                return;
            // Get all prices for scaling
            const allPrices = bricks.flatMap(b => [b.open, b.close, b.high, b.low]);
            const minPrice = Math.min(...allPrices);
            const maxPrice = Math.max(...allPrices);
            const priceRange = maxPrice - minPrice;
            // Add 5% padding
            const pricePadding = priceRange * 0.05;
            const chartMinPrice = minPrice - pricePadding;
            const chartMaxPrice = maxPrice + pricePadding;
            const chartPriceRange = chartMaxPrice - chartMinPrice;
            // Price to Y coordinate
            const priceToY = (price) => {
                return height - bottomPadding - ((price - chartMinPrice) / chartPriceRange) * chartHeight;
            };
            const bricksToShow = Math.min(bricks.length, 100);
            const visibleBricks = bricks.slice(-bricksToShow);
            const brickWidth = chartWidth / bricksToShow * 0.85;
            const brickSpacing = chartWidth / bricksToShow;
            // ===== Draw Grid =====
            ctx.strokeStyle = '#1e293b';
            ctx.lineWidth = 1;
            ctx.setLineDash([4, 4]);
            const gridLines = 10;
            for (let i = 0; i <= gridLines; i++) {
                const price = chartMinPrice + (chartPriceRange / gridLines) * i;
                const y = priceToY(price);
                ctx.beginPath();
                ctx.moveTo(leftPadding, y);
                ctx.lineTo(width - rightPadding, y);
                ctx.stroke();
                ctx.setLineDash([]);
                ctx.fillStyle = '#94a3b8';
                ctx.font = '11px "Segoe UI", Arial';
                ctx.textAlign = 'right';
                ctx.textBaseline = 'middle';
                ctx.fillText(price.toFixed(price < 100 ? 3 : 2), leftPadding - 12, y);
                ctx.setLineDash([4, 4]);
            }
            ctx.setLineDash([]);
            // Draw axes
            ctx.strokeStyle = '#334155';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(leftPadding, topPadding);
            ctx.lineTo(leftPadding, height - bottomPadding);
            ctx.lineTo(width - rightPadding, height - bottomPadding);
            ctx.stroke();
            // IST timezone label on X-axis
            ctx.fillStyle = '#475569';
            ctx.font = '9px "Segoe UI", Arial';
            ctx.textAlign = 'right';
            ctx.textBaseline = 'bottom';
            ctx.fillText('IST (UTC+5:30)', width - rightPadding, height - 2);
            // ===== Draw X-axis Time Labels =====
            ctx.fillStyle = '#64748b';
            ctx.font = '10px "Segoe UI", Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            const labelEvery = Math.max(1, Math.floor(bricksToShow / 8)); // ~8 labels max
            for (let idx = 0; idx < visibleBricks.length; idx += labelEvery) {
                const brick = visibleBricks[idx];
                if (!brick.time)
                    continue;
                const xCenter = leftPadding + (idx * brickSpacing) + brickSpacing / 2;
                const label = new Date(brick.time * 1000).toLocaleTimeString('en-IN', {
                    hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'Asia/Kolkata'
                });
                ctx.fillText(label, xCenter, height - bottomPadding + 6);
            }
            // ===== Draw Bricks =====
            visibleBricks.forEach((brick, idx) => {
                const xStart = leftPadding + (idx * brickSpacing) + (brickSpacing - brickWidth) / 2;
                const openY = priceToY(brick.open);
                const closeY = priceToY(brick.close);
                const highY = priceToY(brick.high);
                const lowY = priceToY(brick.low);
                const isBullish = brick.color === 'green';
                const mainColor = isBullish ? '#10b981' : '#ef4444';
                const outlineColor = isBullish ? '#047857' : '#b91c1c';
                const wickColor = isBullish ? '#059669' : '#dc2626';
                // Wick
                ctx.strokeStyle = wickColor;
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.moveTo(xStart + brickWidth / 2, highY);
                ctx.lineTo(xStart + brickWidth / 2, lowY);
                ctx.stroke();
                // Body
                const bodyTop = Math.min(openY, closeY);
                const bodyBottom = Math.max(openY, closeY);
                const bodyHeight = Math.max(bodyBottom - bodyTop, 2);
                ctx.fillStyle = mainColor;
                ctx.fillRect(xStart, bodyTop, brickWidth, bodyHeight);
                ctx.strokeStyle = outlineColor;
                ctx.lineWidth = 1.5;
                ctx.strokeRect(xStart, bodyTop, brickWidth, bodyHeight);
            });
            // ===== Draw Info =====
            const lastBrick = bricks[bricks.length - 1];
            const isBullish = lastBrick.color === 'green';
            const direction = isBullish ? '▲' : '▼';
            const directionColor = isBullish ? '#10b981' : '#ef4444';
            ctx.fillStyle = '#f1f5f9';
            ctx.font = 'bold 20px "Segoe UI", Arial';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'top';
            ctx.fillText(`${symbol} - Renko`, leftPadding, 10);
            ctx.fillStyle = directionColor;
            ctx.font = 'bold 28px "Segoe UI", Arial';
            ctx.fillText(`${direction} $${priceRef.current.toFixed(priceRef.current < 100 ? 2 : 2)}`, leftPadding, 32);
            const infoBoxX = width - rightPadding - 220;
            const infoBoxY = topPadding;
            const boxWidth = 210;
            const boxHeight = 60;
            ctx.fillStyle = 'rgba(30, 41, 59, 0.9)';
            ctx.fillRect(infoBoxX, infoBoxY, boxWidth, boxHeight);
            ctx.strokeStyle = '#475569';
            ctx.lineWidth = 1;
            ctx.strokeRect(infoBoxX, infoBoxY, boxWidth, boxHeight);
            ctx.fillStyle = '#cbd5e1';
            ctx.font = '12px "Segoe UI", Arial';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'top';
            ctx.fillText(`Brick: $${chartData.brick_size}`, infoBoxX + 10, infoBoxY + 8);
            ctx.fillText(`Total Bricks: ${chartData.total_bricks}`, infoBoxX + 10, infoBoxY + 27);
            ctx.fillText(`Trend: ${isBullish ? 'UPTREND' : 'DOWNTREND'}`, infoBoxX + 10, infoBoxY + 46);
            ctx.fillStyle = directionColor;
            ctx.font = 'bold 12px "Segoe UI", Arial';
            ctx.textAlign = 'right';
            ctx.fillText(isBullish ? 'LONG' : 'SHORT', infoBoxX + boxWidth - 10, infoBoxY + 46);
            // ===== Draw Crosshair =====
            if (showCrosshairRef.current && mousePosRef.current) {
                const { x, y } = mousePosRef.current;
                // Vertical line
                ctx.strokeStyle = 'rgba(248, 113, 113, 0.6)';
                ctx.lineWidth = 1;
                ctx.setLineDash([4, 4]);
                ctx.beginPath();
                ctx.moveTo(x, topPadding);
                ctx.lineTo(x, height - bottomPadding);
                ctx.stroke();
                // Horizontal line
                ctx.strokeStyle = 'rgba(34, 197, 94, 0.6)';
                ctx.beginPath();
                ctx.moveTo(leftPadding, y);
                ctx.lineTo(width - rightPadding, y);
                ctx.stroke();
                ctx.setLineDash([]);
                // Crosshair center point
                ctx.fillStyle = '#fbbf24';
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, Math.PI * 2);
                ctx.fill();
                // Price label on Y-axis (right side)
                if (crosshairPriceRef.current !== null) {
                    const priceText = crosshairPriceRef.current.toFixed(crosshairPriceRef.current < 100 ? 5 : 2);
                    ctx.fillStyle = 'rgba(59, 130, 246, 0.95)';
                    ctx.fillRect(width - rightPadding + 5, y - 12, 75, 24);
                    ctx.strokeStyle = '#3b82f6';
                    ctx.lineWidth = 1;
                    ctx.strokeRect(width - rightPadding + 5, y - 12, 75, 24);
                    ctx.fillStyle = '#ffffff';
                    ctx.font = 'bold 11px "Segoe UI", Arial';
                    ctx.textAlign = 'left';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(priceText, width - rightPadding + 10, y);
                }
                // Price label on Y-axis (left side)
                if (crosshairPriceRef.current !== null) {
                    const priceText = crosshairPriceRef.current.toFixed(crosshairPriceRef.current < 100 ? 5 : 2);
                    ctx.fillStyle = 'rgba(59, 130, 246, 0.95)';
                    ctx.fillRect(leftPadding - 78, y - 12, 75, 24);
                    ctx.strokeStyle = '#3b82f6';
                    ctx.lineWidth = 1;
                    ctx.strokeRect(leftPadding - 78, y - 12, 75, 24);
                    ctx.fillStyle = '#ffffff';
                    ctx.font = 'bold 11px "Segoe UI", Arial';
                    ctx.textAlign = 'right';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(priceText, leftPadding - 8, y);
                }
                // Time label on X-axis (bottom) — show timestamp of hovered brick
                const brickIdx = Math.floor((x - leftPadding) / brickSpacing);
                if (brickIdx >= 0 && brickIdx < visibleBricks.length) {
                    const hoveredBrick = visibleBricks[brickIdx];
                    const timeLabel = hoveredBrick.time
                        ? new Date(hoveredBrick.time * 1000).toLocaleTimeString('en-IN', {
                            hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false, timeZone: 'Asia/Kolkata'
                        })
                        : `#${bricks.length - bricksToShow + brickIdx + 1}`;
                    const labelW = hoveredBrick.time ? 70 : 50;
                    ctx.fillStyle = 'rgba(59, 130, 246, 0.95)';
                    ctx.fillRect(x - labelW / 2, height - bottomPadding + 5, labelW, 22);
                    ctx.strokeStyle = '#3b82f6';
                    ctx.lineWidth = 1;
                    ctx.strokeRect(x - labelW / 2, height - bottomPadding + 5, labelW, 22);
                    ctx.fillStyle = '#ffffff';
                    ctx.font = 'bold 10px "Segoe UI", Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(timeLabel, x, height - bottomPadding + 16);
                }
            }
        };
        // Draw continuously
        const animationFrame = setInterval(drawChart, 100);
        return () => clearInterval(animationFrame);
    }, [symbol, loading, chartData.brick_size, chartData.total_bricks]);
    // Mouse movement handler for crosshair — uses polling to attach once canvas is available
    useEffect(() => {
        let attached = false;
        let pollTimer = null;
        const handleMouseMove = (e) => {
            const canvas = canvasRef.current;
            if (!canvas)
                return;
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;
            mousePosRef.current = { x, y };
            if (bricksRef.current.length > 0) {
                const bricks = bricksRef.current;
                const allPrices = bricks.flatMap(b => [b.open, b.close, b.high, b.low]);
                const minPrice = Math.min(...allPrices);
                const maxPrice = Math.max(...allPrices);
                const priceRange = maxPrice - minPrice;
                const pricePadding = priceRange * 0.05;
                const chartMinPrice = minPrice - pricePadding;
                const chartMaxPrice = maxPrice + pricePadding;
                const chartPriceRange = chartMaxPrice - chartMinPrice;
                const canvasHeight = canvas.height;
                const bottomPadding = 50;
                const topPadding = 50;
                const chartHeight = canvasHeight - topPadding - bottomPadding;
                const price = chartMinPrice + ((canvasHeight - bottomPadding - y) / chartHeight) * chartPriceRange;
                crosshairPriceRef.current = price;
            }
        };
        const handleMouseEnter = () => { showCrosshairRef.current = true; };
        const handleMouseLeave = () => {
            showCrosshairRef.current = false;
            mousePosRef.current = null;
            crosshairPriceRef.current = null;
        };
        const attach = () => {
            const canvas = canvasRef.current;
            if (!canvas)
                return false;
            canvas.addEventListener('mousemove', handleMouseMove);
            canvas.addEventListener('mouseenter', handleMouseEnter);
            canvas.addEventListener('mouseleave', handleMouseLeave);
            return true;
        };
        // Try immediately, then poll every 100ms until canvas is in DOM
        if (!attach()) {
            pollTimer = setInterval(() => {
                if (attach()) {
                    attached = true;
                    if (pollTimer)
                        clearInterval(pollTimer);
                }
            }, 100);
        }
        else {
            attached = true;
        }
        return () => {
            if (pollTimer)
                clearInterval(pollTimer);
            const canvas = canvasRef.current;
            if (canvas) {
                canvas.removeEventListener('mousemove', handleMouseMove);
                canvas.removeEventListener('mouseenter', handleMouseEnter);
                canvas.removeEventListener('mouseleave', handleMouseLeave);
            }
            // Reset crosshair state when symbol changes
            showCrosshairRef.current = false;
            mousePosRef.current = null;
            crosshairPriceRef.current = null;
        };
    }, [symbol, loading]); // Re-attach on symbol change and after loading completes
    if (false) {
        // Error display is now inline inside the chart area - keeping this block for structure only
        return null;
    }
    return (_jsxs("div", { className: "bg-slate-900 rounded-lg border border-slate-700 overflow-hidden", children: [_jsxs("div", { className: "p-4 bg-slate-800 border-b border-slate-700 grid grid-cols-4 gap-3", children: [_jsxs("div", { className: "relative", children: [_jsxs("label", { className: "text-xs text-slate-400 block mb-1", children: ["Symbol (", availableSymbols.length, " available)"] }), _jsx("input", { type: "text", value: symbolSearch || symbol, onChange: (e) => {
                                    setSymbolSearch(e.target.value);
                                    setShowDropdown(true);
                                }, onFocus: () => {
                                    setSymbolSearch('');
                                    setShowDropdown(true);
                                }, placeholder: "Search symbol...", className: "w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white text-sm focus:outline-none focus:border-emerald-500" }), showDropdown && filteredSymbols.length > 0 && (_jsx("div", { className: "absolute z-50 w-full mt-1 bg-slate-700 border border-slate-600 rounded shadow-xl max-h-56 overflow-y-auto", children: filteredSymbols.map(s => (_jsx("div", { onClick: () => {
                                        setSymbol(s);
                                        setBrickSize(getDefaultBrickSize(s));
                                        setSymbolSearch('');
                                        setShowDropdown(false);
                                        setAddedToWatchlist(null);
                                        setLoading(true);
                                    }, className: `px-3 py-2 cursor-pointer text-sm hover:bg-slate-600 ${s === symbol ? 'bg-emerald-900/50 text-emerald-300' : 'text-white'}`, children: s }, s))) })), showDropdown && (_jsx("div", { className: "fixed inset-0 z-40", onClick: () => setShowDropdown(false) }))] }), _jsxs("div", { children: [_jsx("label", { className: "text-xs text-slate-400 block mb-1", children: "Brick Size" }), _jsx("input", { type: "number", value: brickSize, onChange: (e) => {
                                    const val = parseFloat(e.target.value);
                                    if (!isNaN(val) && val > 0)
                                        setBrickSize(val);
                                }, onBlur: (e) => {
                                    // Only reconnect WebSocket on blur (not on every keystroke)
                                    const val = parseFloat(e.target.value);
                                    if (!isNaN(val) && val > 0) {
                                        setBrickSize(val);
                                        setLoading(true);
                                    }
                                }, step: brickSize >= 1 ? "1" : "0.001", min: "0.0001", max: "10000", className: "w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white text-sm focus:outline-none focus:border-emerald-500", placeholder: String(getDefaultBrickSize(symbol)) })] }), _jsxs("div", { children: [_jsx("label", { className: "text-xs text-slate-400 block mb-1", children: "Timeframe" }), _jsxs("div", { className: "flex gap-2", children: [_jsx("button", { onClick: () => {
                                            setTimeframe(1);
                                            setLoading(true);
                                        }, className: `flex-1 px-3 py-2 rounded text-sm font-medium transition ${timeframe === 1
                                            ? 'bg-emerald-600 text-white border border-emerald-500'
                                            : 'bg-slate-700 text-slate-300 border border-slate-600 hover:border-slate-500'}`, children: "1M" }), _jsx("button", { onClick: () => {
                                            setTimeframe(5);
                                            setLoading(true);
                                        }, className: `flex-1 px-3 py-2 rounded text-sm font-medium transition ${timeframe === 5
                                            ? 'bg-emerald-600 text-white border border-emerald-500'
                                            : 'bg-slate-700 text-slate-300 border border-slate-600 hover:border-slate-500'}`, children: "5M" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "text-xs text-slate-400 block mb-1", children: "Watchlist" }), onAddToWatchlist ? (addedToWatchlist === symbol ? (_jsx("div", { className: "w-full px-3 py-2 bg-emerald-900/60 border border-emerald-600 rounded text-emerald-300 text-sm text-center", children: "+ Added!" })) : (_jsxs("button", { onClick: () => {
                                    onAddToWatchlist(symbol);
                                    setAddedToWatchlist(symbol);
                                    setTimeout(() => setAddedToWatchlist(null), 4000);
                                }, className: "w-full px-3 py-2 bg-blue-600 hover:bg-blue-500 border border-blue-500 rounded text-white text-sm font-medium transition", children: ["+ Add ", symbol] }))) : (_jsx("div", { className: "w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-slate-500 text-sm text-center", children: "Select account first" }))] })] }), _jsx("div", { children: loading ? (_jsx("div", { className: "w-full h-96 flex items-center justify-center bg-slate-950", children: _jsxs("div", { className: "text-center", children: [_jsx("div", { className: "text-slate-300 text-lg mb-2", children: "\u23F3 Connecting to MT5..." }), _jsxs("p", { className: "text-slate-500 text-sm", children: ["Loading ", symbol, " historical data"] })] }) })) : error ? (_jsx("div", { className: "w-full h-96 flex items-center justify-center bg-slate-950", children: _jsxs("div", { className: "text-center", children: [_jsxs("p", { className: "text-red-400 text-lg mb-2", children: ["\u274C ", error] }), _jsx("p", { className: "text-slate-500 text-sm", children: "Make sure MT5 is running on the server" }), _jsx("p", { className: "text-slate-600 text-xs mt-2", children: "Attempting to reconnect..." })] }) })) : bricks.length === 0 ? (_jsx("div", { className: "w-full h-96 flex items-center justify-center bg-slate-950", children: _jsxs("div", { className: "text-center", children: [_jsx("div", { className: "text-emerald-400 text-lg mb-2", children: "\u2705 Connected to MT5" }), _jsx("p", { className: "text-slate-400 text-sm", children: "\u23F3 Building Renko bricks from live data..." }), _jsxs("p", { className: "text-slate-600 text-xs mt-2", children: ["Brick size: ", brickSize, " \u2014 waiting for price to move"] })] }) })) : (_jsxs(_Fragment, { children: [_jsxs("div", { className: "relative", style: { height: '550px' }, children: [_jsx("canvas", { ref: canvasRef, className: "w-full h-full bg-slate-950 cursor-crosshair block" }), calculating && (_jsx("div", { className: "absolute top-4 left-4 bg-amber-900/80 border border-amber-600 rounded px-3 py-1.5", children: _jsxs("p", { className: "text-amber-300 text-sm flex items-center gap-2", children: [_jsx("span", { className: "animate-spin", children: "\u231B" }), " Calculating Renko bricks..."] }) }))] }), (bid || ask) && (_jsxs("div", { className: "px-4 py-2 bg-slate-950 border-t border-slate-700 flex gap-4 justify-center", children: [_jsxs("div", { className: "flex gap-2", children: [_jsx("span", { className: "text-slate-400 text-sm", children: "BID:" }), _jsx("span", { className: "text-red-400 font-mono font-bold", children: bid.toFixed(bid < 100 ? 5 : 2) })] }), _jsx("div", { className: "border-l border-slate-700" }), _jsxs("div", { className: "flex gap-2", children: [_jsx("span", { className: "text-slate-400 text-sm", children: "ASK:" }), _jsx("span", { className: "text-green-400 font-mono font-bold", children: ask.toFixed(ask < 100 ? 5 : 2) })] }), _jsx("div", { className: "border-l border-slate-700" }), _jsxs("div", { className: "flex gap-2", children: [_jsx("span", { className: "text-slate-400 text-sm", children: "SPREAD:" }), _jsx("span", { className: "text-blue-400 font-mono font-bold", children: (ask - bid).toFixed(ask - bid < 1 ? 5 : 2) })] })] }))] })) }), _jsxs("div", { className: "px-4 py-2 bg-slate-800 border-t border-slate-700 text-xs text-slate-400 flex justify-between", children: [_jsxs("span", { children: ["\uD83D\uDCCA Timeframe: ", timeframe, "min | Brick: $", brickSize.toFixed(4)] }), _jsxs("span", { children: ["\uD83D\uDD04 ", calculating ? 'Computing...' : 'Real-time updates from MT5'] })] })] }));
}
