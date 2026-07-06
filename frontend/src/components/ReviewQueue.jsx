import { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { getTransactions, reviewTransaction } from '../api';

const RISK_COLORS = {
  LOW: '#3ddc84',
  MEDIUM: '#ffb020',
  HIGH: '#ff8c42',
  CRITICAL: '#ff3860',
};

function timeAgo(timestamp) {
  const seconds = Math.floor((Date.now() - new Date(timestamp)) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ago`;
}

export default function ReviewQueue() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reviewing, setReviewing] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const [high, critical] = await Promise.all([
        getTransactions({ risk_level: 'HIGH', limit: 50 }),
        getTransactions({ risk_level: 'CRITICAL', limit: 50 }),
      ]);
      const combined = [...critical.items, ...high.items].sort(
        (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
      );
      setTransactions(combined);
    } catch (err) {
      console.error('Failed to fetch review queue', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleReview = async (id, decision) => {
    setReviewing(id);
    try {
      await reviewTransaction(id, decision, null);
      await fetchData();
    } catch (err) {
      console.error('Review failed', err);
    } finally {
      setReviewing(null);
    }
  };

  const pending = transactions.filter(
    (t) => !['approved', 'rejected', 'escalated'].includes(t.status)
  );
  const reviewed = transactions.filter(
    (t) => ['approved', 'rejected', 'escalated'].includes(t.status)
  );

  return (
    <div className="review-queue">
      <div className="queue-header">
        <ShieldAlert size={18} />
        <span>Review Queue</span>
        <span className="queue-count">{pending.length} pending</span>
      </div>

      {loading && <div className="empty-state">Loading...</div>}
      {!loading && pending.length === 0 && (
        <div className="empty-state">No transactions pending review.</div>
      )}

      <div className="queue-section-label">PENDING REVIEW</div>
      <AnimatePresence>
        {pending.map((tx) => (
          <motion.div
            key={tx.id}
            layout
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="review-card"
            style={{ borderLeftColor: RISK_COLORS[tx.risk_level] }}
          >
            <div className="review-card-top">
              <span
                className="risk-badge"
                style={{ color: RISK_COLORS[tx.risk_level] }}
              >
                {tx.risk_level}
              </span>
              <span className="tx-amount">₹{Number(tx.amount).toLocaleString()}</span>
              <span className="tx-merchant">{tx.merchant || 'Unknown'}</span>
              <span className="tx-time">{timeAgo(tx.timestamp)}</span>
            </div>

            <div className="review-card-user">
              {tx.user_id} · {tx.location || 'Unknown location'} · {tx.transaction_type}
            </div>

            {tx.signals && (
              <div className="tx-signals">
                {tx.signals.split(', ').map((s) => (
                  <span key={s} className="signal-tag">{s}</span>
                ))}
              </div>
            )}

            {tx.summary && (
              <div className="review-summary">{tx.summary}</div>
            )}

            <div className="review-actions">
              <button
                className="action-btn approve"
                disabled={reviewing === tx.id}
                onClick={() => handleReview(tx.id, 'approve')}
              >
                <CheckCircle size={14} />
                Approve
              </button>
              <button
                className="action-btn reject"
                disabled={reviewing === tx.id}
                onClick={() => handleReview(tx.id, 'reject')}
              >
                <XCircle size={14} />
                Reject
              </button>
              <button
                className="action-btn escalate"
                disabled={reviewing === tx.id}
                onClick={() => handleReview(tx.id, 'escalate')}
              >
                <AlertTriangle size={14} />
                Escalate
              </button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {reviewed.length > 0 && (
        <>
          <div className="queue-section-label" style={{ marginTop: 24 }}>REVIEWED</div>
          {reviewed.map((tx) => (
            <div
              key={tx.id}
              className="review-card reviewed"
              style={{ borderLeftColor: RISK_COLORS[tx.risk_level] }}
            >
              <div className="review-card-top">
                <span className="risk-badge" style={{ color: RISK_COLORS[tx.risk_level] }}>
                  {tx.risk_level}
                </span>
                <span className="tx-amount">₹{Number(tx.amount).toLocaleString()}</span>
                <span className="tx-merchant">{tx.merchant || 'Unknown'}</span>
                <span
                  className="reviewed-status"
                  style={{
                    color:
                      tx.status === 'approved' ? '#3ddc84'
                      : tx.status === 'rejected' ? '#ff3860'
                      : '#ffb020',
                  }}
                >
                  {tx.status.toUpperCase()}
                </span>
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  );
}