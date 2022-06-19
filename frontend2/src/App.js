import React from 'react';
import './App.css';
import {HomePage} from "./pages/HomePage";
import {LoginPage} from "./pages/LoginPage";
import {BrowserRouter as Router, Route } from "react-router-dom";
import {PrivateRoute} from "./utils/PrivateRoute";
import {AuthProvider} from "./context/AuthContext";
import {Navbar} from "./components/Navbar";
import {Application} from "./components/Application";


function App() {
  return (
      <div className="App">
        <Router>
          <AuthProvider>
              <Navbar></Navbar>
              <Route component={HomePage} path='/' exact/>
              <PrivateRoute component={Application} path='/application'/>
            <Route component={LoginPage} path='/login'/>
          </AuthProvider>
        </Router>

      </div>
  );
}

export default App;