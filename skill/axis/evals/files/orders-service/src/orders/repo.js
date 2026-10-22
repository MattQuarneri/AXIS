const { run, all } = require('../db/connection');

async function insertOrder(order) {
  const result = await run('INSERT INTO orders (customer_id, status, total) VALUES (?, ?, ?)', [order.customerId, order.status, order.total]);
  for (const item of order.items) {
    await run('INSERT INTO order_items (order_id, sku, qty, unit_price) VALUES (?, ?, ?, ?)', [result.lastID, item.sku, item.qty, item.unitPrice]);
  }
  return result.lastID;
}

async function findOrder(id) {
  const rows = await all('SELECT * FROM orders WHERE id = ?', [id]);
  if (!rows.length) return null;
  const items = await all('SELECT sku, qty, unit_price AS unitPrice FROM order_items WHERE order_id = ?', [id]);
  return { ...rows[0], items };
}

async function setStatus(id, status) {
  await run('UPDATE orders SET status = ? WHERE id = ?', [status, id]);
}

module.exports = { insertOrder, findOrder, setStatus };
