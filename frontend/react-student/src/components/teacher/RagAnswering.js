import React, { useEffect, useState } from "react";
import Navbar from "./Navbar";

const RagAnswering = () => {
  const [answers, setAnswers] = useState([]);  // State to hold the answers
  const [loading, setLoading] = useState(true);  // Loading state

  useEffect(() => {
    const fetchAnswers = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/answers");
        const data = await response.json();
  
        // Log and check the data type
        console.log("Fetched data:", data);
  
        if (Array.isArray(data)) {
          setAnswers(data);
        } else {
          console.error("API response is not an array", data);
          setAnswers([]);  // Set empty array to avoid map errors
        }
      } catch (error) {
        console.error("Error fetching answers:", error);
        setAnswers([]);  // In case of error, set an empty array
      } finally {
        setLoading(false);
      }
    };
  
    fetchAnswers();
  }, []);
  
  return (
    <div>
      <Navbar /> {/* Include Navbar */}
      <div className="container mt-5" style={styles.container}>
        <h2 className="section-title text-center" style={styles.title}>
          Rag Answering
        </h2>
        {loading ? (
          <p>Loading...</p>
        ) : (
          <table className="table table-striped" style={styles.table}>
            <thead>
              <tr>
                <th>#</th>
                <th>Question</th>
                <th>Answer</th>
              </tr>
            </thead>
            <tbody>
              {answers.map((answer, index) => (
                <tr key={answer.id}>
                  <td>{index + 1}</td>
                  <td>{answer.question}</td>
                  <td>{answer.answer}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

const styles = {
  container: {
    backgroundColor: "#e0f7e7", // Light green background
    borderRadius: "10px",
    padding: "20px",
  },
  title: {
    color: "#388e3c", // Dark green title
    fontWeight: "bold",
  },
  table: {
    backgroundColor: "white",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
  },
};

export default RagAnswering;
