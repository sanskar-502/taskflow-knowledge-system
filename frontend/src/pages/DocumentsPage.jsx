/**
 * Documents page (Admin only).
 * Handles file uploads and displays the list of uploaded documents
 * along with their processing status (chunk counts).
 */

import { useState, useEffect, useRef } from "react";
import api from "../api/axios";

function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await api.get("/documents");
      setDocuments(response.data.documents);
    } catch (err) {
      console.error("Failed to load documents:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    setUploadError("");
    setUploadSuccess("");

    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setUploadError("Please select a file to upload.");
      return;
    }

    if (!file.name.endsWith(".txt")) {
      setUploadError("Only .txt files are supported.");
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      await api.post("/documents", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setUploadSuccess(
        `"${file.name}" uploaded and processed successfully.`
      );
      fileInputRef.current.value = "";
      fetchDocuments();
    } catch (err) {
      setUploadError(
        err.response?.data?.detail || "Upload failed. Please try again."
      );
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return "N/A";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="documents-page">
      <div className="page-header">
        <h1>Knowledge Base</h1>
        <p className="page-subtitle">
          Upload documents to build the AI-searchable knowledge base.
        </p>
      </div>

      {/* Upload section */}
      <div className="card upload-card">
        <h3>Upload Document</h3>
        <p className="upload-hint">
          Upload a .txt file. It will be automatically chunked, embedded, and
          indexed for semantic search.
        </p>

        {uploadError && <div className="error-message">{uploadError}</div>}
        {uploadSuccess && (
          <div className="success-message">{uploadSuccess}</div>
        )}

        <form onSubmit={handleUpload} className="upload-form">
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt"
            className="file-input"
            id="file-upload"
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={uploading}
          >
            {uploading ? "Processing..." : "Upload & Process"}
          </button>
        </form>
      </div>

      {/* Document list */}
      <div className="section-header">
        <h2>Uploaded Documents</h2>
      </div>

      {loading ? (
        <div className="page-loading">Loading documents...</div>
      ) : documents.length === 0 ? (
        <div className="empty-state">
          <h3>No documents yet</h3>
          <p>Upload your first document to start building the knowledge base.</p>
        </div>
      ) : (
        <div className="document-list">
          {documents.map((doc) => (
            <div key={doc.id} className="document-card">
              <div className="doc-icon">TXT</div>
              <div className="doc-info">
                <h4 className="doc-name">{doc.original_name}</h4>
                <div className="doc-meta">
                  <span>{formatFileSize(doc.file_size)}</span>
                  <span className="separator">|</span>
                  <span>{doc.chunk_count} chunks</span>
                  <span className="separator">|</span>
                  <span>
                    Uploaded {new Date(doc.created_at).toLocaleDateString()}
                  </span>
                  {doc.uploader_name && (
                    <>
                      <span className="separator">|</span>
                      <span>by {doc.uploader_name}</span>
                    </>
                  )}
                </div>
              </div>
              <div className="doc-status">
                {doc.chunk_count > 0 ? (
                  <span className="status-badge status-completed">Indexed</span>
                ) : (
                  <span className="status-badge status-pending">
                    Not indexed
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default DocumentsPage;
