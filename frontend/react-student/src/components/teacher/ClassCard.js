import React, { useState } from "react";

const ClassCard = ({ classInfo }) => {
  const [pdfFile, setPdfFile] = useState(null);
  const [isPdfUploaded, setIsPdfUploaded] = useState(false);

  const handlePdfUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
      setPdfFile(file);
      setIsPdfUploaded(true);
    } else {
      alert("Please upload a valid PDF file.");
    }
  };

  return (
    <div className="col-md-4 my-3">
      <div className="card">
        <div className="card-body">
          <h5 className="card-title">{classInfo.name}</h5>
          <h6 className="card-subtitle mb-2 text-muted">{classInfo.subject}</h6>
          <p className="card-text">Created on: {classInfo.creationDate}</p>

          {/* PDF Upload Section */}
          <div>
            <input
              type="file"
              className="form-control"
              accept="application/pdf"
              onChange={handlePdfUpload}
            />
            {isPdfUploaded && (
              <div className="mt-2">
                <p>PDF uploaded successfully!</p>
              </div>
            )}
          </div>

          {/* Start Chat Button */}
          <div className="mt-3">
            <button className="btn btn-info">Start Chat</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClassCard;
