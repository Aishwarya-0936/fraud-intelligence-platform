import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Zap } from 'lucide-react';
import { createTransaction } from '../api';

const PRESETS = [
  {
    label: 'Crypto Transfer',
    payload: {
      user_id: 'user_sim_001',
      amount: 150000,
      merchant: 'CryptoExchange',
      merchant_category: 'crypto',
      location: 'Dubai',
      device_id: 'device_new_001',
      destination_account: 'acc_unknown_999',
      transaction_type: 'transfer',
    },
  },
  {
    label: 'Geo Impossibility',
    payload: {
      user_id: 'user_sim_001',
      amount: 200000,
      merchant: 'CasinoRoyale',
      merchant_category: 'gambling',
      location: 'New York',
      device_id: 'device_new_002',
      destination_account: 'acc_unknown_888',
      transaction_type: 'transfer',
    },
  },
  {
    label: 'Normal Purchase',
    payload: {
      user_id: 'user_sim_002',
      amount: 1200,
      merchant: 'Amazon',
      merchant_category: 'retail',
      location: 'Chennai',
      device_id: 'device_known_001',
      destination_account: null,
      transaction_type: 'purchase',
    },
  },
  {
    label: 'High Value Transfer',
    payload: {
      user_id: 'user_sim_003',
      amount: 500000,
      merchant: 'WireTransfer',
      merchant_category: 'finance',
      location: 'Moscow',
      device_id: 'device_new_003',
      destination_account: 'acc_offshore_001',
      transaction_type: 'transfer',
    },
  },
];

const EMPTY_FORM = {
  user_id: '',
  amount: '',
  merchant: '',
  merchant_category: '',
  location: '',
  device_id: '',
  destination_account: '',
  transaction_type: 'transfer',
};

export default function SimulatePanel({ isOpen, onClose }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handlePreset = (preset) => {
    setForm(preset.payload);
    setResult(null);
    setError(null);
  };

  const handleChange = (e) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const payload = {
        ...form,
        amount: parseFloat(form.amount),
        destination_account: form.destination_account || null,
      };
      const res = await createTransaction(payload);
      setResult(res);
    } catch (err) {
      setError(err.response?.data?.detail || 'Transaction failed');
    } finally {
      setLoading(false);
    }
  };

  const RISK_COLORS = {
    LOW: '#3ddc84',
    MEDIUM: '#ffb020',
    HIGH: '#ff8c42',
    CRITICAL: '#ff3860',
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="modal-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            className="simulate-panel"
            initial={{ opacity: 0, x: 60 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 60 }}
            transition={{ type: 'spring', damping: 24, stiffness: 260 }}
          >
            <div className="panel-header">
              <span className="panel-title">Simulate Transaction</span>
              <button className="close-btn" onClick={onClose}>
                <X size={18} />
              </button>
            </div>

            <div className="preset-row">
              {PRESETS.map((p) => (
                <button
                  key={p.label}
                  className="preset-btn"
                  onClick={() => handlePreset(p)}
                >
                  {p.label}
                </button>
              ))}
            </div>

            <div className="form-grid">
              {[
                { name: 'user_id', label: 'User ID' },
                { name: 'amount', label: 'Amount (₹)', type: 'number' },
                { name: 'merchant', label: 'Merchant' },
                { name: 'merchant_category', label: 'Category' },
                { name: 'location', label: 'Location' },
                { name: 'device_id', label: 'Device ID' },
                { name: 'destination_account', label: 'Destination Account' },
              ].map((field) => (
                <div key={field.name} className="form-field">
                  <label className="field-label">{field.label}</label>
                  <input
                    className="field-input"
                    name={field.name}
                    type={field.type || 'text'}
                    value={form[field.name] || ''}
                    onChange={handleChange}
                    placeholder={field.label}
                  />
                </div>
              ))}

              <div className="form-field">
                <label className="field-label">Transaction Type</label>
                <select
                  className="field-input"
                  name="transaction_type"
                  value={form.transaction_type}
                  onChange={handleChange}
                >
                  <option value="transfer">Transfer</option>
                  <option value="purchase">Purchase</option>
                  <option value="withdrawal">Withdrawal</option>
                  <option value="deposit">Deposit</option>
                  <option value="credit">Credit</option>
                </select>
              </div>
            </div>

            <button
              className="submit-btn"
              onClick={handleSubmit}
              disabled={loading || !form.user_id || !form.amount}
            >
              <Zap size={16} />
              {loading ? 'Processing...' : 'Submit Transaction'}
            </button>

            {error && (
              <div className="result-card error">
                <span>Error: {error}</span>
              </div>
            )}

            {result && (
              <motion.div
                className="result-card"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ borderColor: RISK_COLORS[result.risk_level] }}
              >
                <div className="result-header">
                  <span
                    className="result-level"
                    style={{ color: RISK_COLORS[result.risk_level] }}
                  >
                    {result.risk_level}
                  </span>
                  <span className="result-score">Score: {result.risk_score}</span>
                </div>
                <div className="result-status">Status: {result.status}</div>
                {result.signals && (
                  <div className="result-signals">
                    {result.signals.split(', ').map((s) => (
                      <span key={s} className="signal-tag">{s}</span>
                    ))}
                  </div>
                )}
                {result.summary && (
                  <div className="result-summary">{result.summary}</div>
                )}
              </motion.div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}