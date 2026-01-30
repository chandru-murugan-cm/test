const logger = require('pino')({ prettyPrint: true });
require('dotenv').config();

module.exports = {
  database: {
    dsn: process.env.MONGODBDSN,
    status: {
      connected: false,
      error: false,
    },
  },
  JWTSECRET: process.env.JWTSECRET,
  logger,
};
