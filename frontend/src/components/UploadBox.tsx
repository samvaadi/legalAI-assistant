import React, { useCallback, useState } from 'react';

interface UploadBoxProps {
  onFile: (file: File) => void;
  loading: boolean;
}

export const UploadBox: React.FC<UploadBoxProps> = ({ onFile, loading }) => {
  const [dragging, setDragging] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) onFile(file);
    },
    [onFile]
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFile(file);
  };

  return (
    <div className="upload-overlay">
      <div className="upload-modal">
        <div className="upload-modal-header">
          <h2>Upload Contract</h2>
          <p>PDF or DOCX · Up to 50MB</p>
        </div>

        <div
          className={`drop-zone ${dragging ? 'dragging' : ''} ${loading ? 'loading' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
        >
          {loading ? (
            <div className="upload-loading">
              <div className="upload-spinner" />
              <p>Analyzing contract…</p>
              <span>Extracting clauses & scoring risk</span>
            </div>
          ) : (
            <>
              <div className="drop-icon">⬆</div>
              <p className="drop-text">Drag & drop your contract here</p>
              <span className="drop-sub">or</span>
              <label className="browse-btn">
                Browse Files
                <input
                  type="file"
                  accept=".pdf,.docx,.doc"
                  hidden
                  onChange={handleFileChange}
                />
              </label>
              <p className="drop-formats">Supports PDF · DOCX · DOC</p>
            </>
          )}
        </div>

        <div className="upload-features">
          {['AI Risk Scoring', 'Clause Extraction', 'Rewrite Suggestions', 'Version Tracking'].map((f) => (
            <div key={f} className="upload-feature">
              <span className="feature-check">✓</span>
              {f}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};