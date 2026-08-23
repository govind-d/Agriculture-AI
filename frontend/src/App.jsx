import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';

// Pages (will be imported properly once created)
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';

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
          {/* We will add other routes here later */}
          <Route path="disease-detection" element={<div className="animate-fade-in"><h2>Disease Detection (Coming Soon)</h2></div>} />
          <Route path="crops" element={<div className="animate-fade-in"><h2>Crop Advisor (Coming Soon)</h2></div>} />
          <Route path="fertilizer" element={<div className="animate-fade-in"><h2>Fertilizer (Coming Soon)</h2></div>} />
          <Route path="market" element={<div className="animate-fade-in"><h2>Market Prices (Coming Soon)</h2></div>} />
          <Route path="chat" element={<div className="animate-fade-in"><h2>AI Chatbot (Coming Soon)</h2></div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
