"use client"

import "./App.css";
import { DriverCard } from "./components/DriverCard";
import { Controls } from "./components/Controls";
import { SessionResultTable } from "./components/SessionResultTable";
import { useF1Data } from "./hooks/useF1Data";
import { LapDataTable } from "./components/LapDataTable";

function App() {
	// State for dropdowns
	const {
		years,
		events,
		sessions,
		drivers,
		sessionResult,
		selectedYear,
		selectedEvent,
		selectedSession,
		selectedDriver,
		driverLaps,
		loading,
		errors,
		handleYearChange,
		handleEventChange,
		handleSessionChange,
		handleDriverClick,
	} = useF1Data();

	return (
		<div className="app">
			<header className="app-header">
				<h1>Formula 1 Data Explorer</h1>
			</header>

			<main className="main-content">
				{/* Dropdown Controls */}
				<Controls
					years={years}
					events={events}
					sessions={sessions}
					selectedYear={selectedYear}
					selectedEvent={selectedEvent}
					selectedSession={selectedSession}
					loading={loading}
					errors={errors}
					onYearChange={handleYearChange}
					onEventChange={handleEventChange}
					onSessionChange={handleSessionChange}
				/>
				<div className="drivers-results-grid">

					{/* Drivers Display */}
					{selectedSession && (
						<div className="panel">
							<h2 className="panel-header">Drivers in {selectedEvent?.circuit_name}, {selectedEvent?.country_name} {selectedYear} {selectedSession.session_name}</h2>
							{loading.drivers && <div className="loading">Loading drivers...</div>}
							{errors.drivers && <div className="error">{errors.drivers}</div>}

							<div className="drivers-grid">
								{drivers.map((driver) => (
									<DriverCard
										key={driver.driver_number}
										driver={driver}
										isSelected={selectedDriver?.driver_number == driver.driver_number}
										onClick={handleDriverClick}
									/>
								))}
							</div>
						</div>
					)}

					{selectedSession &&
						<div className="panel">
							<h2 className="panel-header">Session Result</h2>
								<SessionResultTable
									sessionResult={sessionResult}
									loading={loading.sessionResult}
									error={errors.sessionResult}
								/>
						</div>
					}
				</div>

				{/* Lap Data Display */}
				{selectedDriver && (
					<div className="lap-data-section">
						<LapDataTable
							selectedDriver={selectedDriver}
							driverLaps={driverLaps}
							loading={loading.laps}
							error={errors.laps}
						/>
					</div>
				)}
			</main>
		</div>
	)
}

export default App
