import React, { useState, useEffect, useCallback } from 'react';
import { CloudSun, Droplets, Wind, Thermometer, Search, Info } from 'lucide-react';
import api from '../api';

const statBox = {
  background: 'var(--primary-50)',
  padding: '1rem',
  borderRadius: '0.5rem',
  border: '1px solid var(--primary-100)',
};

const statLabel = {
  fontSize: '0.8rem',
  color: 'var(--text-muted)',
  marginBottom: '0.25rem',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  fontWeight: 600,
  display: 'flex',
  alignItems: 'center',
  gap: '0.35rem',
};

const statValue = { fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-color)' };

const WeatherPanel = () => {
  const [city, setCity] = useState('New Delhi');
  const [input, setInput] = useState('New Delhi');
  const [current, setCurrent] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async (targetCity) => {
    setLoading(true);
    setError('');
    try {
      const [cur, fc] = await Promise.all([
        api.get(`/api/weather/current?city=${encodeURIComponent(targetCity)}`),
        api.get(`/api/weather/forecast?city=${encodeURIComponent(targetCity)}&days=5`),
      ]);
      setCurrent(cur.data);
      setForecast(fc.data.forecast || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not load weather for that city.');
      setCurrent(null);
      setForecast([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(city); }, [city, load]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (input.trim()) setCity(input.trim());
  };

  // The backend signals demo mode by injecting a notice into `advice`; surface that
  // as a dedicated banner instead of listing it as farming advice.
  const isDemo = current?.advice?.some((a) => a.includes('demo data'));
  const farmingAdvice = (current?.advice || []).filter((a) => !a.includes('demo data'));

  return (
    <div className="card" style={{ maxWidth: '800px', margin: '0 auto', marginBottom: '2rem', borderTop: '4px solid var(--primary-500)' }}>
      <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <CloudSun className="logo-icon" /> Weather
      </h3>

      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            className="input-field"
            style={{ paddingLeft: '2.5rem' }}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter city (e.g. Pune, Nagpur)"
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={loading} style={{ whiteSpace: 'nowrap' }}>
          {loading ? 'Loading...' : 'Check'}
        </button>
      </form>

      {error && (
        <div style={{ padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-red)', borderRadius: '0.5rem', fontSize: '0.875rem' }}>
          {error}
        </div>
      )}

      {current && (
        <div className="animate-fade-in">
          <div style={{ marginBottom: '1rem', color: 'var(--text-muted)', fontSize: '0.9rem', textTransform: 'capitalize' }}>
            {current.city} &middot; {current.description}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={statBox}>
              <div style={statLabel}><Thermometer size={14} /> Temperature</div>
              <div style={statValue}>
                {current.temperature}&deg;C
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 400 }}> feels {current.feelsLike}&deg;</span>
              </div>
            </div>
            <div style={statBox}>
              <div style={statLabel}><Droplets size={14} /> Humidity</div>
              <div style={statValue}>{current.humidity}%</div>
            </div>
            <div style={statBox}>
              <div style={statLabel}><Wind size={14} /> Wind</div>
              <div style={statValue}>{current.windSpeed}<span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 400 }}> m/s</span></div>
            </div>
          </div>

          {forecast.length > 0 && (
            <>
              <h4 style={{ fontSize: '0.95rem', marginBottom: '0.5rem' }}>{forecast.length}-Day Forecast</h4>
              <div style={{ display: 'grid', gridTemplateColumns: `repeat(auto-fit, minmax(110px, 1fr))`, gap: '0.75rem', marginBottom: '1.5rem' }}>
                {forecast.map((d) => (
                  <div key={d.date} style={{ ...statBox, padding: '0.75rem', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                      {new Date(d.date).toLocaleDateString(undefined, { weekday: 'short', day: 'numeric' })}
                    </div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 700 }}>{d.temperature}&deg;</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{d.humidity}% hum</div>
                  </div>
                ))}
              </div>
            </>
          )}

          {farmingAdvice.length > 0 && (
            <>
              <h4 style={{ fontSize: '0.95rem', marginBottom: '0.5rem' }}>Farming Advice</h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'grid', gap: '0.5rem' }}>
                {farmingAdvice.map((a, i) => (
                  <li key={i} style={{ padding: '0.75rem', background: 'rgba(255, 255, 255, 0.5)', borderRadius: '0.5rem', fontSize: '0.9rem', lineHeight: 1.5 }}>
                    {a}
                  </li>
                ))}
              </ul>
            </>
          )}

          {isDemo && (
            <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'rgba(234, 179, 8, 0.12)', borderRadius: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
              <Info size={16} style={{ flexShrink: 0, marginTop: '0.1rem' }} />
              <span>Showing demo weather. Add <code>OPENWEATHER_API_KEY</code> to <code>backend/.env</code> and restart the backend for live data.</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WeatherPanel;
