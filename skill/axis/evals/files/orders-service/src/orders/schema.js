const { z } = require('zod');

const LineItem = z.object({ sku: z.string(), qty: z.number().int().positive(), unitPrice: z.number().nonnegative() });

const NewOrder = z.object({
  customerId: z.string(),
  items: z.array(LineItem).min(1),
  coupon: z.string().optional()
});

const STATUSES = ['placed', 'shipped', 'cancelled'];

module.exports = { LineItem, NewOrder, STATUSES };
