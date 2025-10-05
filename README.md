# Finding Exoplanets: Exoplanet Simulator and Predictor

![Exoplanet Simulator](https://i.imgur.com/iFhaeEz.png)

## Overview

Exoplanets-BARKED is a project developed for the NASA Space App Challenge 2025 that combines an interactive 3D simulation of planetary systems with a Machine Learning model to predict exoplanet types. The application allows users to adjust the properties of a candidate exoplanet and visualize it in a 3D environment, while an AI backend classifies the exoplanet based on its characteristics.

## Features

*   **Interactive 3D Simulation:** Visualize the Sun, planets of our solar system, and a candidate exoplanet in a dynamic 3D environment.
*   **Parameter Control:** Adjust key properties of the candidate exoplanet (radius, orbital period, transit duration, stellar temperature) through an intuitive user interface.
*   **Exoplanet Prediction:** A Machine Learning model classifies the candidate exoplanet into categories such as "Earth-like", "Gas Giant", etc., and displays the probabilities for each class.
*   **Client-Server Architecture:** Frontend developed with React for the user interface and visualization, and a Flask backend for the Machine Learning logic.

## Project Structure

```
Exoplanets-BARKED/
├── app.py                      # Flask backend for the prediction API.
├── backend_log.txt             # Backend activity log.
├── exoplanet_model.joblib      # Pre-trained Machine Learning model.
├── feature_columns.joblib      # Feature columns used by the model.
├── label_encoder.joblib        # Label encoder for exoplanet classes.
├── requirements.txt            # Python dependencies for the backend and ML.
├── README.md                   # This file.
├── frontend/                   # React application directory (frontend).
│   ├── public/                 # Static files (index.html, 3D textures).
│   ├── src/                    # React source code (App.js, 3D components).
│   ├── package.json            # Node.js dependencies for the frontend.
│   └── ...
├── Pre-process/                # Scripts for data preprocessing and model training.
│   ├── ml-exo-mdl.py           # ML model training script.
│   └── data/                   # Data quality and filtering scripts.
├── raw_sample.csv              # Raw exoplanet data.
├── preprocessed_sample.csv     # Preprocessed exoplanet data.
├── filtered_sample.csv         # Filtered exoplanet data.
└── templates/                  # HTML templates (not directly used by the React frontend).
```

## Technologies Used

**Backend & Machine Learning:**
*   **Python:** Main programming language.
*   **Flask:** Web microframework for the API.
*   **Flask-CORS:** CORS handling.
*   **Scikit-learn:** ML tools (preprocessing, model selection).
*   **XGBoost:** ML classification algorithm.
*   **Pandas & NumPy:** Data manipulation and computation.
*   **Joblib:** Model serialization.

**Frontend:**
*   **JavaScript:** Main programming language.
*   **React:** Library for building user interfaces.
*   **Three.js:** Library for 3D graphics (via `@react-three/fiber`).
*   **@react-three/fiber & @react-three/drei:** Three.js integration with React.
*   **npm:** Node.js package manager.

## Installation and Execution

Follow these steps to set up and run the project on your local machine.

### Prerequisites

Make sure you have the following installed:
*   **Python 3.8+**
*   **Node.js** (includes npm)

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/Exoplanets-BARKED.git
    cd Exoplanets-BARKED
    ```
    *(Replace `https://github.com/your-username/Exoplanets-BARKED.git` with the actual URL of your repository)*

2.  **Install Backend Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Frontend Dependencies:**
    ```bash
    cd frontend
    npm install
    cd ..
    ```

4.  **Run the Backend:**
    Open a new terminal in the project root directory (`Exoplanets-BARKED/`) and execute:
    ```bash
    python app.py
    ```
    The backend will run on `http://127.0.0.1:5000`.

5.  **Run the Frontend:**
    Open *another* new terminal in the project root directory (`Exoplanets-BARKED/`) and execute:
    ```bash
    cd frontend
    npm start
    ```
    The frontend will automatically open in your browser (usually at `http://localhost:3000`).

## Usage

Once the application is running:
1.  You will see a 3D simulation of a solar system.
2.  In the control panel on the left, adjust the parameters of the "Candidate" exoplanet using the sliders.
3.  Click the "Predict Candidate" button to send the parameters to the AI model.
4.  The prediction and probabilities will be displayed in the panel.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
