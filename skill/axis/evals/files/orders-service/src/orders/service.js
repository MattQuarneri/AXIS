const repo = require('./repo');
const { priceOrder } = require('./pricing');
const { NewOrder } = require('./schema');
const { sendOrderConfirmation } = require('../mail/mailer');

// Creates an order: validates, prices, stores, emails.
async function createOrder(input, session) {
  const parsed = NewOrder.parse(input);
  if (session.role !== 'admin' && parsed.customerId !== session.userId) {
    throw new Error('cannot order for another customer');
  }
  const price = priceOrder(parsed.items, parsed.coupon);
  if (price.total > 10000 && session.role !== 'admin') {
    throw new Error('order too large; needs approval');
  }
  const order = { ...parsed, status: 'placed', total: price.total, placedAt: Date.now() };
  const id = await repo.insertOrder(order);
  await sendOrderConfirmation(session.email, id, price.total);
  return { id, ...order };
}

async function cancelOrder(id, session) {
  const order = await repo.findOrder(id);
  if (!order) throw new Error('not found');
  if (order.status === 'shipped') throw new Error('already shipped');
  if (session.role !== 'admin' && order.customer_id !== session.userId) throw new Error('not yours');
  await repo.setStatus(id, 'cancelled');
  return { ...order, status: 'cancelled' };
}

module.exports = { createOrder, cancelOrder };
