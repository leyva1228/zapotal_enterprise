import React from "react";
import { Link } from "react-router-dom";
import { FaChevronRight, FaHome } from "react-icons/fa";
import "./Breadcrumb.css";

export default function Breadcrumb({ items = [] }) {
  if (!items.length) return null;
  return (
    <nav className="breadcrumb" aria-label="breadcrumb">
      <Link to="/" className="breadcrumb__home" title="Inicio">
        <FaHome />
      </Link>
      {items.map((item, i) => {
        const isLast = i === items.length - 1;
        return (
          <React.Fragment key={i}>
            <span className="breadcrumb__sep" aria-hidden="true">
              <FaChevronRight />
            </span>
            {isLast || !item.to ? (
              <span className="breadcrumb__current" aria-current={isLast ? "page" : undefined}>
                {item.label}
              </span>
            ) : (
              <Link to={item.to} className="breadcrumb__link">
                {item.label}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}
