import { useState, useEffect, useRef } from 'react';

interface RenkoBrick {
  index: number;
  open: number;
  close: number;
  high: number;
  low: number;
  color: 'green' | 'red';
  signal?: 'BUY' | 'SELL';
}

interface RenkoChartProps {
  symbol: string;
  brickSize?: number;
}

export default function RenkoChart({ symbol: initialSymbol, brickSize: initialBrickSize }: RenkoChartProps) {
  const [symbol, setSymbol] = useState<string>(initialSymbol || 'EURUSD');
  const [brickSize, setBrickSize] = useState<number>(initialBrickSize || 0.005);
  const [timeframe, setTimeframe] = useState<number>(1); // 1 or 5 minutes
  const [bricks, setBricks] = useState<RenkoBrick[]>([]);
  const [currentPrice, setCurrentPrice] = useState<number>(0);
  const [bid, setBid] = useState<number>(0);
  const [ask, setAsk] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false); // Show when Renko calc in progress
  const [error, setError] = useState<string | null>(null);
  const [availableSymbols, setAvailableSymbols] = useState<string[]>([]);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const bricksRef = useRef<RenkoBrick[]>([]);
  const priceRef = useRef<number>(0);
  const bidRef = useRef<number>(0);
  const askRef = useRef<number>(0);
  const lastTimestampRef = useRef<string>('');
  const isPendingRef = useRef<boolean>(false);  // Prevent duplicate requests
  const [chartData, setChartData] = useState({
    symbol: '',
    brick_size: 0,
    current_direction: 'long',
    total_bricks: 0,
  });

  // Fetch available symbols on mount
  useEffect(() => {
    const fetchSymbols = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/tickers`);
        if (res.ok) {
          const response = await res.json();
          const tickers = response.data || response;
          const symbols = tickers.map((t: any) => t.symbol);
          setAvailableSymbols(symbols);
        }
      } catch (err) {
        console.error('Failed to fetch symbols:', err);
      }
    };
    fetchSymbols();
  }, []);

  // Update when initial symbol changes
  useEffect(() => {
    setSymbol(initialSymbol);
  }, [initialSymbol]);

  // Fetch chart data with efficient polling
  useEffect(() => {
    const fetchChart = async () => {
      try {
        // Skip if request already pending (prevent stacked requests)
        if (isPendingRef.current) {
          console.log('Skipping duplicate request - one already in flight');
          return;
        }
        
        isPendingRef.current = true;
        setCalculating(true);
        const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/renko/chart/${symbol}?brick_size=${brickSize}&timeframe=${timeframe}`;
        const res = await fetch(url);

        if (!res.ok) {
          throw new Error(`Failed to fetch chart: ${res.statusText}`);
        }

        const data = await res.json();
        
        // Always update bid/ask immediately (even while calculating)
        bidRef.current = data.bid || 0;
        askRef.current = data.ask || 0;
        priceRef.current = data.current_price || 0;
        
        // Update state to show bid/ask
        setBid(data.bid || 0);
        setAsk(data.ask || 0);
        setCurrentPrice(data.current_price || 0);
        
        // Only update bricks if data changed (to avoid re-renders)
        if (data.timestamp !== lastTimestampRef.current) {
          lastTimestampRef.current = data.timestamp;
          
          bricksRef.current = data.bricks || [];
          
          if (loading) {
            setBricks(data.bricks || []);
            setChartData({
              symbol: data.symbol,
              brick_size: data.brick_size,
              current_direction: data.current_direction,
              total_bricks: data.total_bricks,
            });
            setError(null);
            setLoading(false);
          }
        }
        setCalculating(false);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to load chart';
        setError(errorMsg);
        setLoading(false);
        setCalculating(false);
      } finally {
        isPendingRef.current = false;
      }
    };

    fetchChart();
    // Increased to 2 seconds to prevent overwhelming backend with requests
    // 500ms was causing 6+ stacked requests during 3-second calculations
    const interval = setInterval(fetchChart, 2000);
    return () => clearInterval(interval);
  }, [symbol, brickSize, timeframe, loading]);

  // Canvas drawing
  useEffect(() => {
    const drawChart = () => {
      if (!canvasRef.current || bricksRef.current.length === 0) return;

      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const rect = canvas.parentElement?.getBoundingClientRect();
      if (rect) {
        canvas.width = rect.width;
        canvas.height = rect.height;
      }

      const width = canvas.width;
      const height = canvas.height;
      const leftPadding = 80;
      const rightPadding = 30;
      const topPadding = 50;
      const bottomPadding = 50;
      const chartWidth = width - leftPadding - rightPadding;
      const chartHeight = height - topPadding - bottomPadding;

      ctx.fillStyle = '#0f172a';
      ctx.fillRect(0, 0, width, height);

      const bricks = bricksRef.current;
      if (bricks.length === 0) return;

      const allPrices = bricks.flatMap(b => [b.open, b.close, b.high, b.low]);
      const minPrice = Math.min(...allPrices);
      const maxPrice = Math.max(...allPrices);
      const priceRange = maxPrice - minPrice;
      
      const pricePadding = priceRange * 0.05;
      const chartMinPrice = minPrice - pricePadding;
      const chartMaxPrice = maxPrice + pricePadding;
      const chartPriceRange = chartMaxPrice - chartMinPrice;

      const priceToY = (price: number) => {
        return height - bottomPadding - ((price - chartMinPrice) / chartPriceRange) * chartHeight;
      };

      const bricksToShow = Math.min(bricks.length, 100);
      const visibleBricks = bricks.slice(-bricksToShow);
      const brickWidth = chartWidth / bricksToShow * 0.85;
      const brickSpacing = chartWidth / bricksToShow;

      // Draw Grid
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

      // Draw Bricks
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

      // Draw Info
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
    };

    const animationFrame = setInterval(drawChart, 100);
    return () => clearInterval(animationFrame);
  }, [symbol, chartData.brick_size, chartData.total_bricks]);

  // Canvas drawing - uses refs so it redraws WITHOUT state updates
  useEffect(() => {
    const drawChart = () => {
      if (!canvasRef.current || bricksRef.current.length === 0) return;

      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      // Set canvas size
      const rect = canvas.parentElement?.getBoundingClientRect();
      if (rect) {
        canvas.width = rect.width;
        canvas.height = rect.height;
      }

      const width = canvas.width;
      const height = canvas.height;
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
      if (bricks.length === 0) return;

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
      const priceToY = (price: number) => {
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
    };

    // Draw continuously
    const animationFrame = setInterval(drawChart, 100);
    return () => clearInterval(animationFrame);
  }, [symbol, chartData.brick_size, chartData.total_bricks]);

  if (error) {
    return (
      <div className="bg-slate-900 p-4 rounded-lg border border-red-600">
        <p className="text-red-400">❌ Chart Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 rounded-lg border border-slate-700 overflow-hidden">
      {/* Controls */}
      <div className="p-4 bg-slate-800 border-b border-slate-700 grid grid-cols-3 gap-3">
        {/* Symbol Selector */}
        <div>
          <label className="text-xs text-slate-400 block mb-1">Symbol</label>
          <select 
            value={symbol}
            onChange={(e) => {
              setSymbol(e.target.value);
              setLoading(true);
            }}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white text-sm focus:outline-none focus:border-emerald-500"
          >
            {availableSymbols.length > 0 ? (
              availableSymbols.map(s => (
                <option key={s} value={s}>{s}</option>
              ))
            ) : (
              <>
                <option value="EURUSD">EURUSD</option>
                <option value="GBPUSD">GBPUSD</option>
                <option value="GOLD">GOLD</option>
                <option value="BTCUSD">BTCUSD</option>
                <option value="ETHUSD">ETHUSD</option>
              </>
            )}
          </select>
        </div>

        {/* Brick Size */}
        <div>
          <label className="text-xs text-slate-400 block mb-1">Brick Size</label>
          <input 
            type="number"
            value={brickSize}
            onChange={(e) => {
              setBrickSize(parseFloat(e.target.value) || 0.001);
              setLoading(true);
            }}
            step="0.001"
            min="0.001"
            max="100"
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white text-sm focus:outline-none focus:border-emerald-500"
            placeholder="0.005"
          />
        </div>

        {/* Timeframe */}
        <div>
          <label className="text-xs text-slate-400 block mb-1">Timeframe</label>
          <div className="flex gap-2">
            <button
              onClick={() => {
                setTimeframe(1);
                setLoading(true);
              }}
              className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${
                timeframe === 1 
                  ? 'bg-emerald-600 text-white border border-emerald-500' 
                  : 'bg-slate-700 text-slate-300 border border-slate-600 hover:border-slate-500'
              }`}
            >
              1M
            </button>
            <button
              onClick={() => {
                setTimeframe(5);
                setLoading(true);
              }}
              className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${
                timeframe === 5 
                  ? 'bg-emerald-600 text-white border border-emerald-500' 
                  : 'bg-slate-700 text-slate-300 border border-slate-600 hover:border-slate-500'
              }`}
            >
              5M
            </button>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div>
        {loading ? (
          <div className="w-full h-96 flex items-center justify-center bg-slate-950">
            <div className="text-center">
              <div className="text-slate-300 text-lg mb-2">⏳ Loading chart data...</div>
              <p className="text-slate-500 text-sm">Fetching from MT5</p>
            </div>
          </div>
        ) : (
          <>
            <div className="relative">
              <canvas
                ref={canvasRef}
                className="w-full bg-slate-950"
                style={{ height: '550px', display: 'block' }}
              />
              {calculating && (
                <div className="absolute top-4 left-4 bg-amber-900/80 border border-amber-600 rounded px-3 py-1.5">
                  <p className="text-amber-300 text-sm flex items-center gap-2">
                    <span className="animate-spin">⌛</span> Calculating Renko bricks...
                  </p>
                </div>
              )}
            </div>
            
            {/* Bid/Ask Display */}
            {(bid || ask) && (
              <div className="px-4 py-2 bg-slate-950 border-t border-slate-700 flex gap-4 justify-center">
                <div className="flex gap-2">
                  <span className="text-slate-400 text-sm">BID:</span>
                  <span className="text-red-400 font-mono font-bold">{bid.toFixed(bid < 100 ? 5 : 2)}</span>
                </div>
                <div className="border-l border-slate-700" />
                <div className="flex gap-2">
                  <span className="text-slate-400 text-sm">ASK:</span>
                  <span className="text-green-400 font-mono font-bold">{ask.toFixed(ask < 100 ? 5 : 2)}</span>
                </div>
                <div className="border-l border-slate-700" />
                <div className="flex gap-2">
                  <span className="text-slate-400 text-sm">SPREAD:</span>
                  <span className="text-blue-400 font-mono font-bold">{(ask - bid).toFixed(ask - bid < 1 ? 5 : 2)}</span>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Status Bar */}
      <div className="px-4 py-2 bg-slate-800 border-t border-slate-700 text-xs text-slate-400 flex justify-between">
        <span>📊 Timeframe: {timeframe}min | Brick: ${brickSize.toFixed(4)}</span>
        <span>🔄 {calculating ? 'Computing...' : 'Real-time updates from MT5'}</span>
      </div>
    </div>
  );
}
