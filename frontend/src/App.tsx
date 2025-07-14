"use client"

import { useState, useEffect } from "react"
import "./App.css"

// Types based on API models
interface Event {
  meeting_key: number
  circuit_key: number
  location: string
  country_name: string
  circuit_name: string
  meeting_official_name: string
  year: number
}

interface F1Session {
  location: string
  meeting_key: number
  session_key: number
  session_type: string
  session_name: string
  date: string
}

interface Driver {
  session_key: number
  first_name: string
  last_name: string
  name_acronym: string
  number: number
  team: string
  headshot_url: string
}

interface LapData {
  lap_number: number
  time: number
  speed_trap: number
  is_pit_out_lap: boolean
  compound: string
}

interface DriverLapsData {
  driver_number: number
  first_name: string
  last_name: string
  team: string
  headshot_url: string
  laps: LapData[]
}

const API_BASE_URL = "http://localhost:8000"

function App() {
  // State for dropdowns
  const [years, setYears] = useState<number[]>([])
  const [events, setEvents] = useState<Event[]>([])
  const [sessions, setSessions] = useState<F1Session[]>([])
  const [drivers, setDrivers] = useState<Driver[]>([])

  // State for selections
  const [selectedYear, setSelectedYear] = useState<number | null>(null)
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null)
  const [selectedSession, setSelectedSession] = useState<F1Session | null>(null)
  const [selectedDriver, setSelectedDriver] = useState<Driver | null>(null)

  // State for lap data
  const [driverLaps, setDriverLaps] = useState<DriverLapsData | null>(null)

  // Loading and error states
  const [loading, setLoading] = useState({
    years: false,
    events: false,
    sessions: false,
    drivers: false,
    laps: false,
  })
  const [errors, setErrors] = useState({
    years: "",
    events: "",
    sessions: "",
    drivers: "",
    laps: "",
  })

  // Fetch available years on component mount
  useEffect(() => {
    fetchYears()
  }, [])

  const fetchYears = async () => {
    setLoading((prev) => ({ ...prev, years: true }))
    setErrors((prev) => ({ ...prev, years: "" }))

    try {
      const response = await fetch(`${API_BASE_URL}/events/years/`)
      if (!response.ok) throw new Error("Failed to fetch years")

      const data = await response.json()
      setYears(data)
    } catch (error) {
      setErrors((prev) => ({ ...prev, years: "Failed to load years" }))
    } finally {
      setLoading((prev) => ({ ...prev, years: false }))
    }
  }

  const fetchEvents = async (year: number) => {
    setLoading((prev) => ({ ...prev, events: true }))
    setErrors((prev) => ({ ...prev, events: "" }))

    try {
      const response = await fetch(`${API_BASE_URL}/events/${year}`)
      if (!response.ok) throw new Error("Failed to fetch events")

      const data = await response.json()
      if (data.length === 0) {
        setErrors((prev) => ({ ...prev, events: "No events available for this year" }))
      }
      setEvents(data)
    } catch (error) {
      setErrors((prev) => ({ ...prev, events: "Failed to load events" }))
    } finally {
      setLoading((prev) => ({ ...prev, events: false }))
    }
  }

  const fetchSessions = async (meetingKey: number) => {
    setLoading((prev) => ({ ...prev, sessions: true }))
    setErrors((prev) => ({ ...prev, sessions: "" }))

    try {
      const response = await fetch(`${API_BASE_URL}/sessions/${meetingKey}`)
      if (!response.ok) throw new Error("Failed to fetch sessions")

      const data = await response.json()
      if (data.length === 0) {
        setErrors((prev) => ({ ...prev, sessions: "No sessions available for this event" }))
      }
      setSessions(data)
    } catch (error) {
      setErrors((prev) => ({ ...prev, sessions: "Failed to load sessions" }))
    } finally {
      setLoading((prev) => ({ ...prev, sessions: false }))
    }
  }

  const fetchDrivers = async (sessionKey: number) => {
    setLoading((prev) => ({ ...prev, drivers: true }))
    setErrors((prev) => ({ ...prev, drivers: "" }))

    try {
      const response = await fetch(`${API_BASE_URL}/drivers/${sessionKey}`)
      if (!response.ok) throw new Error("Failed to fetch drivers")

      const data = await response.json()
      if (data.length === 0) {
        setErrors((prev) => ({ ...prev, drivers: "No drivers available for this session" }))
      }
      setDrivers(data)
    } catch (error) {
      setErrors((prev) => ({ ...prev, drivers: "Failed to load drivers" }))
    } finally {
      setLoading((prev) => ({ ...prev, drivers: false }))
    }
  }

  const fetchDriverLaps = async (sessionKey: number, driverNumber: number) => {
    setLoading((prev) => ({ ...prev, laps: true }))
    setErrors((prev) => ({ ...prev, laps: "" }))

    try {
      const response = await fetch(`${API_BASE_URL}/laps/${sessionKey}/${driverNumber}`)
      if (!response.ok) throw new Error("Failed to fetch lap data")

      const data = await response.json()
      if (!data.laps || data.laps.length === 0) {
        setErrors((prev) => ({ ...prev, laps: "No lap data available for this driver" }))
      }
      setDriverLaps(data)
    } catch (error) {
      setErrors((prev) => ({ ...prev, laps: "Failed to load lap data" }))
    } finally {
      setLoading((prev) => ({ ...prev, laps: false }))
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
  }

  const handleEventChange = (event: Event) => {
    setSelectedEvent(event)
    setSelectedSession(null)
    setSelectedDriver(null)
    setSessions([])
    setDrivers([])
    setDriverLaps(null)
    fetchSessions(event.meeting_key)
  }

  const handleSessionChange = (session: F1Session) => {
    setSelectedSession(session)
    setSelectedDriver(null)
    setDrivers([])
    setDriverLaps(null)
    fetchDrivers(session.session_key)
  }

  const handleDriverClick = (driver: Driver) => {
    setSelectedDriver(driver)
    setDriverLaps(null)
    if (selectedSession) {
      fetchDriverLaps(selectedSession.session_key, driver.number)
    }
  }

  const formatLapTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = (time % 60).toFixed(3)
    return `${minutes}:${seconds.padStart(6, "0")}`
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Formula 1 Data Explorer</h1>
      </header>

      <main className="main-content">
        {/* Dropdown Controls */}
        <div className="controls">
          {/* Year Dropdown */}
          <div className="dropdown-container">
            <label htmlFor="year-select">Year</label>
            <select
              id="year-select"
              value={selectedYear || ""}
              onChange={(e) => handleYearChange(Number(e.target.value))}
              disabled={loading.years}
            >
              <option value="">Select Year</option>
              {years.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
            {loading.years && <div className="loading">Loading...</div>}
            {errors.years && <div className="error">{errors.years}</div>}
          </div>

          {/* Event Dropdown */}
          <div className="dropdown-container">
            <label htmlFor="event-select">Event</label>
            <select
              id="event-select"
              value={selectedEvent?.meeting_key || ""}
              onChange={(e) => {
                const event = events.find((ev) => ev.meeting_key === Number(e.target.value))
                if (event) handleEventChange(event)
              }}
              disabled={!selectedYear || loading.events}
            >
              <option value="">Select Event</option>
              {events.map((event) => (
                <option key={event.meeting_key} value={event.meeting_key}>
                  {event.circuit_name}, {event.country_name}
                </option>
              ))}
            </select>
            {loading.events && <div className="loading">Loading...</div>}
            {errors.events && <div className="error">{errors.events}</div>}
          </div>

          {/* Session Dropdown */}
          <div className="dropdown-container">
            <label htmlFor="session-select">Session</label>
            <select
              id="session-select"
              value={selectedSession?.session_key || ""}
              onChange={(e) => {
                const session = sessions.find((s) => s.session_key === Number(e.target.value))
                if (session) handleSessionChange(session)
              }}
              disabled={!selectedEvent || loading.sessions}
            >
              <option value="">Select Session</option>
              {sessions.map((session) => (
                <option key={session.session_key} value={session.session_key}>
                  {session.session_name}
                </option>
              ))}
            </select>
            {loading.sessions && <div className="loading">Loading...</div>}
            {errors.sessions && <div className="error">{errors.sessions}</div>}
          </div>
        </div>

        {/* Drivers Display */}
        {selectedSession && (
          <div className="drivers-section">
            <h2>Drivers in {selectedSession.session_name}</h2>
            {loading.drivers && <div className="loading">Loading drivers...</div>}
            {errors.drivers && <div className="error">{errors.drivers}</div>}

            <div className="drivers-grid">
              {drivers.map((driver) => (
                <div
                  key={`${driver.session_key}-${driver.number}`}
                  className={`driver-card ${selectedDriver?.number === driver.number ? "selected" : ""}`}
                  onClick={() => handleDriverClick(driver)}
                >
                  <img
                    src={driver.headshot_url || "/placeholder.jpeg"}
                    alt={`${driver.first_name} ${driver.last_name}`}
                    className="driver-image"
                    onError={(e) => {
                      ;(e.target as HTMLImageElement).src = "/placeholder.jpeg?height=80&width=80"
                    }}
                  />
                  <div className="driver-info">
                    <h3>
                      {driver.first_name} {driver.last_name}
                    </h3>
                    <p className="driver-number">#{driver.number}</p>
                    <p className="driver-team">{driver.team}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Lap Data Display */}
        {selectedDriver && (
          <div className="lap-data-section">
            <h2>
              Lap Data for {selectedDriver.first_name} {selectedDriver.last_name}
              <br />
                <p className="note-paragraph">
                  Note: A lap time of 0:00.000 means the OpenF1 API did not provide lap data for this lap.
                </p>
            </h2>
            {loading.laps && <div className="loading">Loading lap data...</div>}
            {errors.laps && <div className="error">{errors.laps}</div>}

            {driverLaps && driverLaps.laps.length > 0 && (
              <div className="lap-data-table">
                <table>
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
        )}
      </main>
    </div>
  )
}

export default App
