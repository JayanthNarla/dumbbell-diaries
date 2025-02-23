# Dumbbell Diaries

Dumbbell Diaries is an innovative fitness tracking and social platform designed to help users monitor workouts, manage nutrition, track progress, and connect with a community of fitness enthusiasts. The project is composed of two main parts:

- **Backend API** powered by FastAPI for robust server-side logic.
- **Frontend Mobile App** built with Expo and React Native for an engaging, cross-platform user experience.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Getting Started](#getting-started)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Features](#features)
- [Development Scripts](#development-scripts)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

Dumbbell Diaries is crafted to support users in tracking their fitness journeys. Key functionalities include:

- **Workout Tracking:** Log and manage workouts.
- **Nutrition & Meal Planning:** Keep track of food intake and receive nutritional advice.
- **Progress Monitoring:** Record measurements and fitness goals.
- **Social Engagement:** Interact with a community of fitness enthusiasts.
- **Custom Theming & Animations:** Enjoy a polished UI with support for light and dark modes, animated components, and interactive features like parallax scrolling.

The backend API handles user authentication, data management, and business logic, while the frontend provides a mobile-first, intuitive interface.

---

## Project Structure

### Backend

The backend is built with FastAPI and includes:

- **Entry Point:** `backend/app/main.py`  
  Runs the FastAPI application, configures CORS, and includes multiple routers for handling endpoints such as `auth`, `users`, `food`, and `workouts`.
- **API Endpoints:** Organized under `backend/app/api/v1/endpoints/` (e.g., `auth.py`, `users.py`, `goals.py`, `notifications.py`, etc.).
- **Models, Schemas & Services:** Various directories (like `models`, `schemas`, `services`, and `utils`) encapsulate the core logic, data models, and business rules.
- **Scripts:** Additional scripts for tasks like seeding data or setting up integrations can be found in `backend/scripts/`.

### Frontend

The frontend is an Expo app utilizing React Native and modern routing techniques:

- **File-Based Routing:** Screens are defined in the `frontend/app/` directory using Expo Router, with sample screens like `index.tsx` (Home) and `explore.tsx`.
- **UI Components & Theming:** Custom components such as `ThemedText`, `ThemedView`, `Collapsible`, and `ParallaxScrollView` enable dynamic theming and a modern look and feel.
- **Animations & Interactivity:** Components like `HelloWave` use `react-native-reanimated` for smooth animations.
- **Development Script:** The `frontend/scripts/reset-project.js` script offers an easy way to reset the app to a blank state, moving the current implementation to `app-example` and generating a new `app` directory.
- **Configuration Files:** The project is configured using files like `app.json`, `package.json`, and `tsconfig.json`.

---

## Getting Started

### Backend Setup

1. **Prerequisites:**
   - Python 3.9 or above.
   - [pip](https://pip.pypa.io/en/stable/) for dependency management.

2. **Setup Environment:**
   - Create a virtual environment:
     ```bash
     python -m venv env
     ```
   - Activate the virtual environment:
     - **Windows:** `env\Scripts\activate`
     - **macOS/Linux:** `source env/bin/activate`

3. **Install Dependencies:**
   - Install FastAPI, Uvicorn, and other dependencies (if a `requirements.txt` is available, use it; otherwise install manually):
     ```bash
     pip install fastapi uvicorn python-multipart
     ```
   - Install dependencies from `requirements.txt`:
     ```bash
     pip install -r requirements.txt
     ```

4. **Run the Server:**
   - Navigate to the `backend` directory:
     ```bash
     cd backend
     ```
   - Launch the backend API with Uvicorn:
     ```bash
     uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
     ```
   - The API should be accessible at [http://localhost:8000](http://localhost:8000).

### Frontend Setup

1. **Prerequisites:**
   - [Node.js](https://nodejs.org/) (LTS version recommended).
   - Expo CLI installed globally (optional):
     ```bash
     npm install -g expo-cli
     ```

2. **Install Dependencies:**
   - Navigate to the `frontend` directory and install dependencies:
     ```bash
     npm install
     ```

3. **Running the App:**
   - Launch the Expo development server:
     ```bash
     npx expo start
     ```
   - Follow the on-screen instructions to open the app on an Android emulator, iOS simulator, or via Expo Go on your physical device.

4. **Resetting the Project:**
   - If you need to start with a fresh slate, run:
     ```bash
     npm run reset-project
     ```
   - This script moves the current code from the `app` directory to `app-example` and creates a new, minimal `app` directory.

---

## Features

- **User Authentication & Management:** Secure endpoints for user login and registration.
- **Workout and Nutrition Tracking:** Log and monitor workouts, food intake, and fitness progress.
- **Custom UI Components:** Reusable components with theming support for light and dark modes.
- **Smooth Animations:** Engaging animations powered by `react-native-reanimated`.
- **File-Based Routing:** Easily structured navigation using Expo Router.
- **Cross-Origin Setup:** Backend configured with CORS middleware to support seamless integration with the frontend.
- **Community Integration:** Plans for social features allow users to interact and share progress.

---

## Development Scripts

### Frontend

- **Start Development Server:**  
  `npm start`  
  or  
  `npx expo start`

- **Platform Specific Commands:**  
  `npm run android` – Start on Android emulator/device.  
  `npm run ios` – Start on iOS simulator/device.  
  `npm run web` – Start in a web browser.

- **Reset Project:**  
  `npm run reset-project`  
  Resets the `app` directory by moving current files to `app-example` and creating a fresh `app`.

- **Run Tests:**  
  `npm test` – Execute Jest tests for frontend components.

### Backend

- **Start the API Server:**
  ```bash
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```

---

## Technologies Used

- **Backend:**
  - [FastAPI](https://fastapi.tiangolo.com/) – A modern, fast (high-performance) web framework for building APIs.
  - [Uvicorn](https://www.uvicorn.org/) – An ASGI server for serving FastAPI applications.
  - Python Standard Libraries for file and script management.

- **Frontend:**
  - [Expo](https://expo.dev/) – A framework and platform for universal React applications.
  - [React Native](https://reactnative.dev/) – A framework for building native apps using React.
  - [Expo Router](https://expo.github.io/router/) – File-based routing built for Expo.
  - [React Native Reanimated](https://docs.swmansion.com/react-native-reanimated/) – A library for complex animations.
  - [Expo Vector Icons](https://docs.expo.dev/guides/icons/), [Expo Blur](https://docs.expo.dev/versions/latest/sdk/blur/) for UI enhancements.

---

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch:**
   ```bash
   git checkout -b feature/YourNewFeature
   ```
3. **Commit Your Changes:**  
   Provide clear and concise commit messages.
4. **Push to the Branch:**  
   ```bash
   git push origin feature/YourNewFeature
   ```
5. **Open a Pull Request:**  
   Describe your changes and the motivation behind them.

Please make sure to adhere to the existing code style and conventions. For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute as needed.

---

## Acknowledgments

- Special thanks to the [Expo](https://expo.dev/) and [FastAPI](https://fastapi.tiangolo.com/) communities for their excellent documentation and support.
- Inspiration from various fitness apps and social platforms.
- Developers and contributors who continuously improve this project.

---

Happy coding and stay fit!
