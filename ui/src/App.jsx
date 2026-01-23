import React, { useState } from "react";

// --- Sub-components (in a real app, these would be separate files) ---

const LandingView = ({ onSearch, initialQuery }) => {
  const [query, setQuery] = useState(initialQuery || "");

  const handleSubmit = () => {
    if (query.trim()) onSearch(query);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSubmit();
  };

  return (
    <div className="landing-container">
      {/* Logo Section */}
      <div className="logo-container">
        {/* Simple CSS Dog Icon */}
        <div
          style={{
            width: "80px",
            height: "80px",
            background: "#289B9F",
            borderRadius: "50%",
            marginBottom: "20px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <span style={{ fontSize: "40px" }}>🐕</span>
        </div>

        <div className="logo-main">
          <span className="logo-buddy">Buddy</span>
          <span className="logo-fetch">Fetch</span>
        </div>
        <div className="logo-subtitle">An AI-powered semantic search tool</div>
      </div>

      {/* Search Input */}
      <div className="search-wrapper">
        <div className="search-input-container">
          <input
            className="search-input"
            placeholder="Search 1,580,000 emails from the Clinton Presidential Library"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
          />
        </div>
        <div className="search-button" onClick={handleSubmit}>
          Search
        </div>
      </div>

      {/* Suggestions */}
      <div className="suggestions-row">
        <span style={{ opacity: 0.8 }}>Try:</span>
        <div
          className="suggestion-chip"
          onClick={() => onSearch("Kosovo peacekeeping")}
        >
          role of intelligence in supporting policymaking during the 1992-1995
          Bosnian war
        </div>
        <div
          className="suggestion-chip"
          onClick={() => onSearch("Elena Kagan")}
        >
          Elena Kagan
        </div>
        <div
          className="suggestion-chip"
          onClick={() => onSearch("sweat shop abuses")}
        >
          sweat shop abuses
        </div>
      </div>
    </div>
  );
};

const ResultCard = ({ result, onClick }) => {
  // Format date if available
  const dateStr = result.date
    ? new Date(result.date).toLocaleDateString()
    : "Unknown Date";

  return (
    <div className="result-card" onClick={() => onClick(result)}>
      <div className="result-subject">{result.title}</div>
      <div className="result-meta">
        <span>{dateStr}</span>
        <span>•</span>
        <span>
          {result.url.includes("fake-archive")
            ? "Presidential Record"
            : "External"}
        </span>
      </div>
      <div
        className="result-snippet"
        dangerouslySetInnerHTML={{ __html: result.snippet }}
      ></div>
    </div>
  );
};

const ResultsView = ({
  results,
  query,
  onSearch,
  loading,
  onResultClick,
  onClear,
}) => {
  const [localQuery, setLocalQuery] = useState(query);

  return (
    <div className="results-container">
      <div className="results-header">
        <div className="results-header-logo" onClick={onClear}>
          <span>Buddy</span>
          <span style={{ color: "var(--color-teal-accent)" }}>Fetch</span>
        </div>
        <div className="results-search-bar">
          <div className="search-input-container" style={{ height: "40px" }}>
            <input
              className="search-input"
              value={localQuery}
              onChange={(e) => setLocalQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && onSearch(localQuery)}
            />
          </div>
          <div
            className="search-button"
            style={{ width: "80px", height: "40px" }}
            onClick={() => onSearch(localQuery)}
          >
            Search
          </div>
        </div>
      </div>

      <div className="results-list">
        {loading ? (
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              padding: "40px",
            }}
          >
            <div className="loader"></div>
          </div>
        ) : (
          <>
            <div style={{ marginBottom: "16px", color: "#666" }}>
              Found {results.length} results for "{query}"
            </div>
            {results.map((r) => (
              <ResultCard key={r.id} result={r} onClick={onResultClick} />
            ))}
          </>
        )}
      </div>
    </div>
  );
};

const EmailDrawer = ({ email, onClose }) => {
  if (!email) return null;

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-close" onClick={onClose}>
          &times;
        </div>

        <div className="drawer-header">
          <div className="drawer-title">{email.title}</div>
          <div className="drawer-meta-row">
            <strong>From:</strong> {email.author || "Unknown"}
          </div>
          <div className="drawer-meta-row">
            <strong>To:</strong> {email.to || "Unknown"}
          </div>
          <div className="drawer-meta-row">
            <strong>Agency:</strong> {email.agency || "N/A"}
          </div>
          <div className="drawer-meta-row">
            <strong>Date:</strong>{" "}
            {email.date ? new Date(email.date).toLocaleDateString() : "N/A"}
          </div>
          <div className="drawer-meta-row">
            <strong>Link:</strong>{" "}
            <a
              href={email.url}
              target="_blank"
              rel="noreferrer"
              style={{ color: "#4AA3A2" }}
            >
              View Original Record
            </a>
          </div>
        </div>

        <div className="drawer-body">
          <div className="content-section">
            <span className="content-label">Content</span>
            <div className="email-body-text">
              {email.body && email.body !== "No content available." ? (
                email.body
              ) : (
                /* Fallback to snippet if body is missing, removing HTML tags for cleaner look if prefered, but keeping simpler for now */
                <div dangerouslySetInnerHTML={{ __html: email.snippet }} />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  const [view, setView] = useState("landing"); // 'landing' | 'results'
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState(null);

  const performSearch = async (searchQuery) => {
    setLoading(true);
    setQuery(searchQuery);
    setView("results");

    try {
      const response = await fetch("http://localhost:8080/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery }),
      });
      const data = await response.json();

      if (!response.ok) {
        console.error("Search error:", data.error);
        setResults([]);
      } else {
        setResults(data.results || []);
      }
    } catch (err) {
      console.error("Search failed:", err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setView("landing");
    setQuery("");
    setResults([]);
  };

  return (
    <div className="App">
      {view === "landing" ? (
        <LandingView onSearch={performSearch} />
      ) : (
        <ResultsView
          results={results}
          query={query}
          onSearch={performSearch}
          loading={loading}
          onResultClick={setSelectedEmail}
          onClear={handleClear}
        />
      )}

      {selectedEmail && (
        <EmailDrawer
          email={selectedEmail}
          onClose={() => setSelectedEmail(null)}
        />
      )}
    </div>
  );
}

export default App;
