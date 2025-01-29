import { useRef } from 'react';
import { Mesh } from 'three';
import { Color } from 'three';
import { useFrame } from '@react-three/fiber';

const Scene = () => {
	console.log('scene init');
	const meshRef = useRef<Mesh>(null);
	const rotationSpeed = 0.01;

	useFrame(() => {
		if (meshRef.current) {
			meshRef.current.rotation.y += rotationSpeed;
		}
	});

	return (
		<>
			{/* Main object */}
			<mesh ref={meshRef}>
				<boxGeometry args={[1, 1, 1]} />
				<meshToonMaterial
					color={new Color('#FF9B50')}
					emissive={new Color('#FF9B50')}
					emissiveIntensity={0.2}
				/>
			</mesh>
			{/* Outline mesh */}
			<mesh ref={meshRef} scale={1.05}>
				<boxGeometry args={[1, 1, 1]} />
				<meshBasicMaterial color="black" side={2} transparent opacity={0.8} />
			</mesh>
		</>
	);
};
export default Scene;
