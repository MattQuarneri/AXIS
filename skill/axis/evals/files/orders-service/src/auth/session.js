const jwt = require('jsonwebtoken');

// Reads the bearer token and puts { userId, role } on the request.
function attachSession(req, res, next) {
  const header = req.headers.authorization || '';
  try {
    const claims = jwt.verify(header.replace('Bearer ', ''), process.env.JWT_SECRET);
    req.session = { userId: claims.sub, role: claims.role, expires: claims.exp };
  } catch (err) {
    req.session = { userId: null, role: 'guest' };
  }
  next();
}

module.exports = { attachSession };
