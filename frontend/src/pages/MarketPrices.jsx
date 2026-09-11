import React, { useState } from 'react';
import { IndianRupee, TrendingUp, Search } from 'lucide-react';
import api from '../api';
import WeatherPanel from '../components/WeatherPanel';

const MarketPrices = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await api.get(`/api/crop-prices/market-trends?crop_name=${encodeURIComponent(query)}`);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch market prices. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ padding: '1rem' }}>
      <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <IndianRupee className="logo-icon" /> Weather &amp; Market Prices
      </h2>

      <WeatherPanel />

      <div className="card" style={{ maxWidth: '800px', margin: '0 auto', marginBottom: '2rem' }}>
        <h3 style={{ marginBottom: '1rem' }}>Crop Price Analysis</h3>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
          Get current estimated prices and future trends for your crops powered by Gemini AI.
        </p>

        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input 
              type="text" 
              className="input-field" 
              style={{ paddingLeft: '2.5rem' }}
              value={query} 
              onChange={(e) => setQuery(e.target.value)} 
              required 
              placeholder="Enter crop name (e.g. Wheat, Tomato, Onion)" 
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading} style={{ whiteSpace: 'nowrap' }}>
            {loading ? 'Analyzing...' : 'Get Prices'}
          </button>
        </form>

        {error && (
          <div style={{ padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-red)', borderRadius: '0.5rem', fontSize: '0.875rem' }}>
            {error}
          </div>
        )}
      </div>

      {result && (
        <div className="animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto', display: 'grid', gap: '1.5rem' }}>
          <div className="card" style={{ borderTop: '4px solid var(--primary-500)' }}>
            <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', textTransform: 'capitalize' }}>
              {result.crop} Market Overview
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ background: 'var(--primary-50)', padding: '1rem', borderRadius: '0.5rem', border: '1px solid var(--primary-100)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Current Price</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-color)' }}>
                  ₹{result.currentPrice.price} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 400 }}>/{result.currentPrice.unit}</span>
                </div>
              </div>
              <div style={{ background: 'var(--primary-50)', padding: '1rem', borderRadius: '0.5rem', border: '1px solid var(--primary-100)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Market Trend</div>
                <div style={{ 
                  fontSize: '1.2rem', 
                  fontWeight: 700, 
                  color: result.trend === 'Rising' ? 'var(--accent-green)' : result.trend === 'Falling' ? 'var(--accent-red)' : 'var(--text-color)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem'
                }}>
                  {result.trend === 'Rising' && <TrendingUp size={20} />}
                  {result.trend}
                </div>
              </div>
            </div>

            <h4 style={{ fontSize: '0.95rem', marginBottom: '0.5rem' }}>AI Forecast & Factors</h4>
            <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.5)', borderRadius: '0.5rem', fontSize: '0.9rem', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
              {result.forecast}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketPrices;
