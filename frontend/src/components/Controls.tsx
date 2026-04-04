import { useState } from 'react';

export default function Controls({
  onStart,
  onStop,
  onUpdateSettings,
}: {
  onStart: () => Promise<void>;
  onStop: () => Promise<void>;
  onUpdateSettings: (brickSize: number) => Promise<void>;
}) {
  const [brickSize, setBrickSize] = useState(1);

  return (
    <div className="bg-slate-800 p-4 rounded-lg grid grid-cols-1 md:grid-cols-3 gap-3">
      <button className="btn bg-emerald-500 px-4 py-2 rounded" onClick={onStart}>
        Start Bot
      </button>
      <button className="btn bg-rose-500 px-4 py-2 rounded" onClick={onStop}>
        Stop Bot
      </button>
      <div className="flex gap-2 items-center">
        <input
          type="number"
          min="0.1"
          step="0.1"
          value={brickSize}
          onChange={(e) => setBrickSize(Number(e.target.value))}
          className="rounded px-2 py-1 text-black"
        />
        <button className="btn bg-blue-500 px-4 py-2 rounded" onClick={() => onUpdateSettings(brickSize)}>
          Set Brick Size
        </button>
      </div>
    </div>
  );
}
