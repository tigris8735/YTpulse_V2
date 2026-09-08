import React, { useContext } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext } from './context/AuthContext';
import Layout from './components/common/Layout/Layout';

// Auth pages
import Login from './components/auth/Login';
import Register from './components/auth/Register';

// Main pages
import TrendsFeed from './components/trends/TrendsFeed';
import PreviewPage from './components/preview/PreviewPage';
import GeneratePage from './components/generate/GeneratePage';
import QueuePage from './components/queue/QueuePage';
import Cabinet from './components/cabinet/Cabinet';

// Payment pages
import Plans from './components/payments/Plans';
import Checkout from './components/payments/Checkout';
import Success from './components/payments/Success';
import ErrorPage from './components/payments/Error';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useContext(AuthContext);
  if (loading) return <div className="loader">Loading...</div>;
  return user ? children : <Navigate to="/login" />;
};

const ProRoute = ({ children }) => {
  const { user } = useContext(AuthContext);
  if (!user || user.plan !== 'pro') {
    return <Navigate to="/plans" replace />;
  }
  return children;
};

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/plans" element={<Plans />} />
      <Route path="/checkout" element={<Checkout />} />
      <Route path="/payment/success" element={<Success />} />
      <Route path="/payment/error" element={<ErrorPage />} />

      {/* Protected routes with Layout */}
      <Route element={<Layout />}>
        <Route
          path="/"
          element={
            <PrivateRoute>
              <TrendsFeed />
            </PrivateRoute>
          }
        />
        <Route
          path="/preview"
          element={
            <PrivateRoute>
              <PreviewPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/generate"
          element={
            <PrivateRoute>
              <ProRoute>
                <GeneratePage />
              </ProRoute>
            </PrivateRoute>
          }
        />
        <Route
          path="/queue"
          element={
            <PrivateRoute>
              <ProRoute>
                <QueuePage />
              </ProRoute>
            </PrivateRoute>
          }
        />
        <Route
          path="/cabinet/*"
          element={
            <PrivateRoute>
              <Cabinet />
            </PrivateRoute>
          }
        />
      </Route>
    </Routes>
  );
}

export default App;