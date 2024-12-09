import React from "react";
import Navbar from "./Navbar";

const RagAnswering = () => {
  return (
    <div>
      <Navbar /> {/* Include Navbar */}
      <div className="container mt-5" style={styles.container}>
        <h2 className="section-title text-center" style={styles.title}>
          Rag Answering
        </h2>
        <table className="table table-striped" style={styles.table}>
          <thead>
            <tr>
              <th>#</th>
              <th>Question</th>
              <th>Answer</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>1</td>
              <td>What is Rag Answering?</td>
              <td>Rag answering is a method of response...</td>
            </tr>
            {/* Add more rows as necessary */}
          </tbody>
        </table>
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
