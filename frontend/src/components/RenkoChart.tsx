import { useState, useEffect, useRef } from 'react';

interface RenkoBrick {
  index: number;
  open: number;
  close: number;
  high: number;
  low: number;
  color: 'green' | 'red';
  signal: 'BUY' | 'SELL';
}

interface RenkoChartProps {
  symbol: string;
  brickSize?: number;
}

export default function RenkoChart({ symbol, brickSize }: RenkoChartProps) {
  const [bricks, setBricks] = useState<RenkoBrick[]>([]);
  const [currentPrice, setCurrentPrice] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [chartData, setChartData] = useState({
    symbol: '',
    brick_size: 0,
    bricks: [],
    current_price: 0,
    current_direction: 'long',
  });

  // Fetch Renko chart data
  useEffect(() => {
    const fetchChart = async () => {
      try {
        setLoading(true);
        setError(null);

        const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/renko/chart/${symbol}${brickSize ? `?brick_size=${brickSize}` : ''}`;
        const res = await fetch(url);

        if (!res.ok) {
          throw new Error(`Failed to fetch chart: ${res.statusText}`);
        }

        const data = await res.json();
        setChartData(data);
        setBricks(data.bricks);
        setCurrentPrice(data.current_price);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load chart');
      } finally {
        setLoading(false);
      }
    };

    fetchChart();

    // Poll every 1 second for real-time updates
    const interval = setInterval(fetchChart, 1000);
    return () => clearInterval(interval);
  }, [symbol, brickSize]);

  // Draw Renko chart on canvas - Professional TradingView style
  useEffect(() => {
    if (!canvasRef.current || bricks.length === 0) return;

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
    const leftPadding = 70;
    const rightPadding = 20;
    const topPadding = 40;
    const bottomPadding = 40;
    const chartWidth = width - leftPadding - rightPadding;
    const chartHeight = height - topPadding - bottomPadding;

    // Clear canvas with dark background
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, width, height);

    if (bricks.length === 0) return;

    // Find min/max prices for scaling
    const prices = bricks.flatMap(b => [b.open, b.close, b.high, b.low]);
    const minPrice = Math.min(...prices) * 0.998;
    const maxPrice = Math.max(...prices) * 1.002;
    const priceRange = maxPrice - minPrice || 1;

    // Calculate dimensions
    const yScale = chartHeight / priceRange;
    const bricksToShow = Math.min(bricks.length, 50);
    const brickWidth = chartWidth / bricksToShow;

    // Helper function to convert price to Y coordinate
    const priceToY = (price: number) => {
      return height - bottomPadding - ((price - minPrice) * yScale);
    };

    // Draw background grid
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);

    // Horizontal grid lines with prices
    for (let i = 0; i <= 8; i++) {
      const price = minPrice + ((priceRange / 8) * i);
      const y = priceToY(price);
      
      // Grid line
      ctx.beginPath();
      ctx.moveTo(leftPadding, y);
      ctx.lineTo(width - rightPadding, y);
      ctx.stroke();

      // Price label on left
      ctx.setLineDash([]);
      ctx.fillStyle = '#94a3b8';
      ctx.font = 'bold 12px Arial';
      ctx.textAlign = 'right';
      ctx.fillText(price.toFixed(2), leftPadding - 10, y + 4);
      ctx.setLineDash([5, 5]);
    }

    ctx.setLineDash([]);

    // Draw Y-axis
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(leftPadding, topPadding);
    ctx.lineTo(leftPadding, height - bottomPadding);
    ctx.lineTo(width - rightPadding, height - bottomPadding);
    ctx.stroke();

    // Draw bricks - Professional style
    const visibleBricks = bricks.slice(-bricksToShow);
    const brickSpacing = brickWidth * 0.8;
    const wickWidth = 1;

    visibleBricks.forEach((brick, idx) => {
      const x = leftPadding + (idx / bricksToShow) * chartWidth + brickWidth * 0.1;

      const openY = priceToY(brick.open);
      const closeY = priceToY(brick.close);
      const highY = priceToY(brick.high);
      const lowY = priceToY(brick.low);

      // Determine colors
      const bullColor = '#10b981';
      const bearColor = '#ef4444';
      const wickColor = brick.color === 'green' ? '#059669' : '#dc2626';
      const brickColor = brick.color === 'green' ? bullColor : bearColor;

      // Draw wick (high-low line)
      ctx.strokeStyle = wickColor;
      ctx.lineWidth = wickWidth;
      ctx.beginPath();
      ctx.moveTo(x + brickSpacing / 2, highY);
      ctx.lineTo(x + brickSpacing / 2, lowY);
      ctx.stroke();

      // Draw brick body with gradient effect
      const top = Math.min(openY, closeY);
      const bottom = Math.max(openY, closeY);
      const bodyHeight = Math.max(bottom - top, 2);

      // Brick fill
      ctx.fillStyle = brickColor;
      ctx.globalAlpha = 0.8;
      ctx.fillRect(x, top, brickSpacing, bodyHeight);
      ctx.globalAlpha = 1.0;

      // Brick border
      ctx.strokeStyle = wickColor;
      ctx.lineWidth = 1.5;
      ctx.strokeRect(x, top, brickSpacing, bodyHeight);
    });

    // Draw title with symbol info
    ctx.fillStyle = '#f1f5f9';
    ctx.font = 'bold 18px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(`${symbol} - Renko`, leftPadding + 10, 25);

    // Current price info
    const lastBrick = bricks[bricks.length - 1];
    const direction = lastBrick.color === 'green' ? '▲ BUY' : '▼ SELL';
    const directionColor = lastBrick.color === 'green' ? '#10b981' : '#ef4444';

    ctx.fillStyle = directionColor;
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'right';
    ctx.fillText(direction, width - rightPadding - 10, 25);

    // Price info box
    const infoX = width - rightPadding - 150;
    const infoY = topPadding + 5;
    
    ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
    ctx.fillRect(infoX - 5, infoY - 25, 145, 50);
    
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 1;
    ctx.strokeRect(infoX - 5, infoY - 25, 145, 50);

    ctx.fillStyle = '#cbd5e1';
    ctx.font = '11px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(`Brick: ${chartData.brick_size}`, infoX, infoY - 10);
    ctx.fillText(`Bricks: ${chartData.total_bricks}`, infoX, infoY + 5);
    ctx.fillText(`Price: ${currentPrice.toFixed(2)}`, infoX, infoY + 20);

  }, [bricks, currentPrice, chartData.brick_size, chartData.total_bricks]);

  if (error) {
    return (
      <div className="bg-slate-900 p-4 rounded-lg border border-red-600">
        <p className="text-red-400">❌ Chart Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 p-4 rounded-lg border border-slate-700">
      <div className="mb-3 flex justify-between items-center">
        <div>
          <h3 className="text-xl font-bold text-white">{symbol}</h3>
          <p className="text-sm text-slate-400">
            Renko Chart • Brick: <span className="text-emerald-400 font-mono">{chartData.brick_size}</span> • 
            Total: <span className="text-blue-400 font-mono">{chartData.total_bricks}</span>
          </p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-white">${currentPrice.toFixed(2)}</p>
          <p className={`text-sm font-semibold ${chartData.current_direction === 'long' ? 'text-green-400' : 'text-red-400'}`}>
            {chartData.current_direction === 'long' ? '🟢 Uptrend' : '🔴 Downtrend'}
          </p>
        </div>
      </div>

      {loading ? (
        <div className="w-full h-96 flex items-center justify-center bg-slate-800 rounded border border-slate-700">
          <p className="text-slate-300">⏳ Loading real-time data from MT5...</p>
        </div>
      ) : (
        <div className="border border-slate-700 rounded overflow-hidden">
          <canvas
            ref={canvasRef}
            className="w-full bg-slate-950"
            style={{ height: '450px', display: 'block' }}
          />
        </div>
      )}

      <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
        <div className="bg-slate-800 p-2 rounded border border-slate-700">
          <p className="text-slate-400">🟢 GREEN</p>
          <p className="text-emerald-400 font-semibold">Bullish</p>
        </div>
        <div className="bg-slate-800 p-2 rounded border border-slate-700">
          <p className="text-slate-400">🔴 RED</p>
          <p className="text-red-400 font-semibold">Bearish</p>
        </div>
        <div className="bg-slate-800 p-2 rounded border border-slate-700">
          <p className="text-slate-400">⚡ REAL-TIME</p>
          <p className="text-blue-400 font-semibold">MT5 1-Min</p>
        </div>
      </div>
    </div>
  );
}
