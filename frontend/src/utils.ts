export const formatLapTime = (time: number) => {
	const minutes = Math.floor(time / 60);
	const seconds = (time % 60).toFixed(3);
	return `${minutes}:${seconds.padStart(6, "0")}`;
};

