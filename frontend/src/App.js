import React, { useRef, useState, Suspense } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import { OrbitControls, Text, Stars } from '@react-three/drei';
import * as THREE from 'three';
import axios from 'axios';
import './App.css';

// --- Data for our solar system
// Textures will be loaded from the /public/textures/ folder
const solarSystemData = [
  { name: 'Mercury', texture: 'mercury.jpg', size: 0.38, distance: 5, speed: 0.04 },
  { name: 'Venus', texture: 'venus.jpg', size: 0.95, distance: 7, speed: 0.035 },
  { name: 'Earth', texture: 'earth.jpg', size: 1, distance: 10, speed: 0.03 },
  { name: 'Mars', texture: 'mars.jpg', size: 0.53, distance: 13, speed: 0.025 },
  { name: 'Jupiter', texture: 'jupiter.jpg', size: 4, distance: 20, speed: 0.02 },
  { name: 'Saturn', texture: 'saturn.jpg', size: 3.5, distance: 28, speed: 0.015, ring: { texture: 'saturn_ring_alpha.png', size: 6 } },
  { name: 'Uranus', texture: 'uranus.jpg', size: 2, distance: 35, speed: 0.01 },
  { name: 'Neptune', texture: 'neptune.jpg', size: 1.9, distance: 40, speed: 0.005 },
];

// --- 3D Components

// Component for a planet
function Planet({ 
  name,
  texture: texturePath, 
  size, 
  distance, 
  speed,
  ring,
  isCandidate = false 
}) {
  const meshRef = useRef();
  const groupRef = useRef();
  const texture = useLoader(THREE.TextureLoader, `/textures/${texturePath}`);
  
  let ringTexture;
  if (ring) {
    ringTexture = useLoader(THREE.TextureLoader, `/textures/${ring.texture}`);
  }

  useFrame(({ clock }) => {
    const elapsedTime = clock.getElapsedTime();
    groupRef.current.position.x = Math.cos(elapsedTime * speed) * distance;
    groupRef.current.position.z = Math.sin(elapsedTime * speed) * distance;
    meshRef.current.rotation.y += 0.005;
  });

  return (
    <group ref={groupRef}>
      <mesh ref={meshRef} scale={isCandidate ? size * 1.2 : size}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshStandardMaterial map={texture} />
        {ring && (
          <mesh rotation-x={Math.PI / 2}>
            <ringGeometry args={[ring.size * 0.6, ring.size, 64]} />
            <meshBasicMaterial map={ringTexture} side={THREE.DoubleSide} transparent={true} />
          </mesh>
        )}
      </mesh>
      <Text position={[0, size + 0.5, 0]} fontSize={0.5} color="white" anchorX="center">
        {name}
      </Text>
    </group>
  );
}

// Component for the Sun
function Sun() {
  const texture = useLoader(THREE.TextureLoader, '/textures/sun.jpg');
  return (
    <mesh>
      <sphereGeometry args={[3, 32, 32]} />
      <meshBasicMaterial map={texture} />
    </mesh>
  );
}

// --- Main App Component
function App() {
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [candidateParams, setCandidateParams] = useState({
    'OrbitalPeriod_days': 365,
    'TransitDuration_hrs': 2,
    'PlanetaryRadius_EarthRadii': 1,
    'StellarTemp_K': 5778,
  });

  const handleParamChange = (param, value) => {
    setCandidateParams(prevParams => ({
      ...prevParams,
      [param]: parseFloat(value)
    }));
  };

  const handlePredict = async () => {
    setIsLoading(true);
    setPrediction(null);
    try {
      const response = await axios.post('http://127.0.0.1:5000/predict', candidateParams);
      setPrediction(response.data);
    } catch (error) {
      console.error("Error making prediction:", error);
      setPrediction({ prediction: 'Error', probabilities: {} });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="scene-container">
        <Canvas camera={{ position: [0, 20, 50], fov: 45 }}>
          <Suspense fallback={<Text color="white">Loading 3D Assets...</Text>}>
            <ambientLight intensity={0.2} />
            <pointLight position={[0, 0, 0]} intensity={1.5} />
            
            <Stars radius={200} depth={50} count={5000} factor={4} saturation={0} fade />

            <Sun />

            {solarSystemData.map(planet => <Planet key={planet.name} {...planet} />)}
            
            {/* This is our interactive candidate planet */}
            <Planet 
              name="Candidate"
              texture="moon.jpg"
              size={candidateParams.PlanetaryRadius_EarthRadii}
              distance={50}
              speed={0.02}
              isCandidate={true}
            />

          </Suspense>
          <OrbitControls />
        </Canvas>
      </div>
      <div className="ui-panel">
        <h1>Exoplanet Simulator</h1>
        <p>
          Control the properties of the 'Candidate' exoplanet using the sliders below and then press 'Predict' to classify it.
        </p>
        
        <div className="controls">
          <div className="control-item">
            <label>Planetary Radius (Earths)</label>
            <input 
              type="range" 
              min="0.1" 
              max="15" 
              step="0.1" 
              value={candidateParams.PlanetaryRadius_EarthRadii}
              onChange={(e) => handleParamChange('PlanetaryRadius_EarthRadii', e.target.value)}
            />
            <span>{candidateParams.PlanetaryRadius_EarthRadii}</span>
          </div>
          <div className="control-item">
            <label>Orbital Period (days)</label>
            <input 
              type="range" 
              min="1" 
              max="2000" 
              step="1" 
              value={candidateParams.OrbitalPeriod_days}
              onChange={(e) => handleParamChange('OrbitalPeriod_days', e.target.value)}
            />
            <span>{candidateParams.OrbitalPeriod_days}</span>
          </div>
          <div className="control-item">
            <label>Transit Duration (hours)</label>
            <input 
              type="range" 
              min="0.1" 
              max="24" 
              step="0.1" 
              value={candidateParams.TransitDuration_hrs}
              onChange={(e) => handleParamChange('TransitDuration_hrs', e.target.value)}
            />
            <span>{candidateParams.TransitDuration_hrs}</span>
          </div>
          <div className="control-item">
            <label>Stellar Temperature (K)</label>
            <input 
              type="range" 
              min="2000" 
              max="15000" 
              step="100" 
              value={candidateParams.StellarTemp_K}
              onChange={(e) => handleParamChange('StellarTemp_K', e.target.value)}
            />
            <span>{candidateParams.StellarTemp_K}</span>
          </div>
        </div>

        <button onClick={handlePredict} disabled={isLoading}>
          {isLoading ? 'Predicting...' : 'Predict Candidate'}
        </button>

        {prediction && (
          <div className="prediction-result">
            <h2>Prediction: {prediction.prediction}</h2>
            <ul>
              {Object.entries(prediction.probabilities).map(([key, value]) => (
                <li key={key}>{key}: {(value * 100).toFixed(2)}%</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
