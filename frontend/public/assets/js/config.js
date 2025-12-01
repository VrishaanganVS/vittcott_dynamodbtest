// Shared configuration for VittCott frontend
// This file centralizes API URL configuration to avoid hard-coded URLs across files

(function() {
  'use strict';

  /**
   * Determine the API base URL based on the current protocol.
   * - If opened via file:// (local file system), fall back to localhost:3000
   * - Otherwise use empty string for same-origin relative paths
   * - Can be overridden by setting window.VITTCOTT_API_BASE before this script loads
   */
  function getApiBase() {
    // Allow explicit override
    if (typeof window.VITTCOTT_API_BASE === 'string') {
      return window.VITTCOTT_API_BASE;
    }
    // When opened via file://, we need an absolute URL
    if (window.location.protocol === 'file:') {
      return 'http://localhost:3000';
    }
    // For HTTP/HTTPS, use relative paths (same-origin)
    return '';
  }

  /**
   * Determine the Assistant URL for the AI assistant (e.g., Streamlit app).
   * - Can be overridden by setting window.VITTCOTT_ASSISTANT_URL before this script loads
   * - Defaults to localhost:8501 for local development
   * - In production, set this to '/assistant/' or your deployed assistant URL
   */
  function getAssistantUrl() {
    // Allow explicit override
    if (typeof window.VITTCOTT_ASSISTANT_URL === 'string') {
      return window.VITTCOTT_ASSISTANT_URL;
    }
    // Default to local Streamlit for development
    return 'http://localhost:8501';
  }

  // Export configuration object to window
  window.VittCottConfig = {
    getApiBase: getApiBase,
    getAssistantUrl: getAssistantUrl
  };
})();
