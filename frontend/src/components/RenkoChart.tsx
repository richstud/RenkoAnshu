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

    // Poll every 2 seconds for real-time updates
    const interval = setInterval(fetchChart, 2000);
    return () => clearInterval(interval);
  }, [symbol, brickSize]);

  // Draw Renko chart on canvas
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
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    // Clear canvas
    ctx.fillStyle = '#1f2937';
    ctx.fillRect(0, 0, width, height);

    if (bricks.length === 0) return;

    // Find min/max prices for scaling
    const prices = bricks.flatMap(b => [b.open, b.close, b.high, b.low]);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice || 1;

    // Calculate dimensions
    const brickWidth = chartWidth / bricks.length;
    const yScale = chartHeight / priceRange;

    // Helper function to convert price to Y coordinate
    const priceToY = (price: number) => {
      return height - padding - ((price - minPrice) * yScale);
    };

    // Draw grid lines
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 1;

    // Horizontal grid lines
    for (let i = 0; i <= 5; i++) {
      const price = minPrice + ((priceRange / 5) * i);
      const y = priceToY(price);
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();

      // Price labels
      ctx.fillStyle = '#9CA3AF';
      ctx.font = '12px Arial';
      ctx.textAlign = 'right';
      ctx.fillText(price.toFixed(2), padding - 10, y + 4);
    }

    // Draw bricks
    const visibleBricks = bricks.slice(-50); // Show last 50 bricks
    const startIndex = bricks.length - visibleBricks.length;

    visibleBricks.forEach((brick, idx) => {
      const x = padding + ((idx / visibleBricks.length) * chartWidth);
      const nextX = padding + (((idx + 1) / visibleBricks.length) * chartWidth);
      const brickWidth = nextX - x - 2;

      const openY = priceToY(brick.open);
      const closeY = priceToY(brick.close);
      const highY = priceToY(brick.high);
      const lowY = priceToY(brick.low);

      // Draw wick (high-low line)
      ctx.strokeStyle = brick.color === 'green' ? '#10B981' : '#EF4444';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x + brickWidth / 2, highY);
      ctx.lineTo(x + brickWidth / 2, lowY);
      ctx.stroke();

      // Draw brick body
      const top = Math.min(openY, closeY);
      const bottom = Math.max(openY, closeY);
      const bodyHeight = Math.max(bottom - top, 1);

      ctx.fillStyle = brick.color === 'green' ? '#10B981' : '#EF4444';
      ctx.fillRect(x, top, brickWidth, bodyHeight);

      // Draw brick border
      ctx.strokeStyle = brick.color === 'green' ? '#059669' : '#DC2626';
      ctx.lineWidth = 1;
      ctx.strokeRect(x, top, brickWidth, bodyHeight);
    });

    // Draw Y-axis
    ctx.strokeStyle = '#4B5563';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();

    // Draw title and info
    ctx.fillStyle = '#F3F4F6';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(`${symbol} - Renko Chart (${chartData.brick_size})`, padding + 10, 25);

    // Current price and direction
    const direction = bricks[bricks.length - 1].color === 'green' ? '▲ UP' : '▼ DOWN';
    const directionColor = bricks[bricks.length - 1].color === 'green' ? '#10B981' : '#EF4444';

    ctx.fillStyle = directionColor;
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'right';
    ctx.fillText(`${direction}`, width - padding - 10, 25);

    ctx.fillStyle = '#D1D5DB';
    ctx.font = '12px Arial';
    ctx.fillText(`Current: ${currentPrice.toFixed(2)}`, width - padding - 10, 45);
  }, [bricks, currentPrice, chartData.brick_size]);

  if (error) {
    return (
      <div className="bg-slate-700 p-4 rounded-lg border border-red-600">
        <p className="text-red-400">❌ Chart Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-700 p-4 rounded-lg border border-slate-600">
      <div className="mb-3">
        <h3 className="text-lg font-semibold text-white">📊 Renko Chart - {symbol}</h3>
        <div className="text-sm text-slate-400 mt-1">
          Brick Size: <span className="text-blue-400 font-mono">{chartData.brick_size}</span> | 
          Total Bricks: <span className="text-blue-400 font-mono">{chartData.total_bricks}</span> | 
          Direction: <span className={chartData.current_direction === 'long' ? 'text-green-400' : 'text-red-400'}>
            {chartData.current_direction === 'long' ? '🟢 Long' : '🔴 Short'}
          </span>
        </div>
      </div>

      {loading ? (
        <div className="w-full h-96 flex items-center justify-center bg-slate-600 rounded">
          <p className="text-slate-300">Loading chart...</p>
        </div>
      ) : (
        <canvas
          ref={canvasRef}
          className="w-full border border-slate-500 rounded"
          style={{ height: '400px' }}
        />
      )}

      <div className="mt-3 text-xs text-slate-400 space-y-1">
        <p>🟢 Green = Bullish (upward) brick</p>
        <p>🔴 Red = Bearish (downward) brick</p>
        <p>Updates every 2 seconds with 1-minute data</p>
      </div>
    </div>
  );
}
