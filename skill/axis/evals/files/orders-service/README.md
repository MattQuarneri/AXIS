# orders-service

A small order API. Express, SQLite, nodemailer. `npm start` runs `src/server.js`.

- `POST /orders` creates an order for the signed-in customer and emails a confirmation.
- `POST /orders/:id/cancel` cancels an order that has not shipped.
- `GET /orders/:id` returns one order with its line items.
