import React from 'react';
import { Link } from 'react-router-dom';
import { FaShieldAlt } from 'react-icons/fa';
import { useAuth } from '../../../context/AuthContext';

export default function PanelAdminButton() {
  const { isAdmin } = useAuth();
  if (!isAdmin) return null;
  return (
    <Link
      to="/admin"
      className="navbar-admin-btn"
      title="Panel de administracion"
      aria-label="Panel admin"
    >
      <FaShieldAlt /> <span>Admin</span>
    </Link>
  );
}
