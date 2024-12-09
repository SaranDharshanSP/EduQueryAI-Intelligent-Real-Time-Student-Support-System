import React, { useState, useEffect } from "react";
import Navbar from "./Navbar";

const TeacherAnswering = () => {
  const [data, setData] = useState([]);
  const [teacherAnswer, setTeacherAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data from the Flask backend
  useEffect(() => {
    fetch("http://localhost:5000/api/teacher-answering")
      .then((response) => response.json())
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch((error) => {
        setError("Error fetching data");
        setLoading(false);
      });
  }, []);

  // Handle answer submission
  const handleAnswerSubmit = (question_id) => {
    const answerData = { teacher_answer: teacherAnswer };

    fetch(`http://localhost:5000/api/teacher-answering/${question_id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(answerData),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data.message);
        alert("Answer updated successfully!");
        setTeacherAnswer("");  // Clear the answer input

        // Update the status of the current question to "answered"
        setData((prevData) => {
          return prevData.map((item) => {
            if (item._id === question_id) {
              return { ...item, status: "answered" };
            }
            return item;
          });
        });
      })
      .catch((error) => {
        console.error("Error updating answer:", error);
        alert("Failed to update the answer.");
      });
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <Navbar /> {/* Include Navbar */}
      <div className="container mt-5" style={styles.container}>
        <h2 className="section-title text-center" style={styles.title}>
          Teacher Answering
        </h2>
        <table className="table table-striped" style={styles.table}>
          <thead>
            <tr>
              <th>#</th>
              <th>Question</th>
              <th>Teacher Answer</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => (
              <tr key={item._id}>
                <td>{index + 1}</td>
                <td>{item.user_message}</td>
                <td>
                  <textarea
                    value={teacherAnswer}
                    onChange={(e) => setTeacherAnswer(e.target.value)}
                    placeholder="Write your answer here..."
                    rows="4"
                    cols="50"
                  />
                  <button
                    onClick={() => handleAnswerSubmit(item._id)} // Pass the _id instead of index
                    style={styles.button}
                  >
                    Submit Answer
                  </button>
                </td>
                <td>{item.status || "Not Answered"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const styles = {
  container: {
    backgroundColor: "#f8d7da", // Light red background
    borderRadius: "10px",
    padding: "20px",
  },
  title: {
    color: "#721c24", // Dark red title
    fontWeight: "bold",
  },
  table: {
    backgroundColor: "white",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
  },
  button: {
    marginTop: "10px",
    padding: "8px 16px",
    backgroundColor: "#721c24",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
};

export default TeacherAnswering;
