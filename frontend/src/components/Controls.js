import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
export default function Controls({ onStart, onStop, onUpdateSettings, }) {
    const [brickSize, setBrickSize] = useState(1);
    return (_jsxs("div", { className: "bg-slate-800 p-4 rounded-lg grid grid-cols-1 md:grid-cols-3 gap-3", children: [_jsx("button", { className: "btn bg-emerald-500 px-4 py-2 rounded", onClick: onStart, children: "Start Bot" }), _jsx("button", { className: "btn bg-rose-500 px-4 py-2 rounded", onClick: onStop, children: "Stop Bot" }), _jsxs("div", { className: "flex gap-2 items-center", children: [_jsx("input", { type: "number", min: "0.1", step: "0.1", value: brickSize, onChange: (e) => setBrickSize(Number(e.target.value)), className: "rounded px-2 py-1 text-black" }), _jsx("button", { className: "btn bg-blue-500 px-4 py-2 rounded", onClick: () => onUpdateSettings(brickSize), children: "Set Brick Size" })] })] }));
}
