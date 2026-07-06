import { useEffect, useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Download } from 'lucide-react';
import { getTransactions } from '../api';
import { exportTransactionsToCsv } from '../utils/exportCsv';
import toast from 'react-hot-toast';
import AnimatedNumber from './AnimatedNumber';
import TransactionModal from './TransactionModal';
import './Dashboard.css';

const RISK_COLORS = {
  LOW: '#3ddc84',
  MEDIUM: '#f5c542',
  HIGH: '#ff6b2b',
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

export default function Dashboard() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [modalTx, setModalTx] = useState(null);
  const seenIds = useRef(new Set());
  const isFirstLoad = useRef(true);

  const fetchData = useCallback(async () => {
    try {
      const data = await getTransactions({ limit: 30 });

      if (!isFirstLoad.current) {
        data.items.forEach((tx) => {
          if (!seenIds.current.has(tx.id) && ['HIGH', 'CRITICAL'].includes(tx.risk_level)) {
            toast(
              `${tx.risk_level} risk: ₹${Number(tx.amount).toLocaleString()} · ${tx.merchant || 'Unknown'}`,
              {
                duration: 10000,
                style: {
                  borderColor:
                    tx.risk_level === 'CRITICAL'
                      ? 'rgba(255,56,96,0.5)'
                      : 'rgba(255,107,43,0.5)',
                },
              }
            );
          }
        });
      }

      data.items.forEach((tx) => seenIds.current.add(tx.id));
      isFirstLoad.current = false;

      setTransactions(data.items);
    } catch (err) {
      console.error('Failed to fetch transactions', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const total = transactions.length;
  const flaggedCount = transactions.filter((t) =>
    ['flagged', 'pending_review', 'blocked'].includes(t.status)
  ).length;
  const avgRisk = total
    ? Math.round(transactions.reduce((sum, t) => sum + Number(t.risk_score), 0) / total)
    : 0;

  const riskDistribution = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((level) => ({
    name: level,
    value: transactions.filter((t) => t.risk_level === level).length,
  })).filter((d) => d.value > 0);

  const filteredTransactions = transactions.filter((tx) => {
    const matchesRisk = riskFilter === 'ALL' || tx.risk_level === riskFilter;
    const query = searchQuery.toLowerCase();
    const matchesSearch =
      !query ||
      tx.merchant?.toLowerCase().includes(query) ||
      tx.user_id?.toLowerCase().includes(query);
    return matchesRisk && matchesSearch;
  });

  return (
    <div className="dashboard">
      <div className="stats-column">
        <div className="stat-card">
          <div className="stat-label">Total Transactions</div>
          <div className="stat-value"><AnimatedNumber value={total} /></div>
          <div className="stat-sub">last 30 processed</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Flagged for Review</div>
          <div className="stat-value danger"><AnimatedNumber value={flaggedCount} /></div>
          <div className="stat-sub">{total ? Math.round((flaggedCount / total) * 100) : 0}% of feed</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Avg Risk Score</div>
          <div className="stat-value accent"><AnimatedNumber value={avgRisk} /></div>
          <div className="stat-sub">out of 150</div>
        </div>

        {riskDistribution.length > 0 && (
          <div className="risk-chart-card">
            <div className="stat-label">Risk Distribution</div>
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie
                  data={riskDistribution}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={40}
                  outerRadius={65}
                  paddingAngle={3}
                >
                  {riskDistribution.map((entry) => (
                    <Cell key={entry.name} fill={RISK_COLORS[entry.name]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: 'var(--bg-panel-raised)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 8,
                    fontFamily: 'var(--font-mono)',
                    fontSize: 12,
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="feed-column">
        <div className="feed-header">
          <span className="feed-title">Live Transaction Feed</span>
        </div>

        <div className="filter-bar">
          <input
            className="filter-search"
            type="text"
            placeholder="Search by merchant or user ID…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {['ALL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((level) => (
            <button
              key={level}
              className={`filter-chip ${riskFilter === level ? `active ${level}` : ''}`}
              onClick={() => setRiskFilter(level)}
            >
              {level}
            </button>
          ))}
          <button
            className="filter-chip"
            onClick={() => exportTransactionsToCsv(filteredTransactions)}
            title="Export visible transactions to CSV"
          >
            <Download size={14} style={{ marginRight: 4, verticalAlign: 'middle' }} />
            Export
          </button>
        </div>

        {loading && <div className="empty-state">Loading transactions…</div>}
        {!loading && filteredTransactions.length === 0 && (
          <div className="empty-state">
            {transactions.length === 0
              ? 'No transactions yet. Try simulating one to see the system in action.'
              : 'No transactions match your search/filter.'}
          </div>
        )}

        <AnimatePresence initial={false}>
          {filteredTransactions.map((tx) => {
            const score = Number(tx.risk_score);
            const scorePercent = Math.min((score / 150) * 100, 100);
            const scoreColor = RISK_COLORS[tx.risk_level];
            const isExpanded = expanded === tx.id;
            const isReviewed = ['approved', 'rejected', 'escalated'].includes(tx.status);

            return (
              <motion.div
                key={tx.id}
                layout
                initial={{ opacity: 0, y: -12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                className={`tx-card ${tx.risk_level === 'CRITICAL' && !isReviewed ? 'critical' : ''}`}
                onClick={() => setExpanded(isExpanded ? null : tx.id)}
                style={{ cursor: 'pointer' }}
              >
                <span
                  className={`risk-badge ${tx.risk_level}`}
                  onClick={(e) => { e.stopPropagation(); setModalTx(tx); }}
                  title="Click for full details"
                >
                  {tx.risk_level}
                </span>

                <div className="tx-main">
                  <div className="tx-top-row">
                    <span className="tx-amount">₹{Number(tx.amount).toLocaleString()}</span>
                    <span className="tx-merchant">{tx.merchant || 'Unknown merchant'}</span>
                  </div>
                  {tx.signals && (
                    <div className="tx-signals">
                      {tx.signals.split(', ').map((sig) => (
                        <span key={sig} className="signal-tag">{sig.replace(/_/g, ' ')}</span>
                      ))}
                    </div>
                  )}
                  <div className="score-bar-wrap">
                    <div
                      className="score-bar-fill"
                      style={{ width: `${scorePercent}%`, background: scoreColor }}
                    />
                  </div>

                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        className="tx-summary-expanded"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.25 }}
                      >
                        <div className="tx-summary-label">AI ANALYSIS</div>
                        <div className="tx-summary-text">
                          {tx.summary || 'No AI summary available for this transaction.'}
                        </div>
                        <div className="tx-summary-meta">
                          <span>Score: {score} / 150</span>
                          <span>Status: {tx.status}</span>
                          <span>Type: {tx.transaction_type}</span>
                          {tx.device_id && <span>Device: {tx.device_id}</span>}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                <div className="tx-meta">
                  <div className="tx-user">{tx.user_id}</div>
                  <div
                    className="tx-time"
                    title={new Date(tx.timestamp).toLocaleString()}
                  >
                    {timeAgo(tx.timestamp)}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      <TransactionModal transaction={modalTx} onClose={() => setModalTx(null)} />
    </div>
  );
}