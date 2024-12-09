import React, { useState } from "react";
import { AiOutlineSend } from "react-icons/ai";
import Sidebar from "./Sidebar"; // Import Sidebar

const ChatInterface = ({ messageHistory = [], addQuestionToSidebar }) => {
  const [userMessage, setUserMessage] = useState("");
  const [messages, setMessages] = useState(messageHistory);
  const [questions, setQuestions] = useState([]); // To store questions for the sidebar

  // Function to send message and get response from the backend
  const handleSendMessage = async () => {
    if (userMessage.trim()) {
      // Add the user message to the messages state
      setMessages((prevMessages) => [
        ...prevMessages,
        { type: "user", content: userMessage },
      ]);

      // Add the user message to the sidebar as a question
      addQuestionToSidebar(userMessage);
      setQuestions((prevQuestions) => [
        ...prevQuestions,
        { content: userMessage, status: "rag" }, // Assuming "rag" as a status for now
      ]);

      // Send the user message to the backend (assuming a POST request to /api/send-message)
      try {
        const response = await fetch("http://127.0.0.1:5000/api/send-message", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message: userMessage }),
        });

        // Check if the request was successful
        if (response.ok) {
          const data = await response.json();
          // Assuming the response contains a "bot_response" field with the bot's answer
          setMessages((prevMessages) => [
            ...prevMessages,
            { type: "bot", content: data.bot_response },
          ]);
        } else {
          // Handle error from the backend
          setMessages((prevMessages) => [
            ...prevMessages,
            { type: "bot", content: "Sorry, I couldn't get an answer." },
          ]);
        }
      } catch (error) {
        console.error("Error sending message:", error);
        setMessages((prevMessages) => [
          ...prevMessages,
          { type: "bot", content: "There was an error with the request." },
        ]);
      }

      // Clear the input field
      setUserMessage("");
    }
  };

  return (
    <div className="flex w-full h-full bg-white rounded-lg shadow-lg p-6">
      {/* Sidebar Component */}
      <Sidebar questions={questions} />

      {/* Chat Interface */}
      <div className="flex-1 flex flex-col ml-4">
        <h2 className="text-3xl font-semibold mb-6 text-center text-blue-600">
          Student Chatbot
        </h2>

        <div className="flex-1 overflow-auto p-4 bg-gray-50 rounded-lg shadow-inner mb-6">
          {messages?.map((msg, index) => (
            <div
              key={index}
              className={`flex ${
                msg.type === "user" ? "justify-end" : "justify-start"
              } mb-4`}
            >
              <div
                className={`p-4 max-w-xs rounded-lg ${
                  msg.type === "user" ? "bg-blue-500 text-white" : "bg-gray-200"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
        </div>

        <div className="flex items-center p-4 border-t bg-gray-100 rounded-b-lg">
          <input
            type="text"
            placeholder="Enter a message"
            value={userMessage}
            onChange={(e) => setUserMessage(e.target.value)}
            className="flex-1 p-2 border border-gray-300 rounded-l-lg"
          />
          <button
            onClick={handleSendMessage}
            className="p-2 bg-blue-500 text-white rounded-r-lg"
          >
            <AiOutlineSend />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
