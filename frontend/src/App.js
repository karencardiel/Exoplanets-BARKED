import React, { useRef, useState, Suspense, useMemo } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import { OrbitControls, Text, Stars } from '@react-three/drei';
import * as THREE from 'three';
import axios from 'axios';
import './App.css';

// --- Data for our solar system
const solarSystemData = [
  { name: 'Mercury', texture: 'mercury.jpg', size: 0.38, distance: 10, speed: 0.04 },
  { name: 'Venus', texture: 'venus.jpg', size: 0.95, distance: 14, speed: 0.035 },
  { name: 'Earth', texture: 'earth.jpg', size: 1, distance: 20, speed: 0.03 },
  { name: 'Mars', texture: 'mars.jpg', size: 0.53, distance: 26, speed: 0.025 },
  { name: 'Jupiter', texture: 'jupiter.jpg', size: 4, distance: 40, speed: 0.02 },
  { name: 'Saturn', texture: 'saturn.jpg', size: 3.5, distance: 56, speed: 0.015, ring: { texture: 'saturn_ring_alpha.png', size: 2.5 } },
  { name: 'Uranus', texture: 'uranus.jpg', size: 2, distance: 70, speed: 0.01 },
  { name: 'Neptune', texture: 'neptune.jpg', size: 1.9, distance: 80, speed: 0.005 },
];

// --- 3D Components

function PlanetRing({ ring }) {
  const ringTexture = useLoader(THREE.TextureLoader, `/textures/${ring.texture}`);
  return (
    <mesh rotation-x={Math.PI / 2}>
      <ringGeometry args={[ring.size * 0.6, ring.size, 64]} />
      <meshBasicMaterial map={ringTexture} side={THREE.DoubleSide} transparent={true} />
    </mesh>
  );
}

// Component for a planet
function Planet({ 
  name,
  texture: texturePath, 
  size, 
  distance, 
  speed,
  ring,
  isCandidate = false,
  color = 'white' // Default color if none is provided
}) {
  const meshRef = useRef();
  const groupRef = useRef();
  const texture = useLoader(THREE.TextureLoader, `/textures/${texturePath}`);

  useFrame(({ clock }) => {
    const elapsedTime = clock.getElapsedTime();
    groupRef.current.position.x = Math.cos(elapsedTime * speed) * distance;
    groupRef.current.position.z = Math.sin(elapsedTime * speed) * distance;
    meshRef.current.rotation.y += 0.005;
  });

  return (
    <group ref={groupRef}>
      <mesh ref={meshRef} scale={isCandidate ? size * 1.2 : size} renderOrder={2}>
        <sphereGeometry args={[1, 32, 32]} />
        {/* Apply the color prop as a tint */}
        <meshStandardMaterial map={texture} color={color} />
        {ring && <PlanetRing ring={ring} />} {/* Conditionally render PlanetRing */}
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
      <sphereGeometry args={[6, 32, 32]} />
      <meshBasicMaterial map={texture} />
    </mesh>
  );
}

// Component for the orbit line
function OrbitLine({ distance, color = 'grey', thickness = 0.05 }) {
  return (
    <mesh rotation-x={Math.PI / 2} renderOrder={1}>
        <ringGeometry args={[distance - (thickness / 2), distance + (thickness / 2), 128]} />
        <meshBasicMaterial color={color} side={THREE.DoubleSide} />
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
        const BACKEND_URL = 'https://mi-proyecto-backend.onrender.com'; // Definimos la URL de Render aquí

        const response = await fetch(`${BACKEND_URL}/predict`, { // Usamos la variable para construir la URL
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(candidateParams),
        });

        if (!response.ok) {
          const errorData = await response.json();
          console.error('Backend error:', errorData);
          setPrediction(`Error: ${errorData.error || 'Unknown backend error'}`);
          return;
        }

        const data = await response.json();
        setPrediction(data);
      } catch (error) {
        console.error('Error during prediction (frontend network issue):', error);
        setPrediction('Error: Could not get prediction due to network or parsing issue.');
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate the candidate planet's color based on stellar temperature
  const candidateColor = useMemo(() => {
    const temp = candidateParams.StellarTemp_K;
    if (temp < 3500) return '#a8c5ff'; // Cool star -> Blue tint
    if (temp > 7000) return '#ffb878'; // Hot star -> Orange/Red tint
    return 'white'; // Normal (no tint)
  }, [candidateParams.StellarTemp_K]);

  const CANDIDATE_DISTANCE = 100;

  return (
    <div className="App">
      <div className="scene-container">
        <Canvas camera={{ position: [0, 40, 120], fov: 45 }}>
          <Suspense fallback={<Text color="white">Loading 3D Assets...</Text>}>
            <ambientLight intensity={0.2} />
            <pointLight position={[0, 0, 0]} intensity={1.5} />
            
            <Stars radius={300} depth={50} count={5000} factor={4} saturation={0} fade />

            <Sun />

            {solarSystemData.map(planet => <Planet key={planet.name} {...planet} />)}
            
            {/* This is our interactive candidate planet */}
            <Planet 
              name="Candidate"
              texture="moon.jpg"
              size={candidateParams.PlanetaryRadius_EarthRadii}
              distance={CANDIDATE_DISTANCE}
              speed={0.01}
              isCandidate={true}
              color={candidateColor} // Pass the dynamic color
            />

            {/* Add the orbit line for the candidate */}
            <OrbitLine distance={CANDIDATE_DISTANCE} color="#444" />

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
              max="25" 
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
              max="4000" 
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
              max="140" 
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
              max="16000" 
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
              {prediction.probabilities && Object.entries(prediction.probabilities).map(([key, value]) => (
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
