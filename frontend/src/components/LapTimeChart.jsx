import React, { useRef, useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ReferenceLine } from "recharts";

/* ---------- Helpers ---------- */
function parseTimeToSeconds(timeInput) {
	if (!timeInput) return null;
	if (typeof timeInput === "number") return timeInput;
	if (typeof timeInput === "string") {
		if (timeInput === "0:00.000") return null;
		const parts = timeInput.split(":");
		if (parts.length === 2) {
			const minutes = parseInt(parts[0], 10) || 0;
			const seconds = parseFloat(parts[1]) || 0;
			return minutes * 60 + seconds;
		}
		const s = parseFloat(timeInput);
		return Number.isNaN(s) ? null : s;
	}
	return null;
}
function formatSecondsToTime(seconds) {
	if (seconds == null) return "N/A";
	const m = Math.floor(seconds / 60);
	const s = (seconds % 60).toFixed(3).padStart(6, "0");
	return `${m}:${s}`;
}
function getCompoundColor(compound) {
	if (!compound) return "#999999";
	const c = compound.toLowerCase();
	if (c.includes("soft")) return "#DA291C";
	if (c.includes("medium")) return "#FFCD00";
	if (c.includes("hard")) return "#F0F0F0";
	if (c.includes("intermediate")) return "#43B02A";
	if (c.includes("wet")) return "#0067A5";
	return "#999999";
}

/* ---------- Custom tooltip & dot ---------- */
const CustomTooltip = ({ active, payload, bestLapSec }) => {
	if (!active || !payload || !payload.length) return null;
	const data = payload[0].payload;
	const delta = data.timeSec != null && bestLapSec != null ? `+${(data.timeSec - bestLapSec).toFixed(3)}s` : "";
	return (
		<div className="custom-tooltip">
			<p className="tooltip-label">Lap {data.lap}</p>
			<p>Time: {formatSecondsToTime(data.timeSec)} </p>
			<p>Delta: {delta}</p>
			<p>Compound: {data.compound || "N/A"}</p>
			<p>Speed Trap: {data.speedTrap || "N/A"} km/h</p>
			{data.pitOut && <p style={{ color: "#82aaff" }}>Pit Out Lap</p>}
			{data.isOutlier && <p style={{ color: "#cccccc" }}>Marked as outlier</p>}
		</div>
	);
};

const CustomDot = (props) => {
	const { cx, cy, payload } = props;
	if (payload.timeSec == null) return null;
	return (
		<circle
			cx={cx}
			cy={cy}
			r={4}
			fill={getCompoundColor(payload.compound)}
			stroke={payload.pitOut ? "#ffffff" : "none"}
			strokeWidth={payload.pitOut ? 2 : 0}
		/>
	);
};

