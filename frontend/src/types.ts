// Types based on API models
export interface Event {
	meeting_key: number
	circuit_key: number
	location: string
	country_name: string
	circuit_name: string
	meeting_official_name: string
	year: number
}

export interface F1Session {
	location: string
	meeting_key: number
	session_key: number
	session_type: string
	session_name: string
	date: string
}

export interface Driver {
	session_key: number
	first_name: string
	last_name: string
	name_acronym: string
	driver_number: number
	team: string
	headshot_url: string
}

export interface LapData {
	lap_number: number
	time: number
	speed_trap: number
	is_pit_out_lap: boolean
	compound: string
}

export interface DriverLapsData {
	driver_number: number
	first_name: string
	last_name: string
	team: string
	headshot_url: string
	laps: LapData[]
}

export interface DriverSessionResult {
	position: number
	team: string
	first_name: string
	last_name: string
	number_of_laps: number
	gap_to_leader: string
	duration: number
	dnf: boolean
	dns: boolean
	dsq: boolean
}

export interface SessionResultData {
	result: DriverSessionResult[]
}

export interface MultipleDriverLapsData {
	[driverNumber: number]: DriverLapsData
}

export type TeamColors = Record<string, string>;
