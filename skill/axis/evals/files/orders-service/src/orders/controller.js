const service = require('./service');
const repo = require('./repo');

async function create(req, res) {
  if (!req.session.userId) return res.status(401).json({ error: 'sign in first' });
  try {
    const order = await service.createOrder(req.body, req.session);
    res.status(201).json(order);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
}

async function cancel(req, res) {
  try {
    res.json(await service.cancelOrder(Number(req.params.id), req.session));
  } catch (err) {
    res.status(err.message === 'not found' ? 404 : 409).json({ error: err.message });
  }
}

async function show(req, res) {
  const order = await repo.findOrder(Number(req.params.id));
  if (!order) return res.status(404).json({ error: 'not found' });
  if (req.session.role !== 'admin' && order.customer_id !== req.session.userId) return res.status(403).json({ error: 'not yours' });
  res.json(order);
}

module.exports = { create, cancel, show };
