const sqlite3 = require('sqlite3');

const db = new sqlite3.Database(process.env.DB_FILE || 'orders.db');

function run(sql, params) {
  return new Promise((resolve, reject) => db.run(sql, params, function (err) { err ? reject(err) : resolve(this); }));
}
function all(sql, params) {
  return new Promise((resolve, reject) => db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows))));
}

module.exports = { run, all };
