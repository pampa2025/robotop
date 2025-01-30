import { Group, Mesh, MeshToonMaterial, Color, Vector3, Object3DEventMap } from 'three';
import { useAnimations, useGLTF, Grid, Html } from '@react-three/drei';
import { useEffect, useRef, useState } from 'react';

export function RobotArm() {
  const group = useRef<Group<Object3DEventMap>>(null);
  const animationFrameId = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, []);
  const { scene, animations } = useGLTF('/models/db_robotarm_animate-transformed.glb');
  const { actions } = useAnimations(animations, group);
  const [selectedMesh, setSelectedMesh] = useState<Mesh | null>(null);
  const [color, setColor] = useState('#ffffff');
  const [pickerPosition, setPickerPosition] = useState({ x: 0, y: 0 });

  const handleColorChange = (newColor: string) => {
    setColor(newColor);
    if (selectedMesh && selectedMesh.material instanceof MeshToonMaterial) {
      selectedMesh.material.color.set(newColor);
      selectedMesh.material.emissive.set(newColor).multiplyScalar(0.2);
      selectedMesh.material.needsUpdate = true;
    }
  };

  const handleClick = (event: any) => {
    event.stopPropagation();
    const mesh = event.object;
    if (mesh instanceof Mesh) {
      // Stop all animations
      Object.values(actions).forEach(action => {
        if (action) action.stop();
      });

      // Reset previous selection highlight
      if (selectedMesh && selectedMesh.material instanceof MeshToonMaterial) {
        selectedMesh.material.emissiveIntensity = 0.3;
        selectedMesh.material.emissive.multiplyScalar(0.2);
        selectedMesh.material.opacity = 1;
        selectedMesh.material.transparent = false;
      }

      // Set mesh and color
      setSelectedMesh(mesh);
      if (mesh.material instanceof MeshToonMaterial) {
        setColor('#' + mesh.material.color.getHexString());
        // Enhanced highlight effect
        mesh.material.emissiveIntensity = 3;
        mesh.material.emissive.copy(mesh.material.color);
        mesh.material.opacity = 0.9;
        mesh.material.transparent = true;
        
        // Add pulsing effect
        const animatePulse = () => {
          if (mesh === selectedMesh) {
            const intensity = 2.5 + Math.sin(Date.now() * 0.005) * 0.5;
            mesh.material.emissiveIntensity = intensity;
            requestAnimationFrame(animatePulse);
          }
        };
        animatePulse();
      }

      // Get world position for the color picker
      const worldPos = new Vector3();
      mesh.getWorldPosition(worldPos);
      setPickerPosition({ x: worldPos.x, y: worldPos.y + 0.5 });
    }
  };

  // Update the Done button handler
  return (
      <>
        <color attach="background" args={['#f0f0f0']} />
        <Grid
          position={[0, -0.01, 0]}
          args={[10, 10]}
          cellSize={0.5}
          cellThickness={0.5}
          cellColor="#6f6f6f"
          sectionSize={2}
          sectionThickness={1}
          sectionColor="#9d4b4b"
          fadeDistance={30}
          fadeStrength={1}
          followCamera={false}
        />
        <group ref={group} dispose={null} onClick={handleClick}>
          <primitive object={scene} />
        </group>
        {selectedMesh && (
          <Html
            position={[pickerPosition.x, pickerPosition.y, 0]}
            wrapperClass="html-label"
            occlude={[scene]}
            zIndexRange={[0, 100]}
          >
            <div style={{
              background: 'white',
              padding: '10px',
              borderRadius: '5px',
              display: 'flex',
              gap: '5px',
              alignItems: 'center',
              boxShadow: '0 0 10px rgba(0,0,0,0.2)',
              pointerEvents: 'auto'
            }}>
              <input
                type="color"
                value={color}
                onChange={(e) => handleColorChange(e.target.value)}
                style={{ cursor: 'pointer' }}
              />
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  if (selectedMesh && selectedMesh.material instanceof MeshToonMaterial) {
                    selectedMesh.material.emissiveIntensity = 0.3;
                    selectedMesh.material.emissive.copy(selectedMesh.material.color).multiplyScalar(0.2);
                  }
                  Object.values(actions).forEach(action => {
                    if (action) action.play();
                  });
                  setSelectedMesh(null);
                }}
                style={{ cursor: 'pointer' }}
              >
                Done
              </button>
            </div>
          </Html>
        )}
      </>
    );
}