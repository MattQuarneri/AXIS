const express = require('express');
const orders = require('./orders/controller');
const { attachSession } = require('./auth/session');

const app = express();
app.use(express.json());
app.use(attachSession);

app.post('/orders', orders.create);
app.post('/orders/:id/cancel', orders.cancel);
app.get('/orders/:id', orders.show);

app.listen(process.env.PORT || 3000, () => console.log('orders-service listening'));
