const nodemailer = require('nodemailer');

const transport = nodemailer.createTransport({ host: process.env.SMTP_HOST, port: 587 });

async function sendOrderConfirmation(to, orderId, total) {
  await transport.sendMail({ to, subject: 'Order ' + orderId + ' confirmed', text: 'Your total is $' + total });
}

module.exports = { sendOrderConfirmation };
