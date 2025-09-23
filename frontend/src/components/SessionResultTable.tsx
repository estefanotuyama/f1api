import { SessionResultData } from "../types"
import { formatTime, solveDriverStatus } from "../utils"

interface SessionResultProps {
	sessionResult: SessionResultData | null
	loading: boolean
	error: string
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
							<td>{formatTime(driver)}</td>
							<td>{solveDriverStatus(driver)}</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>
	)
}
