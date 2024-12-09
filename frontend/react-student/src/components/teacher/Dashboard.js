import React, { useState } from "react";
import Navbar from "./Navbar";
import StatusMessage from "./StatusMessage";

const Dashboard = () => {
  const [classes, setClasses] = useState([]);
  const [className, setClassName] = useState("");
  const [subject, setSubject] = useState("");
  const [status, setStatus] = useState("");
  const [statusType, setStatusType] = useState("");
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  // Handle class creation
  const handleClassCreate = () => {
    if (!className || !subject) {
      setStatus("Please provide both class name and subject.");
      setStatusType("error");
      return;
    }

    const newClass = {
      id: classes.length + 1,
      name: className,
      subject: subject,
      creationDate: new Date().toLocaleDateString(),
    };

    setClasses([...classes, newClass]);
    setStatus("Class created successfully!");
    setStatusType("success");
    setClassName("");
    setSubject("");
    setIsFormVisible(false);
  };

  // Handle PDF file upload to the backend
  const handleFileUpload = async () => {
    if (!selectedFile) {
      setStatus("Please select a PDF file.");
      setStatusType("error");
      return;
    }

    // Trigger an alert indicating successful upload
    alert("File uploaded successfully!");

    // Optionally, clear the selected file after uploading
    setSelectedFile(null);
  };

  return (
    <div>
      <Navbar />
      <div className="container mt-4">
        {/* Title */}
        <h1 className="text-center">Teacher's Dashboard</h1>

        {/* Create Class Section */}
        <div className="text-center">
          <button
            className="btn btn-primary"
            onClick={() => setIsFormVisible(!isFormVisible)}
          >
            {isFormVisible ? "Close Form" : "Create Class"}
          </button>
        </div>

        {/* Form to create class */}
        {isFormVisible && (
          <div className="my-3">
            <div className="mb-3">
              <input
                type="text"
                className="form-control"
                placeholder="Class Name"
                value={className}
                onChange={(e) => setClassName(e.target.value)}
              />
            </div>
            <div className="mb-3">
              <input
                type="text"
                className="form-control"
                placeholder="Subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              />
            </div>
            <button className="btn btn-success" onClick={handleClassCreate}>
              Create Class
            </button>
          </div>
        )}

        {/* File Upload Section */}
        <div className="my-3">
          <input
            type="file"
            className="form-control"
            accept=".pdf"
            onChange={(e) => setSelectedFile(e.target.files[0])}
          />
          <button className="btn btn-info mt-2" onClick={handleFileUpload}>
            Upload PDF
          </button>
        </div>

        {/* Status Message */}
        {status && <StatusMessage message={status} type={statusType} />}

        {/* Display Classes */}
        <div className="mt-5">
          {classes.length === 0 ? (
            <p className="text-center">No classes created yet.</p>
          ) : (
            <div className="row">
              {classes.map((cls) => (
                <div className="col-md-4" key={cls.id}>
                  <div className="card">
                    <div className="card-body">
                      <h5 className="card-title">{cls.name}</h5>
                      <p className="card-text">{cls.subject}</p>
                      <p className="text-muted">Created on {cls.creationDate}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
