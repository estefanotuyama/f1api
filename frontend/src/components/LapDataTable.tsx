
import type { Driver, DriverLapsData } from "../types"
import { formatLapTime } from "../utils"

interface LapDataTableProps {
	selectedDriver: Driver | null
	driverLaps: DriverLapsData | null
	loading: boolean
	error: string
}

export const LapDataTable = ({ selectedDriver, driverLaps, loading, error }: LapDataTableProps) => {
	if (!selectedDriver) {
		return null
	}

	return (
		<div className="panel-lap-data">
			<h2 className="panel-header">
				Lap Data for {selectedDriver.first_name} {selectedDriver.last_name}
				<br />
				<p className="note">
					Note: A lap time of 0:00.000 means the OpenF1 API did not provide lap data for this lap.
				</p>
			</h2>

			{loading && <div className="loading">Loading lap data...</div>}
			{error && <div className="error">{error}</div>}

			{driverLaps && driverLaps.laps.length > 0 && (
				<div className="data-table-container">
					<table className="data-table">
						<thead>
							<tr>
								<th>Lap</th>
								<th>Time</th>
								<th>Speed Trap (km/h)</th>
								<th>Compound</th>
								<th>Pit Out</th>
							</tr>
						</thead>
						<tbody>
							{driverLaps.laps.map((lap) => (
								<tr key={lap.lap_number}>
									<td>{lap.lap_number}</td>
									<td>{formatLapTime(lap.time)}</td>
									<td>{lap.speed_trap}</td>
									<td>{lap.compound}</td>
									<td>{lap.is_pit_out_lap ? "Yes" : "No"}</td>
								</tr>
							))}
						</tbody>
					</table>
				</div>
			)}
		</div>
	)
}

