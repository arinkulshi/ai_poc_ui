import { useState, useEffect } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "";

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
      <div className="logo-section">
        <div className="logo-header">
          <div className="dog-illustration">
            <img src="/Vector.svg" alt="BuddyFetch Logo" />
          </div>
          <div className="logo-text">
            <h1 className="logo-title">
              <span className="logo-buddy">Buddy</span>
              <span className="logo-fetch">Fetch</span>
            </h1>
            <p className="logo-subtitle">An AI-powered semantic search tool</p>
          </div>
        </div>
      </div>

      <div className="search-section">
        <div className="search-wrapper">
          <input
            type="text"
            className="search-input"
            placeholder="Search the Enron email corpus"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button className="search-button" onClick={handleSubmit}>
            Search
          </button>
        </div>
      </div>

      <div className="suggestions-section">
        <span className="suggestions-label">Try:</span>
        <div className="suggestions-chips">
          <button
            className="suggestion-chip"
            onClick={() =>
              onSearch("concerns about hiding losses from investors")
            }
          >
            concerns about hiding losses from investors
          </button>
          <button
            className="suggestion-chip"
            onClick={() => onSearch("California energy crisis power prices")}
          >
            California energy crisis power prices
          </button>
          <button
            className="suggestion-chip"
            onClick={() => onSearch("natural gas trading strategies")}
          >
            natural gas trading strategies
          </button>
        </div>
      </div>
    </div>
  );
};

const ResultCard = ({ result, onClick }) => {
  const dateStr = result.date
    ? new Date(result.date).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      })
    : "Unknown Date";

  return (
    <div className="result-card" onClick={() => onClick(result)}>
      <div className="result-header">
        <h3 className="result-title">{result.title}</h3>
      </div>

      <div className="result-meta">
        <span className="result-date">{dateStr}</span>
        <span className="result-separator">&bull;</span>
        <span className="result-source">{result.folder || "Email"}</span>
        {result.author && (
          <>
            <span className="result-separator">&bull;</span>
            <span className="result-author">From: {result.author}</span>
          </>
        )}
      </div>

      <div className="result-abstract-label">Snippet</div>

      <div
        className="result-snippet"
        dangerouslySetInnerHTML={{ __html: result.snippet }}
      />
    </div>
  );
};

