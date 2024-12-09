import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Register from "./Register"; // Import Register component

const Login = () => {
  const [isStudent, setIsStudent] = useState(false); // Track if it's student or teacher login
  const [isRegistering, setIsRegistering] = useState(false); // Toggle for Register view
  const [username, setUsername] = useState(""); // Username state
  const [password, setPassword] = useState(""); // Password state
  const [error, setError] = useState(""); // Error state to show login errors
  const navigate = useNavigate(); // Hook for navigation

  // Set role function to update isStudent state
  const setRole = (role) => {
    if (role === "teacher") {
      setIsStudent(false); // When "teacher" is selected, set isStudent to false
    } else {
      setIsStudent(true); // When "student" is selected, set isStudent to true
    }
  };

  // Toggle between login and register views
  const toggleRegisterView = () => setIsRegistering((prevState) => !prevState);

  // Handle login logic with API request
  const handleLogin = async () => {
    const data = {
      username: username,
      password: password,
    };

    try {
      const response = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (response.status === 200) {
        // Successful login, navigate to the appropriate dashboard based on role
        console.log("User Role:", result.user.role); // Log the user role to check it
        if (isStudent) {
          navigate("/student-dashboard"); // Redirect to student dashboard
        } else {
          navigate("/teacher-dashboard"); // Redirect to teacher dashboard
        }
      } else {
        // Handle login failure
        setError(result.message);
      }
    } catch (err) {
      setError("An error occurred. Please try again later.");
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-gray-100">
      {/* If not registering, show login form */}
      {!isRegistering ? (
        <div className="w-96 p-6 bg-white rounded-lg shadow-lg">
          <div className="flex justify-between mb-4">
            {/* Teacher Login Button */}
            <button
              className={`py-2 px-4 ${!isStudent ? "bg-blue-500 text-white" : "bg-gray-200"}`}
              onClick={() => setRole("teacher")} // Set role as "teacher" and update isStudent
            >
              Teacher login
            </button>
            {/* Student Login Button */}
            <button
              className={`py-2 px-4 ${isStudent ? "bg-blue-500 text-white" : "bg-gray-200"}`}
              onClick={() => setRole("student")} // Set role as "student" and update isStudent
            >
              Student login
            </button>
          </div>

          {/* Username Input */}
          <input
            className="w-full p-2 mb-4 border rounded"
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          {/* Password Input */}
          <input
            className="w-full p-2 mb-4 border rounded"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {/* Error message */}
          {error && <p className="text-red-500 text-center mb-4">{error}</p>}

          {/* Login Button */}
          <button
            onClick={handleLogin}
            className="w-full py-2 bg-blue-500 text-white rounded"
          >
            Login
          </button>

          {/* Register Link */}
          <p className="mt-4 text-center">
            Not signed up?{" "}
            <button onClick={toggleRegisterView} className="text-blue-500">
              Register here
            </button>
          </p>
        </div>
      ) : (
        <Register /> // Show Register component if isRegistering is true
      )}
    </div>
  );
};

export default Login;
