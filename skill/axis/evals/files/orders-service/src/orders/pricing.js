const COUPONS = { WELCOME10: 0.1, VIP20: 0.2 };

function subtotal(items) {
  return items.reduce((sum, item) => sum + item.qty * item.unitPrice, 0);
}

function discountFor(coupon, amount) {
  const rate = COUPONS[coupon] || 0;
  return Math.round(amount * rate * 100) / 100;
}

function priceOrder(items, coupon) {
  const before = subtotal(items);
  const discount = discountFor(coupon, before);
  return { subtotal: before, discount, total: before - discount };
}

module.exports = { subtotal, discountFor, priceOrder };
