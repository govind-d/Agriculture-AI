import React, { useState } from 'react';
import { Sprout, Droplets, Thermometer, FlaskConical, CloudRain, ShieldAlert } from 'lucide-react';
import api from '../api';

const CropAdvisor = () => {
  const [formData, setFormData] = useState({
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    temperature: '',
    humidity: '',
    ph: '',
    rainfall: ''
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRecommend = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const payload = {
        nitrogen: Number(formData.nitrogen),
        phosphorus: Number(formData.phosphorus),
        potassium: Number(formData.potassium),
        temperature: Number(formData.temperature),
        humidity: Number(formData.humidity),
        ph: Number(formData.ph),
        rainfall: Number(formData.rainfall)
      };
      
      const res = await api.post('/api/crops/recommend', payload);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get recommendation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ padding: '1rem' }}>
      <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Sprout className="logo-icon" /> AI Crop Advisor
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem' }}>
        
        {/* Input Form Section */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Soil & Environmental Data</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
            Enter your soil parameters and local weather to get the best crop recommendations powered by AI.
          </p>

          {error && (
            <div style={{ padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-red)', borderRadius: '0.5rem', marginBottom: '1rem', fontSize: '0.875rem' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleRecommend} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}>Nitrogen (N)</label>
                <input type="number" className="input-field" name="nitrogen" value={formData.nitrogen} onChange={handleChange} required min="0" max="200" placeholder="e.g. 50" />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}>Phosphorus (P)</label>
                <input type="number" className="input-field" name="phosphorus" value={formData.phosphorus} onChange={handleChange} required min="0" max="200" placeholder="e.g. 40" />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}>Potassium (K)</label>
                <input type="number" className="input-field" name="potassium" value={formData.potassium} onChange={handleChange} required min="0" max="200" placeholder="e.g. 30" />
              </div>
              <div>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}><FlaskConical size={14}/> Soil pH</label>
                <input type="number" step="0.1" className="input-field" name="ph" value={formData.ph} onChange={handleChange} required min="0" max="14" placeholder="e.g. 6.5" />
              </div>
              <div>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}><Thermometer size={14}/> Temperature (°C)</label>
                <input type="number" step="0.1" className="input-field" name="temperature" value={formData.temperature} onChange={handleChange} required min="-10" max="60" placeholder="e.g. 25.5" />
              </div>
              <div>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}><Droplets size={14}/> Humidity (%)</label>
                <input type="number" step="0.1" className="input-field" name="humidity" value={formData.humidity} onChange={handleChange} required min="0" max="100" placeholder="e.g. 71.0" />
              </div>
              <div style={{ gridColumn: '1 / -1' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}><CloudRain size={14}/> Rainfall (mm)</label>
                <input type="number" step="0.1" className="input-field" name="rainfall" value={formData.rainfall} onChange={handleChange} required min="0" max="500" placeholder="e.g. 100.0" />
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }} disabled={loading}>
              {loading ? 'Analyzing data...' : 'Get AI Recommendation'}
            </button>
          </form>
        </div>

        {/* Results Section */}
        <div>
          {result ? (
            <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="card" style={{ borderTop: '4px solid var(--primary-500)' }}>
                <h3 style={{ marginBottom: '1rem', color: 'var(--primary-700)' }}>Top Recommended Crops</h3>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
                  {result.topCrops.map((crop, index) => (
                    <div key={index} style={{ 
                      background: index === 0 ? 'var(--primary-500)' : 'var(--primary-100)', 
                      color: index === 0 ? 'white' : 'var(--primary-700)',
                      padding: '0.5rem 1rem', 
                      borderRadius: '2rem', 
                      fontWeight: 600,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      boxShadow: index === 0 ? '0 4px 6px -1px rgba(0, 0, 0, 0.1)' : 'none'
                    }}>
                      <span style={{ 
                        background: index === 0 ? 'rgba(255,255,255,0.2)' : 'white', 
                        borderRadius: '50%', 
                        width: '24px', 
                        height: '24px', 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center', 
                        fontSize: '0.8rem' 
                      }}>#{index + 1}</span>
                      {crop.crop.charAt(0).toUpperCase() + crop.crop.slice(1)} ({Math.round(crop.confidence * 100)}%)
                    </div>
                  ))}
                </div>

                <h4 style={{ fontSize: '0.95rem', marginBottom: '0.5rem' }}>AI Insight</h4>
                <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.5)', borderRadius: '0.5rem', fontSize: '0.9rem', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
                  {result.insight}
                </div>
              </div>

              {result.warnings && result.warnings.length > 0 && (
                <div className="card" style={{ background: 'rgba(239, 68, 68, 0.05)', borderLeft: '4px solid var(--accent-red)' }}>
                  <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-red)', marginBottom: '0.5rem' }}>
                    <ShieldAlert size={18} /> Important Warnings
                  </h4>
                  <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--text-color)', fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {result.warnings.map((w, i) => <li key={i}>{w}</li>)}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', background: 'rgba(255, 255, 255, 0.3)', border: '2px dashed var(--primary-200)' }}>
              <Sprout size={48} style={{ color: 'var(--primary-300)', marginBottom: '1rem' }} />
              <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>Submit your soil data to see<br/>AI crop recommendations here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CropAdvisor;
