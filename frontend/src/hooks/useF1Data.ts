import { useState, useEffect } from "react";
import { Driver, F1Session, LapData, DriverLapsData, Event } from "../types";

const API_BASE_URL = "http://localhost:8000";

export const useF1Data = () => {

	const [years, setYears] = useState<number[]>([]);
	const [events, setEvents] = useState<Event[]>([]);
	const [sessions, setSessions] = useState<F1Session[]>([]);
	const [drivers, setDrivers] = useState<Driver[]>([]);

	// State for selections
	const [selectedYear, setSelectedYear] = useState<number | null>(null);
	const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
	const [selectedSession, setSelectedSession] = useState<F1Session | null>(null);
	const [selectedDriver, setSelectedDriver] = useState<Driver | null>(null);

	// State for lap data
	const [driverLaps, setDriverLaps] = useState<DriverLapsData | null>(null);

	// Loading and error states
	const [loading, setLoading] = useState({
		years: false,
		events: false,
		sessions: false,
		drivers: false,
		laps: false,
	});
	const [errors, setErrors] = useState({
		years: "",
		events: "",
		sessions: "",
		drivers: "",
		laps: "",
	});

	// Fetch available years on component mount
	useEffect(() => {
		fetchYears()
	}, []);

	const fetchYears = async () => {
		setLoading((prev) => ({ ...prev, years: true }));
		setErrors((prev) => ({ ...prev, years: "" }));

		try {
			const response = await fetch(`${API_BASE_URL}/events/years/`);
			if (!response.ok) throw new Error("Failed to fetch years");

			const data = await response.json();
			setYears(data);
		} catch (error) {
			setErrors((prev) => ({ ...prev, years: "Failed to load years" }));
		} finally {
			setLoading((prev) => ({ ...prev, years: false }));
		}
	}

	const fetchEvents = async (year: number) => {
		setLoading((prev) => ({ ...prev, events: true }));
		setErrors((prev) => ({ ...prev, events: "" }));

		try {
			const response = await fetch(`${API_BASE_URL}/events/${year}`);
			if (!response.ok) throw new Error("Failed to fetch events");

			const data = await response.json();
			if (data.length === 0) {
				setErrors((prev) => ({ ...prev, events: "No events available for this year" }));
			};
			setEvents(data);
		} catch (error) {
			setErrors((prev) => ({ ...prev, events: "Failed to load events" }));
		} finally {
			setLoading((prev) => ({ ...prev, events: false }));
		}
	}

	const fetchSessions = async (meetingKey: number) => {
		setLoading((prev) => ({ ...prev, sessions: true }));
		setErrors((prev) => ({ ...prev, sessions: "" }));

		try {
			const response = await fetch(`${API_BASE_URL}/sessions/${meetingKey}`);
			if (!response.ok) throw new Error("Failed to fetch sessions");

			const data = await response.json();
			if (data.length === 0) {
				setErrors((prev) => ({ ...prev, sessions: "No sessions available for this event" }));
			};
			setSessions(data);
		} catch (error) {
			setErrors((prev) => ({ ...prev, sessions: "Failed to load sessions" }));
		} finally {
			setLoading((prev) => ({ ...prev, sessions: false }));
		}
	}

	const fetchDrivers = async (sessionKey: number) => {
		setLoading((prev) => ({ ...prev, drivers: true }));
		setErrors((prev) => ({ ...prev, drivers: "" }));

		try {
			const response = await fetch(`${API_BASE_URL}/drivers/${sessionKey}`);
			if (!response.ok) throw new Error("Failed to fetch drivers");

			const data = await response.json();
			if (data.length === 0) {
				setErrors((prev) => ({ ...prev, drivers: "No drivers available for this session" }));
			}
			setDrivers(data);
		} catch (error) {
			setErrors((prev) => ({ ...prev, drivers: "Failed to load drivers" }));
		} finally {
			setLoading((prev) => ({ ...prev, drivers: false }));
		}
	}

	const fetchDriverLaps = async (sessionKey: number, driverNumber: number) => {
		setLoading((prev) => ({ ...prev, laps: true }));
		setErrors((prev) => ({ ...prev, laps: "" }));

		try {
			const response = await fetch(`${API_BASE_URL}/laps/${sessionKey}/${driverNumber}`);
			if (!response.ok) throw new Error("Failed to fetch lap data");

			const data = await response.json();
			if (!data.laps || data.laps.length === 0) {
				setErrors((prev) => ({ ...prev, laps: "No lap data available for this driver" }));
			};
			setDriverLaps(data)
		} catch (error) {
			setErrors((prev) => ({ ...prev, laps: "Failed to load lap data" }));
		} finally {
			setLoading((prev) => ({ ...prev, laps: false }));
		}
	}

	// Handle dropdown changes
	const handleYearChange = (year: number) => {
		setSelectedYear(year)
		setSelectedEvent(null)
		setSelectedSession(null)
		setSelectedDriver(null)
		setEvents([])
		setSessions([])
		setDrivers([])
		setDriverLaps(null)
		fetchEvents(year)
	};

	const handleEventChange = (event: Event) => {
		setSelectedEvent(event)
		setSelectedSession(null)
		setSelectedDriver(null)
		setSessions([])
		setDrivers([])
		setDriverLaps(null)
		fetchSessions(event.meeting_key)
	};

	const handleSessionChange = (session: F1Session) => {
		setSelectedSession(session)
		setSelectedDriver(null)
		setDrivers([])
		setDriverLaps(null)
		fetchDrivers(session.session_key)
	};

	const handleDriverClick = (driver: Driver) => {
		setSelectedDriver(driver)
		setDriverLaps(null)
		if (selectedSession) {
			fetchDriverLaps(selectedSession.session_key, driver.driver_number)
		}
	};

	return {
		years, events, sessions, drivers,
		selectedYear, selectedEvent, selectedSession, selectedDriver,
		driverLaps,
		loading, errors,
		handleYearChange, handleEventChange, handleSessionChange, handleDriverClick
	};

};