const SummaryCard = ({ summary, summaryRefs, results, onResultClick }) => {
  if (!summary) return null;

  // Replace [N] and [N, M, ...] citation markers with clickable links
  const renderSummaryWithCitations = () => {
    const parts = summary.split(/(\[\d+(?:,\s*\d+)*\])/g);
    return parts.map((part, i) => {
      const match = part.match(/^\[(\d+(?:,\s*\d+)*)\]$/);
      if (match) {
        const indices = match[1].split(/,\s*/).map((n) => parseInt(n, 10) - 1);
        return indices.map((refIndex, j) => {
          const ref = summaryRefs[refIndex];
          const matchedResult = ref
            ? results.find((r) => ref.document && ref.document.includes(r.id))
            : null;
          return (
            <button
              key={`${i}-${j}`}
              className="citation-link"
              onClick={(e) => {
                e.stopPropagation();
                if (matchedResult) onResultClick(matchedResult);
              }}
              title={ref?.title || `Reference ${refIndex + 1}`}
            >
              [{refIndex + 1}]
            </button>
          );
        });
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="summary-card">
      <div className="summary-header">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path
            d="M8 1L10 5.5L15 6.5L11.5 10L12.5 15L8 12.5L3.5 15L4.5 10L1 6.5L6 5.5L8 1Z"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinejoin="round"
          />
        </svg>
        <span>AI Summary Of First 5 Emails</span>
      </div>
      <p className="summary-text">{renderSummaryWithCitations()}</p>
    </div>
  );
};

const ResultsView = ({
  results,
  query,
  summary,
  summaryRefs,
  onSearch,
  loading,
  onResultClick,
  onClear,
  currentPage,
  totalResults,
  pageSize,
  filters,
  onFiltersChange,
}) => {
  const [localQuery, setLocalQuery] = useState(query);
  const [showFilters, setShowFilters] = useState(false);
  const totalPages = Math.ceil(totalResults / pageSize);

  const handleKeyDown = (e) => {
    if (e.key === "Enter") onSearch(localQuery, 1, filters);
  };

  const handleFilterChange = (field, value) => {
    onFiltersChange({ ...filters, [field]: value });
  };

  const handleSearchClick = () => {
    onSearch(localQuery, 1, filters);
  };

  const clearFilters = () => {
    onFiltersChange({ sender: "", subject: "", to: "" });
  };

  const hasActiveFilters = filters.sender || filters.subject || filters.to;

  return (
    <div className="results-container">
      <div className="results-header">
        <div className="results-logo" onClick={onClear}>
          <img
            src="/logo-light-mode.jpg"
            alt="BuddyFetch Logo"
            className="results-logo-image"
          />
          <span className="results-logo-buddy">Buddy</span>
          <span className="results-logo-fetch">Fetch</span>
        </div>

        <div className="results-search-wrapper">
          <div className="results-search-input-wrapper">
            <svg
              className="results-search-icon"
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M7 12C9.76142 12 12 9.76142 12 7C12 4.23858 9.76142 2 7 2C4.23858 2 2 4.23858 2 7C2 9.76142 4.23858 12 7 12Z"
                stroke="#6B7280"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M14 14L10.5 10.5"
                stroke="#6B7280"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <input
              type="text"
              className="results-search-input"
              value={localQuery}
              onChange={(e) => setLocalQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Search emails..."
            />
          </div>
          <button
            className="results-search-button"
            onClick={handleSearchClick}
          >
            Search
          </button>
          <button
            className={`filter-toggle-button ${showFilters ? "active" : ""}`}
            onClick={() => setShowFilters(!showFilters)}
            title="Toggle filters"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M2 4h12M4 8h8M6 12h4"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
            {hasActiveFilters && <span className="filter-badge" />}
          </button>
        </div>
      </div>

      {showFilters && (
        <div className="filters-bar">
          <div className="filter-input-group">
            <label>From:</label>
            <input
              type="text"
              placeholder="sender email"
              value={filters.sender}
              onChange={(e) => handleFilterChange("sender", e.target.value)}
            />
          </div>
          <div className="filter-input-group">
            <label>To:</label>
            <input
              type="text"
              placeholder="recipient email"
              value={filters.to}
              onChange={(e) => handleFilterChange("to", e.target.value)}
            />
          </div>
          <div className="filter-input-group">
            <label>Subject:</label>
            <input
              type="text"
              placeholder="exact subject"
              value={filters.subject}
              onChange={(e) => handleFilterChange("subject", e.target.value)}
            />
          </div>
          {hasActiveFilters && (
            <button className="clear-filters-button" onClick={clearFilters}>
              Clear
            </button>
          )}
        </div>
      )}

      <div className="results-content">
        {loading ? (
          <div className="results-loading">
            <div className="loader"></div>
            <p>Searching...</p>
          </div>
        ) : (
          <>
            <SummaryCard
              summary={summary}
              summaryRefs={summaryRefs}
              results={results}
              onResultClick={onResultClick}
            />
            <div className="results-count">
              <span className="results-count-number">
                Showing {(currentPage - 1) * pageSize + 1}–
                {Math.min(currentPage * pageSize, totalResults)} of{" "}
                {totalResults} results for{" "}
              </span>
              <span className="results-count-query">"{query}"</span>
            </div>
            <div className="results-list">
              {results.map((r) => (
                <ResultCard key={r.id} result={r} onClick={onResultClick} />
              ))}
            </div>
            {totalPages > 1 && (
              <div className="pagination-bar">
                <button
                  className="pagination-button"
                  disabled={currentPage <= 1}
                  onClick={() => onSearch(query, currentPage - 1, filters)}
                >
                  Previous
                </button>
                <span className="pagination-info">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  className="pagination-button"
                  disabled={currentPage >= totalPages}
                  onClick={() => onSearch(query, currentPage + 1, filters)}
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

const EmailDrawer = ({ email, onClose }) => {
  if (!email) return null;

  const dateStr = email.date
    ? new Date(email.date).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "Unknown Date";

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        <button
          className="drawer-close"
          onClick={onClose}
          aria-label="Close drawer"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path
              d="M18 6L6 18M6 6L18 18"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </button>

        <div className="drawer-header">
          <div className="drawer-subject-row">
            <h2 className="drawer-subject-value">Subject: {email.title}</h2>
          </div>

          <div className="drawer-metadata">
            {email.author && (
              <div className="drawer-meta-row">
                <span className="drawer-meta-label">From:</span>
                <span className="drawer-meta-value">{email.author}</span>
              </div>
            )}

            {email.to && (
              <div className="drawer-meta-row">
                <span className="drawer-meta-label">To:</span>
                <span className="drawer-meta-value">{email.to}</span>
              </div>
            )}

            <div className="drawer-meta-row">
              <span className="drawer-meta-label">Date:</span>
              <span className="drawer-meta-value">{dateStr}</span>
            </div>

            {email.folder && (
              <div className="drawer-meta-row">
                <span className="drawer-meta-label">Folder:</span>
                <span className="drawer-meta-value">{email.folder}</span>
              </div>
            )}
          </div>
        </div>

        <div className="drawer-body">
          <div className="drawer-content-section">
            <h3 className="drawer-content-label">Email Body</h3>
            <div
              className="drawer-content-text"
              dangerouslySetInnerHTML={{
                __html: email.body || email.snippet || "No content available.",
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

const PasswordGate = ({ onAuthenticated }) => {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    // Check if already authenticated
    const token = sessionStorage.getItem("auth_token");
    if (token) {
      onAuthenticated(token);
    }
    setChecking(false);
  }, []);

  const handleSubmit = async () => {
    setError("");
    try {
      const res = await fetch(`${API_BASE}/verify-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError("Incorrect password");
        return;
      }
      sessionStorage.setItem("auth_token", data.token);
      onAuthenticated(data.token);
    } catch {
      setError("Connection failed");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSubmit();
  };

  if (checking) return null;

  return (
    <div className="landing-container">
      <div className="logo-section">
        <div className="logo-header">
          <div className="dog-illustration">
            <img src="/Vector.svg" alt="BuddyFetch Logo" />
          </div>
          <div className="logo-text">
            <h1 className="logo-title">
              <span className="logo-buddy">Buddy</span>
              <span className="logo-fetch">Fetch</span>
            </h1>
            <p className="logo-subtitle">Enter password to continue</p>
          </div>
        </div>
      </div>
      <div className="search-section">
        <div className="search-wrapper">
          <input
            type="password"
            className="search-input"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus
          />
          <button className="search-button" onClick={handleSubmit}>
            Enter
          </button>
        </div>
        {error && (
          <p style={{ color: "#e74c3c", marginTop: "0.5rem" }}>{error}</p>
        )}
      </div>
    </div>
  );
};

function App() {
  const [authToken, setAuthToken] = useState(
    sessionStorage.getItem("auth_token"),
  );
  const [view, setView] = useState("landing");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [summary, setSummary] = useState("");
  const [summaryRefs, setSummaryRefs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const [filters, setFilters] = useState({ sender: "", subject: "", to: "" });
  const pageSize = 10;

  if (!authToken) {
    return <PasswordGate onAuthenticated={setAuthToken} />;
  }

  const performSearch = async (searchQuery, page = 1, searchFilters = filters) => {
    setLoading(true);
    setQuery(searchQuery);
    setCurrentPage(page);
    setView("results");

    // Build filters object with only non-empty values
    const activeFilters = {};
    if (searchFilters.sender) activeFilters.sender = searchFilters.sender;
    if (searchFilters.subject) activeFilters.subject = searchFilters.subject;
    if (searchFilters.to) activeFilters.to = searchFilters.to;

    try {
      const response = await fetch(`${API_BASE}/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          query: searchQuery,
          page,
          page_size: pageSize,
          filters: Object.keys(activeFilters).length > 0 ? activeFilters : undefined,
        }),
      });
      const data = await response.json();

      if (response.status === 401) {
        sessionStorage.removeItem("auth_token");
        setAuthToken(null);
        return;
      }

      if (!response.ok) {
        console.error("Search error:", data.error);
        setResults([]);
        setSummary("");
        setSummaryRefs([]);
        setTotalResults(0);
      } else {
        setResults(data.results || []);
        setSummary(data.summary || "");
        setSummaryRefs(data.summary_references || []);
        setTotalResults(data.total_size || 0);
      }
    } catch (err) {
      console.error("Search failed:", err);
      setResults([]);
      setTotalResults(0);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setView("landing");
    setQuery("");
    setResults([]);
    setSummary("");
    setSummaryRefs([]);
    setSelectedEmail(null);
    setCurrentPage(1);
    setTotalResults(0);
  };

  return (
    <div className="App">
      {view === "landing" ? (
        <LandingView onSearch={performSearch} initialQuery={query} />
      ) : (
        <ResultsView
          results={results}
          query={query}
          summary={summary}
          summaryRefs={summaryRefs}
          onSearch={performSearch}
          loading={loading}
          onResultClick={setSelectedEmail}
          onClear={handleClear}
          currentPage={currentPage}
          totalResults={totalResults}
          pageSize={pageSize}
          filters={filters}
          onFiltersChange={setFilters}
        />
      )}

      <EmailDrawer
        email={selectedEmail}
        onClose={() => setSelectedEmail(null)}
      />
    </div>
  );
}

export default App;
