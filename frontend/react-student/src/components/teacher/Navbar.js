import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav
      className="navbar navbar-expand-lg navbar-light"
      style={{ backgroundColor: "#f8f9fa" }}
    >
      <div className="container-fluid">
        <a className="navbar-brand" href="/">
          Teacher's Dashboard
        </a>
        <div className="d-flex">
          <Link to="/rag-answering" className="btn btn-outline-success mx-2">
            Rag Answering
          </Link>
          <Link to="/teacher-answering" className="btn btn-outline-danger mx-2">
            Teacher Answering
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
