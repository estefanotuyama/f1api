import { DriverSessionResult } from "./types";

export const formatLapTime = (time: number) => {
	const minutes = Math.floor(time / 60);
	const seconds = (time % 60).toFixed(3);
	return `${minutes}:${seconds.padStart(6, "0")}`;
};

export const solveDriverStatus = (driver: DriverSessionResult) => {
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


export const formatTime = (driver: DriverSessionResult): string => {
	if (driver.position === 1) {
		const minutes = driver.duration / 60;

		if (minutes < 3) {
			// Qualifying-style lap (under 3 min) → mm:ss.sss
			const wholeMinutes = Math.floor(minutes);
			const seconds = driver.duration % 60;
			return `${wholeMinutes}:${seconds.toFixed(3).padStart(6, "0")}`;
		} else {
			// Race duration → h:mm:ss
			const hours = Math.floor(driver.duration / 3600);
			const mins = Math.floor((driver.duration % 3600) / 60);
			const secs = Math.floor(driver.duration % 60);
			return `${hours}:${mins.toString().padStart(2, "0")}:${secs
				.toString()
				.padStart(2, "0")}`;
		}
	} else {
		if (!driver.gap_to_leader) {
			return "—";
		}

		const gap = String(driver.gap_to_leader).trim().toUpperCase();

		if (gap.includes("LAP")) {
			return gap;
		}

		const numericGap = gap.replace(/[^\d.]/g, ""); // keep only numbers and dot
		return `+${numericGap}s`;
	}
};