/* ---------- Main ---------- */
export const LapTimeChart = ({ selectedDriver, driverLaps, loading, error }) => {
	const outerRef = useRef(null); // stable parent (visible width)
	const [containerWidth, setContainerWidth] = useState(800);

	// Toggle to exclude outliers from Y-scale (default ON)
	const [excludeOutliers, setExcludeOutliers] = useState(true);

	// Measure stable container width (outerRef should be .chart-content)
	useEffect(() => {
		function measure() {
			const el = outerRef.current;
			if (!el) return;
			const w = Math.floor(el.getBoundingClientRect().width);
			setContainerWidth(w || 800);
		}
		measure();
		window.addEventListener("resize", measure);
		return () => window.removeEventListener("resize", measure);
	}, []);

	const renderContent = () => {
		if (loading) return <div className="loading">Loading lap data...</div>;
		if (error) return <div className="error">{error}</div>;
		if (!driverLaps || !driverLaps.laps || driverLaps.laps.length === 0) {
			return <div>No lap data available for this session.</div>;
		}

		// Build chart data
		const chartData = driverLaps.laps.map((lap) => ({
			lap: lap.lap_number,
			timeSec: parseTimeToSeconds(lap.time),
			speedTrap: lap.speed_trap,
			compound: lap.compound,
			pitOut: lap.is_pit_out_lap,
		}));

		// Median for simple outlier detection
		const validTimes = chartData.map(d => d.timeSec).filter(t => t != null);
		const median = (() => {
			if (!validTimes.length) return null;
			const s = [...validTimes].sort((a, b) => a - b);
			const m = Math.floor(s.length / 2);
			return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
		})();

		// Mark outliers: > median * threshold
		const OUTLIER_THRESHOLD = 1.15;
		chartData.forEach(d => {
			d.isOutlier = false;
			if (d.timeSec == null) { d.isOutlier = false; return; }
			if (median != null && d.timeSec > median * OUTLIER_THRESHOLD) d.isOutlier = true;
			// NOTE: we intentionally do NOT auto-mark lap 1/pitOut here to keep rule simple.
			// If you want to include them, uncomment below:
			// if (d.pitOut) d.isOutlier = true;
		});

		const outlierCount = chartData.filter(d => d.isOutlier).length;

		// Filter data for chart rendering based on excludeOutliers toggle
		const displayData = excludeOutliers
			? chartData.filter(d => d.timeSec != null && !d.isOutlier)
			: chartData;

		// Decide which times to use for scaling the Y axis
		let scaleTimes = chartData.filter(d => d.timeSec != null && !(excludeOutliers && d.isOutlier)).map(d => d.timeSec);
		if (scaleTimes.length === 0) scaleTimes = chartData.filter(d => d.timeSec != null).map(d => d.timeSec);

		// Compute best lap (for tooltip delta)
		const allValidTimes = chartData.filter(d => d.timeSec != null).map(d => d.timeSec);
		const bestLapSec = allValidTimes.length ? Math.min(...allValidTimes) : null;

		const bestLapData = bestLapSec ? chartData.find(d => d.timeSec === bestLapSec) : null;
		const bestLapNumber = bestLapData ? bestLapData.lap : null;

		// Compute Y domain
		const PAD = 1.0; // seconds padding
		const hasScaleTimes = scaleTimes.length > 0;
		const minTime = hasScaleTimes ? Math.min(...scaleTimes) : 0;
		const maxTime = hasScaleTimes ? Math.max(...scaleTimes) : 0;
		const yDomain = hasScaleTimes ? [Math.ceil(maxTime + PAD), Math.max(0, Math.floor(minTime - PAD))] : ["auto", "auto"];

		// Chart size logic (horizontal scrolling) - use displayData for sizing
		const POINT_SPACING = 60;
		const innerWidth = Math.max(POINT_SPACING * displayData.length, Math.floor(containerWidth * 0.8));
		const MAX_WIDTH = 4000;
		const chartInnerWidth = Math.min(innerWidth, MAX_WIDTH);

		return (
			<>
				{/* Controls / toggle */}
				<div className="outlier-controls">
					<div className="outlier-controls-left">
						<label className="outlier-toggle-label">
							<div
								onClick={() => setExcludeOutliers(v => !v)}
								className={`toggle-switch ${excludeOutliers ? 'active' : 'inactive'}`}
							>
								<div className={`toggle-switch-knob ${excludeOutliers ? 'active' : 'inactive'}`} />
							</div>
							Hide outliers from chart
						</label>

						<div className={`outlier-badge ${outlierCount > 0 ? 'has-outliers' : 'no-outliers'}`}>
							<span className="outlier-badge-dot">●</span>
							{outlierCount > 0
								? `${outlierCount} outlier${outlierCount > 1 ? "s" : ""} detected`
								: "No outliers detected"
							}
							{excludeOutliers && outlierCount > 0 && " (hidden)"}
						</div>
					</div>

					<div className="outlier-threshold-info">
						Threshold: +15% above median
					</div>
				</div>

				{/* Chart note */}
				<p className="chart-note">
					{excludeOutliers
						? `Showing ${displayData.length} laps with outliers hidden. Scale optimized for regular lap times.`
						: `Showing all ${chartData.length} laps. Outliers appear as faded circles.`
					} Scroll horizontally to view all data.
				</p>

				<div className="lap-chart-container" style={{ overflowX: "auto", paddingTop: 12 }}>
					<div
						className="lap-chart-inner"
						style={{
							minWidth: `${chartInnerWidth}px`,
							width: `${chartInnerWidth}px`,
							display: "block",
						}}
					>
						<LineChart
							width={chartInnerWidth}
							height={460}
							data={displayData}
							margin={{ top: 20, right: 30, left: 40, bottom: 20 }}
						>
							<CartesianGrid strokeDasharray="3 3" strokeOpacity={0.15} />

							<XAxis
								dataKey="lap"
								type="number"
								domain={["dataMin", "dataMax"]}
								tick={{ fill: "#A9A9A9", fontSize: 12 }}
								allowDecimals={false}
								interval={0}
								label={{ value: "Lap", position: "insideBottom", offset: 0, fill: "#A9A9A9" }}
							/>
							<YAxis
								dataKey="timeSec"
								tickFormatter={(value) => {
									if (value == null) return "N/A";
									const m = Math.floor(value / 60);
									const s = (value % 60).toFixed(1);
									return m > 0 ? `${m}:${s.padStart(4, '0')}` : `${s}s`;
								}}
								tick={{ fill: "#A9A9A9", fontSize: 12 }}
								domain={yDomain}
								width={80}
								tickCount={8}
								label={{
									value: "Lap Time",
									angle: -90,
									position: "insideLeft",
									fill: "#A9A9A9",
									style: { textAnchor: 'middle' }
								}}
							/>
							<Tooltip content={<CustomTooltip bestLapSec={bestLapSec} />} />

							{bestLapNumber != null && (
								<ReferenceLine
									x={bestLapNumber}
									label={{
										value: "Best Lap",
										position: "top",
										fill: "#00C49F",
										fontSize: "12px",
										fontWeight: "500"
									}}
									stroke="#00C49F"
									strokeDasharray="3 6"
									strokeWidth={2}
								/>
							)}

							<Line
								type="linear"
								dataKey="timeSec"
								stroke="#8884d8"
								strokeWidth={2}
								dot={<CustomDot />}
								connectNulls={false}
								isAnimationActive={false}
								strokeLinecap="butt"
								strokeLinejoin="miter"
							/>
						</LineChart>
					</div>
				</div>
			</>
		);
	};

	return (
		<div className="panel-lap-data">
			<h2 className="panel-header">
				Lap Data for {selectedDriver?.first_name} {selectedDriver?.last_name}
			</h2>

			<div ref={outerRef} className="chart-content" style={{ width: "100%", overflowX: "hidden" }}>
				{renderContent()}
			</div>
		</div>
	);
};
