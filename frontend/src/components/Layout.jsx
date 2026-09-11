import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Home, Scan, Sprout, Droplets, CloudSun, LogOut, MessageSquare } from 'lucide-react';
import './Layout.css';

const Layout = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/', icon: Home },
    { name: 'Disease Detection', path: '/disease-detection', icon: Scan },
    { name: 'Crop Advisor', path: '/crops', icon: Sprout },
    { name: 'Fertilizer', path: '/fertilizer', icon: Droplets },
    { name: 'Weather & Prices', path: '/market', icon: CloudSun },
    { name: 'AI Chatbot', path: '/chat', icon: MessageSquare },
  ];

  return (
    <div className="layout-container">
      {/* Sidebar */}
      <aside className="sidebar glass-panel animate-fade-in">
        <div className="sidebar-header">
          <div className="logo-icon"><Sprout size={28} /></div>
          <h2 className="logo-text">AgriGuardian</h2>
        </div>
        
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <item.icon size={20} className="nav-icon" />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button onClick={handleLogout} className="logout-btn">
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="topbar glass-panel animate-fade-in">
          <div className="topbar-search">
            {/* Search or breadcrumbs could go here */}
          </div>
          <div className="user-profile">
            <div className="avatar">F</div>
          </div>
        </header>
        <div className="content-area">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
