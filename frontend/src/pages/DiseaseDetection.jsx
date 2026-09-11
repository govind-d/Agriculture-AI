import React, { useState, useEffect } from 'react';
import { UploadCloud, AlertTriangle, CheckCircle, Leaf } from 'lucide-react';
import api from '../api';

const DiseaseDetection = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [recentDetections, setRecentDetections] = useState([]);

  useEffect(() => {
    fetchRecent();
  }, []);

  const fetchRecent = async () => {
    try {
      const res = await api.get('/api/disease-detection/recent');
      setRecentDetections(res.data.detections || []);
    } catch (err) {
      console.error('Failed to fetch recent detections:', err);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError('');
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Please select an image first.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const res = await api.post('/api/disease-detection/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(res.data);
      fetchRecent();
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ padding: '1rem' }}>
      <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Leaf className="logo-icon" /> AI Disease Detection
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem' }}>
        
        {/* Upload Section */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Upload Leaf Image</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
            Upload a clear photo of the affected crop leaf for instant AI analysis.
          </p>

          <div 
            style={{ 
              border: '2px dashed var(--primary-200)', 
              borderRadius: '0.75rem', 
              padding: '2rem', 
              textAlign: 'center',
              cursor: 'pointer',
              marginBottom: '1rem',
              background: 'rgba(255, 255, 255, 0.5)'
            }}
            onClick={() => document.getElementById('leaf-upload').click()}
          >
            {previewUrl ? (
              <img src={previewUrl} alt="Preview" style={{ maxWidth: '100%', maxHeight: '250px', borderRadius: '0.5rem', objectFit: 'contain' }} />
            ) : (
              <div style={{ color: 'var(--text-muted)' }}>
                <UploadCloud size={48} style={{ margin: '0 auto 1rem', color: 'var(--primary-400)' }} />
                <p>Click to browse or drag and drop</p>
                <p style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>JPEG, PNG (Max 10MB)</p>
              </div>
            )}
            <input 
              type="file" 
              id="leaf-upload" 
              accept="image/*" 
              style={{ display: 'none' }} 
              onChange={handleFileChange}
            />
          </div>

          {error && (
            <div style={{ padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-red)', borderRadius: '0.5rem', marginBottom: '1rem', fontSize: '0.875rem' }}>
              {error}
            </div>
          )}

          <button 
            className="btn btn-primary" 
            style={{ width: '100%' }} 
            onClick={handleAnalyze} 
            disabled={!selectedFile || loading}
          >
            {loading ? 'Analyzing with AI...' : 'Analyze Image'}
          </button>
        </div>

        {/* Results Section */}
        <div>
          {result && (
            <div className="card animate-fade-in" style={{ borderTop: `4px solid ${result.detectedDisease === 'Healthy' ? 'var(--accent-green)' : 'var(--accent-orange)'}` }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                {result.detectedDisease === 'Healthy' ? (
                  <CheckCircle color="var(--accent-green)" />
                ) : (
                  <AlertTriangle color={result.lowConfidence ? 'var(--accent-orange)' : 'var(--accent-red)'} />
                )}
                <h3 style={{ margin: 0 }}>{result.detectedDisease}</h3>
              </div>
              
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                  <span>AI Confidence Score</span>
                  <span style={{ fontWeight: 600 }}>{(result.confidenceScore * 100).toFixed(1)}%</span>
                </div>
                <div style={{ width: '100%', height: '8px', background: 'var(--primary-100)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ 
                    width: `${result.confidenceScore * 100}%`, 
                    height: '100%', 
                    background: result.confidenceScore > 0.8 ? 'var(--primary-500)' : 'var(--accent-orange)'
                  }} />
                </div>
                {result.lowConfidence && (
                  <p style={{ fontSize: '0.75rem', color: 'var(--accent-orange)', marginTop: '0.5rem' }}>
                    Note: The AI is not entirely confident. Please consult an expert if unsure.
                  </p>
                )}
              </div>

              <div>
                <h4 style={{ fontSize: '0.95rem', marginBottom: '0.5rem' }}>Recommended Action</h4>
                <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.5)', borderRadius: '0.5rem', fontSize: '0.9rem', lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>
                  {result.recommendedAction}
                </div>
              </div>
            </div>
          )}

          {/* Recent History */}
          {!result && recentDetections.length > 0 && (
            <div className="card">
              <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Recent Analyses</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {recentDetections.slice(0, 3).map((item) => (
                  <div key={item.id} style={{ display: 'flex', gap: '1rem', alignItems: 'center', padding: '0.75rem', background: 'rgba(255, 255, 255, 0.5)', borderRadius: '0.5rem' }}>
                    <img src={item.imageUrl} alt="crop" style={{ width: '60px', height: '60px', objectFit: 'cover', borderRadius: '0.25rem' }} />
                    <div>
                      <h4 style={{ fontSize: '0.95rem', margin: '0 0 0.25rem 0' }}>{item.detectedDisease}</h4>
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
                        {new Date(item.detectedAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DiseaseDetection;
