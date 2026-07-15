import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchInteractions } from "../../redux/slices/interactionsSlice";

const HCPHistoryList = () => {
  const dispatch = useDispatch();
  const { selectedHCP } = useSelector((state) => state.hcps);
  const { list, status } = useSelector((state) => state.interactions);

  useEffect(() => {
    if (selectedHCP) {
      dispatch(fetchInteractions(selectedHCP.id));
    }
  }, [selectedHCP, dispatch]);

  if (!selectedHCP) {
    return (
      <div className="history-empty-state">
        <div className="empty-icon">🏥</div>
        <p>Select an HCP to view their interaction history.</p>
      </div>
    );
  }

  return (
    <div className="hcp-history-list">
      <h3 className="history-title">Timeline</h3>
      {status === "loading" && <div className="history-loading">Loading history...</div>}
      {status === "succeeded" && list.length === 0 && (
        <div className="history-empty-state"><p>No past interactions found.</p></div>
      )}
      
      <div className="timeline">
        {list.map((ix) => (
          <div key={ix.id} className="history-card glass-panel">
            <div className="history-card-header">
              <span className="history-date">{ix.interaction_date}</span>
              {ix.channel && <span className={`badge channel-${ix.channel.toLowerCase()}`}>{ix.channel}</span>}
            </div>
            <p className="history-summary">{ix.summary || ix.raw_input || "No summary provided."}</p>
            <div className="history-card-footer">
              {ix.sentiment && (
                <span className={`badge sentiment-${ix.sentiment.toLowerCase()}`}>{ix.sentiment}</span>
              )}
              {ix.follow_up_required && (
                <span className="badge followup-required">Follow-up: {ix.follow_up_date}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HCPHistoryList;
