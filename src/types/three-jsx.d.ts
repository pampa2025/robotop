import * as THREE from 'three';

declare global {
	namespace JSX {
		interface IntrinsicElements {
			group: THREE.Group;
			primitive: { object: THREE.Object3D };
			skinnedMesh: THREE.SkinnedMesh;
		}
	}
}
