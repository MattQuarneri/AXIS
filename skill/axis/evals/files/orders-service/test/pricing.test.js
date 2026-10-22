const { priceOrder } = require('../src/orders/pricing');

test('applies a coupon', () => {
  expect(priceOrder([{ qty: 2, unitPrice: 50 }], 'WELCOME10')).toEqual({ subtotal: 100, discount: 10, total: 90 });
});
