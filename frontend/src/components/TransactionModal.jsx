import { motion, AnimatePresence } from 'framer-motion';
import { X, Copy } from 'lucide-react';
import toast from 'react-hot-toast';
import './TransactionModal.css';

export default function TransactionModal({ transaction, onClose }) {
  if (!transaction) return null;

  const copyId = () => {
    navigator.clipboard.writeText(transaction.id);
    toast('Transaction ID copied', { duration: 2000 });
  };

  return (
    <AnimatePresence>
      <motion.div
        className="modal-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="modal-box"
          initial={{ opacity: 0, scale: 0.95, y: 12 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 12 }}
          transition={{ duration: 0.2 }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="modal-header">
            <span className={`risk-badge ${transaction.risk_level}`}>
              {transaction.risk_level}
            </span>
            <button className="modal-close" onClick={onClose}>
              <X size={18} />
            </button>
          </div>

          <div className="modal-amount">₹{Number(transaction.amount).toLocaleString()}</div>
          <div className="modal-merchant">{transaction.merchant || 'Unknown merchant'}</div>

          <div className="modal-grid">
            <div className="modal-field">
              <span className="modal-field-label">User ID</span>
              <span className="modal-field-value">{transaction.user_id}</span>
            </div>
            <div className="modal-field">
              <span className="modal-field-label">Status</span>
              <span className="modal-field-value">{transaction.status}</span>
            </div>
            <div className="modal-field">
              <span className="modal-field-label">Risk Score</span>
              <span className="modal-field-value">{Number(transaction.risk_score)} / 150</span>
            </div>
            <div className="modal-field">
              <span className="modal-field-label">Type</span>
              <span className="modal-field-value">{transaction.transaction_type}</span>
            </div>
            <div className="modal-field">
              <span className="modal-field-label">Location</span>
              <span className="modal-field-value">{transaction.location || '—'}</span>
            </div>
            <div className="modal-field">
              <span className="modal-field-label">Device ID</span>
              <span className="modal-field-value">{transaction.device_id || '—'}</span>
            </div>
            <div className="modal-field">
              <span className="modal-field-label">Destination Account</span>
              <span className="modal-field-value">{transaction.destination_account || '—'}</span>
            </div>
            <div className="modal-field">
              <span className="modal-field-label">Timestamp</span>
              <span className="modal-field-value">{new Date(transaction.timestamp).toLocaleString()}</span>
            </div>
          </div>

          {transaction.signals && (
            <div className="modal-section">
              <div className="modal-section-label">Fraud Signals</div>
              <div className="modal-signals">
                {transaction.signals.split(', ').map((sig) => (
                  <span key={sig} className="signal-tag">{sig.replace(/_/g, ' ')}</span>
                ))}
              </div>
            </div>
          )}

          {transaction.summary && (
            <div className="modal-section">
              <div className="modal-section-label">AI Analysis</div>
              <div className="modal-summary">{transaction.summary}</div>
            </div>
          )}

          {transaction.review_decision && (
            <div className="modal-section">
              <div className="modal-section-label">Review Decision</div>
              <div className="modal-summary">
                {transaction.review_decision} · {new Date(transaction.reviewed_at).toLocaleString()}
              </div>
            </div>
          )}

          <button className="modal-copy-btn" onClick={copyId}>
            <Copy size={14} />
            Copy Transaction ID
          </button>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}