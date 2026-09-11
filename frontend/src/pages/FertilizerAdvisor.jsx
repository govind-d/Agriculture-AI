import React, { useState } from 'react';
import { FlaskConical, Droplets, Thermometer, Box, ShieldAlert } from 'lucide-react';
import api from '../api';

const FertilizerAdvisor = () => {
  const [formData, setFormData] = useState({
    temperature: '',
    humidity: '',
    moisture: '',
    soilType: '',
    cropType: '',
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    landArea: '1'
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
        temperature: Number(formData.temperature),
        humidity: Number(formData.humidity),
        moisture: Number(formData.moisture),
        soilType: formData.soilType,
        cropType: formData.cropType,
        nitrogen: Number(formData.nitrogen),
        phosphorus: Number(formData.phosphorus),
        potassium: Number(formData.potassium),
        landArea: Number(formData.landArea)
      };
      
      const res = await api.post('/api/fertilizer/recommend', payload);
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
        <FlaskConical className="logo-icon" /> AI Fertilizer Advisor
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem' }}>
        
        {/* Input Form Section */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Soil & Crop Data</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
            Provide details about your soil, current crop, and land area to get tailored fertilizer recommendations.
          </p>

          {error && (
            <div style={{ padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-red)', borderRadius: '0.5rem', marginBottom: '1rem', fontSize: '0.875rem' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleRecommend} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div style={{ gridColumn: '1 / -1' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}>Crop Type</label>
                <input type="text" className="input-field" name="cropType" value={formData.cropType} onChange={handleChange} required placeholder="e.g. Wheat, Rice, Cotton" />
              </div>
              <div style={{ gridColumn: '1 / -1' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}>Soil Type</label>
                <select className="input-field" name="soilType" value={formData.soilType} onChange={handleChange} required>
                  <option value="" disabled>Select Soil Type</option>
                  <option value="Sandy">Sandy</option>
                  <option value="Loamy">Loamy</option>
                  <option value="Black">Black</option>
                  <option value="Red">Red</option>
                  <option value="Clayey">Clayey</option>
                </select>
              </div>

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
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}><Droplets size={14}/> Moisture (%)</label>
                <input type="number" step="0.1" className="input-field" name="moisture" value={formData.moisture} onChange={handleChange} required min="0" max="100" placeholder="e.g. 35" />
              </div>
              <div>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}><Thermometer size={14}/> Temp (°C)</label>
                <input type="number" step="0.1" className="input-field" name="temperature" value={formData.temperature} onChange={handleChange} required min="0" max="50" placeholder="e.g. 28.5" />
              </div>
              <div>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}><Droplets size={14}/> Humidity (%)</label>
                <input type="number" step="0.1" className="input-field" name="humidity" value={formData.humidity} onChange={handleChange} required min="0" max="100" placeholder="e.g. 65.0" />
              </div>
              <div style={{ gridColumn: '1 / -1' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}><Box size={14}/> Land Area (Acres)</label>
                <input type="number" step="0.1" className="input-field" name="landArea" value={formData.landArea} onChange={handleChange} required min="0.1" placeholder="e.g. 2.5" />
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }} disabled={loading}>
              {loading ? 'Analyzing data...' : 'Get Fertilizer Recommendation'}
            </button>
          </form>
        </div>

        {/* Results Section */}
        <div>
          {result ? (
            <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="card" style={{ borderTop: '4px solid var(--primary-500)' }}>
                <h3 style={{ marginBottom: '0.5rem', color: 'var(--primary-700)', fontSize: '1.1rem' }}>Recommended Fertilizer</h3>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--primary-800)', marginBottom: '1.5rem' }}>
                  {result.fertilizer}
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                  <div style={{ background: 'var(--primary-50)', padding: '1rem', borderRadius: '0.5rem', border: '1px solid var(--primary-100)' }}>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Qty / Acre</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-color)' }}>{result.qtyPerAcre} kg</div>
                  </div>
                  <div style={{ background: 'var(--primary-50)', padding: '1rem', borderRadius: '0.5rem', border: '1px solid var(--primary-100)' }}>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Total Required</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-color)' }}>{result.totalQty} kg</div>
                  </div>
                </div>

                <h4 style={{ fontSize: '0.95rem', marginBottom: '0.5rem' }}>Why this fertilizer?</h4>
                <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.5)', borderRadius: '0.5rem', fontSize: '0.9rem', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
                  {result.explanation}
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
              <FlaskConical size={48} style={{ color: 'var(--primary-300)', marginBottom: '1rem' }} />
              <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>Submit your soil data to see<br/>AI fertilizer recommendations here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FertilizerAdvisor;
