import React from 'react';

const Dashboard = () => {
  return (
    <div className="animate-fade-in">
      <h1 style={{ marginBottom: '2rem' }}>Welcome to AgriGuardian</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        <div className="card">
          <h3>Your Farms</h3>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>Loading farm data...</p>
        </div>
        
        <div className="card">
          <h3>Recent Detections</h3>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>No recent disease detections.</p>
        </div>
        
        <div className="card">
          <h3>Weather Overview</h3>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>Fetching local weather...</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
