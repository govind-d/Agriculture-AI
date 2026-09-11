import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';

// Pages (will be imported properly once created)
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import DiseaseDetection from './pages/DiseaseDetection';
import CropAdvisor from './pages/CropAdvisor';
import FertilizerAdvisor from './pages/FertilizerAdvisor';
import MarketPrices from './pages/MarketPrices';
import AIChatbot from './pages/AIChatbot';

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="disease-detection" element={<DiseaseDetection />} />
          <Route path="crops" element={<CropAdvisor />} />
          <Route path="fertilizer" element={<FertilizerAdvisor />} />
          <Route path="market" element={<MarketPrices />} />
          <Route path="chat" element={<AIChatbot />} />
        </Route>
      </Routes>

    </BrowserRouter>
  );
}

export default App;
