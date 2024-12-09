import React, { useState } from "react";
import { AiOutlineCheckCircle, AiOutlineClockCircle } from "react-icons/ai";

const Sidebar = ({ questions }) => {
  const [selectedQuestion, setSelectedQuestion] = useState(null);

  const currentDate = new Date().toLocaleDateString();

  const handleQuestionClick = (questionId) => {
    if (selectedQuestion === questionId) {
      setSelectedQuestion(null); // Hide the answer if clicked again
    } else {
      setSelectedQuestion(questionId); // Show the answer for the clicked question
    }
  };

  return (
    <div className="sidebar w-1/4 p-4 bg-gray-100 shadow-lg">
      <h3 className="text-xl font-semibold mb-4">Question History</h3>
      <p className="text-sm text-gray-600 mb-4">Last updated: {currentDate}</p>

      <div className="questions-list space-y-4">
        {questions.length === 0 ? (
          <p>No questions available.</p>
        ) : (
          questions.map((question, index) => (
            <div key={index} className="question-item">
              <div
                className="flex items-center cursor-pointer"
                onClick={() => handleQuestionClick(index)}
              >
                <span className="mr-2">
                  {question.status === "rag" ? (
                    <AiOutlineCheckCircle className="text-green-500" />
                  ) : (
                    <AiOutlineClockCircle className="text-yellow-500" />
                  )}
                </span>
                <span>{question.content}</span>
              </div>

              {selectedQuestion === index && (
                <div className="mt-2 ml-6 text-sm text-gray-700">
                  <p>Answer: This is the answer for the selected question.</p>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Sidebar;
