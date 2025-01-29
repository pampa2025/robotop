import './App.css';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import Scene from './components/Scene';

function App() {
	return (
		<div style={{ width: '100vw', height: '100vh' }}>
			<Canvas>
				<OrbitControls />
				<ambientLight intensity={0.5} />
				<directionalLight position={[10, 10, 5]} intensity={1} />
				<Scene />
			</Canvas>
		</div>
	);
}

export default App;
