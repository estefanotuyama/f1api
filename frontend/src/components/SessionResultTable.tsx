import { DriverSessionResult, SessionResultData } from "../types"
import { formatLapTime, formatGap } from "../utils";

interface SessionResultProps {
	sessionResult: SessionResultData | null
	loading: boolean
	error: string
}

const solveDriverStatus = (driver: DriverSessionResult) => {
	if (driver.dnf) {
		return `${driver.number_of_laps} (DNF)`
	}
	else if (driver.dns) {
		return "DNS"
	}
	else if (driver.dsq) {
		return "DSQ"
	}
	return driver.number_of_laps
}

export const SessionResultTable = ({ sessionResult, loading, error }: SessionResultProps) => {
	if (loading) {
		return <div className="loading">Loading session result...</div>
	}

	if (error) {
		return <div className="error">{error}</div>
	}

	if (!sessionResult || sessionResult.result.length === 0) {
		return null
	}

	return (
		<div className="results-table-container">
			<table className="data-table">
				<thead>
					<tr>
						<th>Position</th>
						<th>Driver</th>
						<th>Team</th>
						<th>Gap to leader</th>
						<th>Laps</th>
					</tr>
				</thead>
				<tbody>
					{sessionResult.result.map((driver) => (
						<tr key={driver.position}>
							<td>{driver.position}</td>
							<td>{`${driver.first_name} ${driver.last_name}`}</td>
							<td>{driver.team}</td>
							<td>{driver.position === 1 ? driver.duration : driver.gap_to_leader}</td>
							<td>{solveDriverStatus(driver)}</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>
	)
}
