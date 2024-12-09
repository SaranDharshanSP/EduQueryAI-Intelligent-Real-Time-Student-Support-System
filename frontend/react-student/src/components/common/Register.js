import React, { useState } from "react";
import axios from "axios"; // Import axios for making API requests

const Register = () => {
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [className, setClassName] = useState("");
  const [isStudent, setIsStudent] = useState(true); // Default to Student

  const handleToggle = (value) => {
    setIsStudent(value);
  };

  const handleRegister = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:5000/register", {
        name,
        username,
        password,
        role: isStudent ? "student" : "teacher", // Correctly map role to string
        className: isStudent ? className : undefined, // Only send className if student
      });
      console.log(response)

      if (response.status === 201) {
        alert("Registration successful!");
        // Optionally redirect to login or home page
      }
    
    } catch (error) {
      if (error.response) {
        alert(error.response.data.message);
      } else {
        alert("Error occurred during registration.");
      }
    }
  };

  return (
    <div className="w-96 p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-xl mb-4">
        {isStudent ? "Student" : "Teacher"} Registration
      </h2>

      {/* Segmented Toggle */}
      <div className="flex items-center mb-4">
        <div
          className={`w-1/2 text-center py-2 cursor-pointer ${
            isStudent ? "bg-blue-500 text-white" : "bg-gray-200 text-black"
          }`}
          onClick={() => handleToggle(true)}
        >
          Teacher
        </div>
        <div
          className={`w-1/2 text-center py-2 cursor-pointer ${
            !isStudent ? "bg-blue-500 text-white" : "bg-gray-200 text-black"
          }`}
          onClick={() => handleToggle(false)}
        >
          Student
        </div>
      </div>

      <input
        className="w-full p-2 mb-4 border rounded"
        type="text"
        placeholder="Full Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <input
        className="w-full p-2 mb-4 border rounded"
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        className="w-full p-2 mb-4 border rounded"
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {isStudent && (
        <input
          className="w-full p-2 mb-4 border rounded"
          type="text"
          placeholder="Class"
          value={className}
          onChange={(e) => setClassName(e.target.value)}
        />
      )}
      <button
        className="w-full py-2 bg-blue-500 text-white rounded"
        onClick={handleRegister} // Call handleRegister on button click
      >
        Register
      </button>
    </div>
  );
};

export default Register;
