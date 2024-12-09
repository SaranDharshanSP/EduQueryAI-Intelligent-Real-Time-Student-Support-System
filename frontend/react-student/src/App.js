import React, { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Login from "./components/common/Login";
import Register from "./components/common/Register";
import ChatInterface from "./components/student/ChatInterface";
import Dashboard from "./components/teacher/Dashboard";
import RagAnswering from "./components/teacher/RagAnswering";
import TeacherAnswering from "./components/teacher/TeacherAnswering";

const App = () => {
  const [messages, setMessages] = useState([]); // Define messages state
  const [sidebarQuestions, setSidebarQuestions] = useState([]); // Sidebar state for tracking user questions

  // Function to add questions to the sidebar
  const addQuestionToSidebar = (question) => {
    setSidebarQuestions((prevQuestions) => [...prevQuestions, question]);
  };

  return (
    <Router>
      <Routes>
        {/* Route for Login */}
        <Route path="/" element={<Login />} />

        {/* Route for Register */}
        <Route path="/register" element={<Register />} />

        {/* Route for Student Dashboard */}
        <Route
          path="/student-dashboard"
          element={
            <ChatInterface
              messageHistory={messages} // Pass messages to the ChatInterface
              addQuestionToSidebar={addQuestionToSidebar} // Pass function to add questions to the sidebar
            />
          }
        />

        {/* Route for Teacher Dashboard */}
        <Route path="/teacher-dashboard" element={<Dashboard />} />

        {/* Route for Rag Answering */}
        <Route path="/rag-answering" element={<RagAnswering />} />

        {/* Route for Teacher Answering */}
        <Route path="/teacher-answering" element={<TeacherAnswering />} />
      </Routes>
    </Router>
  );
};

export default App;
