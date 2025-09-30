import React, { useEffect } from 'react';
import toast, { type Toast } from 'react-hot-toast';

const WelcomeMessage: React.FC = () => {
	useEffect(() => {
		const toastId = 'welcome-toast';

		toast(
			(t: Toast) => (
				<div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
					<span>🚀 Welcome to RacePace! Check out session results and compare driver lap times instantly.</span>
					<button
						onClick={() => toast.dismiss(t.id)}
						style={{
							border: '1px solid white',
							background: 'transparent',
							color: 'white',
							borderRadius: '4px',
							padding: '6px 10px',
							cursor: 'pointer',
						}}
					>
						Dismiss
					</button>
				</div>
			),
			{
				id: toastId,
				duration: 80000,
				position: 'bottom-right',
				style: {
					background: '#363636',
					color: '#eaeaea',
				},
			}
		);
	}, []);

	return null;
};

export default WelcomeMessage;
