import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import { Mesh } from 'three'
import { useStore } from '../store'

const Scene = () => {
  const meshRef = useRef<Mesh>(null)
  const rotation = useStore((state) => state.rotation)
  const setRotation = useStore((state) => state.setRotation)

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y = rotation
      setRotation(rotation + 0.01)
    }
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}

export default Scene