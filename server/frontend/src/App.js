import React, { useState, useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import LoginPanel from "./components/Login/Login";
import Register from "./components/Register/Register";
import Home from "./components/Home/Home";
import Dealers from "./components/Dealers/Dealers";
import Dealer from "./components/Dealers/Dealer";
import PostReview from "./components/Dealers/PostReview";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const username = sessionStorage.getItem("username");
    if (username) {
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <Routes>
      {/* Public Routes */}
      <Route 
        path="/" 
        element={isAuthenticated ? <Home /> : <LoginPanel />} 
      />
      <Route 
        path="/login" 
        element={isAuthenticated ? <Navigate to="/" /> : <LoginPanel />} 
      />
      <Route 
        path="/register" 
        element={isAuthenticated ? <Navigate to="/" /> : <Register />} 
      />

      {/* Protected Routes */}
      <Route 
        path="/home" 
        element={isAuthenticated ? <Home /> : <Navigate to="/login" />} 
      />
      <Route 
        path="/dealers" 
        element={isAuthenticated ? <Dealers /> : <Navigate to="/login" />} 
      />
      <Route 
        path="/dealer/:id" 
        element={isAuthenticated ? <Dealer /> : <Navigate to="/login" />} 
      />
      <Route 
        path="/postreview/:id" 
        element={isAuthenticated ? <PostReview /> : <Navigate to="/login" />} 
      />

      {/* Catch all - redirect to home or login */}
      <Route 
        path="*" 
        element={<Navigate to={isAuthenticated ? "/" : "/login"} />} 
      />
    </Routes>
  );
}

export default App;
