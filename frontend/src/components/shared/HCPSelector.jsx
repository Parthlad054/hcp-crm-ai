import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { searchHCPs, selectHCP, clearHCPSelection } from "../../redux/slices/hcpSlice";

const HCPSelector = () => {
  const dispatch = useDispatch();
  const { list, selectedHCP, status } = useSelector((state) => state.hcps);
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (query.trim() !== "") {
        dispatch(searchHCPs(query));
        setIsOpen(true);
      } else {
        setIsOpen(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [query, dispatch]);

  const handleSelect = (hcp) => {
    dispatch(selectHCP(hcp));
    setQuery("");
    setIsOpen(false);
  };

  const handleClear = () => {
    dispatch(clearHCPSelection());
  };

  return (
    <div className="hcp-selector glass-panel">
      {selectedHCP ? (
        <div className="selected-hcp-card">
          <div className="hcp-info">
            <span className="hcp-name">{selectedHCP.name}</span>
            <span className="hcp-specialty">{selectedHCP.specialty}</span>
          </div>
          <button className="clear-btn" onClick={handleClear} aria-label="Clear selection">✕</button>
        </div>
      ) : (
        <div className="search-container">
          <input
            type="text"
            className="search-input"
            placeholder="Search HCPs by name (e.g. Smith)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          {isOpen && list.length > 0 && (
            <ul className="dropdown-list glass-panel">
              {list.map((hcp) => (
                <li key={hcp.id} onClick={() => handleSelect(hcp)} className="dropdown-item">
                  <div className="hcp-name">{hcp.name}</div>
                  <div className="hcp-subtext">{hcp.specialty}</div>
                </li>
              ))}
            </ul>
          )}
          {isOpen && status === "loading" && <div className="dropdown-list glass-panel"><div className="dropdown-item">Searching...</div></div>}
        </div>
      )}
    </div>
  );
};

export default HCPSelector;
