import React, { useState, useEffect } from 'react';
import { Leaf, Sprout, TrendingUp, AlertTriangle } from 'lucide-react';
import api from '../api';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const [recentDetections, setRecentDetections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const res = await api.get('/api/disease-detection/recent');
        setRecentDetections(res.data.detections || []);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div className="animate-fade-in" style={{ padding: '1rem' }}>
      <h1 style={{ marginBottom: '0.5rem' }}>Welcome to Agriculture AI</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Here is an overview of your farm's health and market trends.</p>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: 'linear-gradient(135deg, var(--primary-50) 0%, white 100%)' }}>
          <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'var(--primary-100)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary-600)' }}>
            <Leaf size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: 0 }}>Total Scans</h3>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{loading ? '-' : recentDetections.length}</div>
          </div>
        </div>
        
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, white 100%)' }}>
          <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'rgba(239, 68, 68, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-red)' }}>
            <AlertTriangle size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: 0 }}>Diseases Detected</h3>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{loading ? '-' : recentDetections.filter(d => d.detectedDisease !== 'Healthy').length}</div>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: 'linear-gradient(135deg, var(--primary-50) 0%, white 100%)' }}>
          <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'var(--primary-100)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary-600)' }}>
            <Sprout size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: 0 }}>Healthy Crops</h3>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{loading ? '-' : recentDetections.filter(d => d.detectedDisease === 'Healthy').length}</div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.5rem' }}>
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ margin: 0 }}>Recent Detections</h3>
            <Link to="/disease-detection" style={{ fontSize: '0.875rem', color: 'var(--primary-600)', textDecoration: 'none', fontWeight: 500 }}>View All</Link>
          </div>
          
          {loading ? (
            <p style={{ color: 'var(--text-muted)' }}>Loading recent activity...</p>
          ) : recentDetections.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem 0' }}>
              <Leaf size={32} style={{ color: 'var(--primary-200)', margin: '0 auto 1rem' }} />
              <p style={{ color: 'var(--text-muted)' }}>No recent detections found.</p>
              <Link to="/disease-detection" className="btn btn-primary" style={{ display: 'inline-block', marginTop: '1rem', textDecoration: 'none' }}>Scan a Crop</Link>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {recentDetections.slice(0, 5).map(item => (
                <div key={item.id} style={{ display: 'flex', gap: '1rem', alignItems: 'center', padding: '0.75rem', background: 'rgba(255, 255, 255, 0.5)', borderRadius: '0.5rem', border: '1px solid var(--primary-50)' }}>
                  <img src={item.imageUrl} alt="crop" style={{ width: '50px', height: '50px', objectFit: 'cover', borderRadius: '0.25rem' }} />
                  <div style={{ flex: 1 }}>
                    <h4 style={{ fontSize: '0.95rem', margin: '0 0 0.25rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {item.detectedDisease}
                      {item.detectedDisease === 'Healthy' ? (
                        <span style={{ fontSize: '0.7rem', padding: '0.1rem 0.4rem', background: 'rgba(16, 185, 129, 0.1)', color: 'var(--accent-green)', borderRadius: '1rem' }}>Safe</span>
                      ) : (
                        <span style={{ fontSize: '0.7rem', padding: '0.1rem 0.4rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-red)', borderRadius: '1rem' }}>Warning</span>
                      )}
                    </h4>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
                      {new Date(item.detectedAt).toLocaleString()}
                    </p>
                  </div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--primary-600)' }}>
                    {(item.confidenceScore * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ margin: 0 }}>Quick Actions</h3>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <Link to="/disease-detection" className="card" style={{ textDecoration: 'none', textAlign: 'center', background: 'var(--primary-50)', border: '1px solid var(--primary-100)', transition: 'all 0.2s' }}>
              <Leaf size={32} style={{ color: 'var(--primary-500)', margin: '0 auto 0.5rem' }} />
              <div style={{ fontWeight: 500, color: 'var(--primary-800)' }}>Scan Crop</div>
            </Link>
            <Link to="/crops" className="card" style={{ textDecoration: 'none', textAlign: 'center', background: 'var(--primary-50)', border: '1px solid var(--primary-100)', transition: 'all 0.2s' }}>
              <Sprout size={32} style={{ color: 'var(--primary-500)', margin: '0 auto 0.5rem' }} />
              <div style={{ fontWeight: 500, color: 'var(--primary-800)' }}>Recommend Crop</div>
            </Link>
            <Link to="/market" className="card" style={{ textDecoration: 'none', textAlign: 'center', background: 'var(--primary-50)', border: '1px solid var(--primary-100)', transition: 'all 0.2s' }}>
              <TrendingUp size={32} style={{ color: 'var(--primary-500)', margin: '0 auto 0.5rem' }} />
              <div style={{ fontWeight: 500, color: 'var(--primary-800)' }}>Check Prices</div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
