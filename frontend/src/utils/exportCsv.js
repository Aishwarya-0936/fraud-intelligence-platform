export function exportTransactionsToCsv(transactions, filename = 'transactions.csv') {
  if (!transactions.length) return;

  const headers = ['id', 'user_id', 'amount', 'merchant', 'risk_level', 'risk_score', 'status', 'signals', 'timestamp'];
  const rows = transactions.map((tx) =>
    headers.map((h) => {
      const val = tx[h] ?? '';
      const escaped = String(val).replace(/"/g, '""');
      return `"${escaped}"`;
    }).join(',')
  );

  const csvContent = [headers.join(','), ...rows].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}