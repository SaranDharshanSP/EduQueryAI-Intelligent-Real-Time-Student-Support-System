import React from "react";

const StatusMessage = ({ message, type }) => {
  return (
    <div
      className={`alert alert-${
        type === "success" ? "success" : "danger"
      } mt-3`}
    >
      {message}
    </div>
  );
};

export default StatusMessage;
