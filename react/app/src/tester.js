import React, { useState } from "react";

const ApiTester = () => {
  const [url, setUrl] = useState("");
  const [method, setMethod] = useState("GET");
  const [payload, setPayload] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSendRequest = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const options = {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        ...(method !== "GET" && payload ? { body: payload } : {}),
      };

      const res = await fetch(url, options);
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5">
      <div className="card shadow-sm mb-4">
        <div className="card-body">
          <div className="mb-3">
            <label className="form-label">API URL</label>
            <input
              type="text"
              className="form-control"
              placeholder="https://example.com/api"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">Method</label>
            <select
              className="form-select"
              value={method}
              onChange={(e) => setMethod(e.target.value)}
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="DELETE">DELETE</option>
              <option value="PATCH">PATCH</option>
            </select>
          </div>

          <div className="mb-3">
            <label className="form-label">Payload (JSON)</label>
            <textarea
              className="form-control"
              placeholder='{"key": "value"}'
              value={payload}
              onChange={(e) => setPayload(e.target.value)}
              rows={6}
              disabled={method === "GET"}
            />
          </div>

          <button
            className="btn btn-primary"
            onClick={handleSendRequest}
            disabled={loading}
          >
            {loading ? "Sending..." : "Send Request"}
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          Error: {error}
        </div>
      )}

      {response && (
        <div className="card">
          <div className="card-body">
            <label className="form-label">Response</label>
            <pre className="bg-light p-3 rounded">
              {JSON.stringify(response, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiTester;
