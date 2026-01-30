const cookieParser = require('cookie-parser');
const express = require('express');
const session = require('express-session'); // Import express-session
const configg = require('./config');

const { logger } = configg;

// This is the root file of the routing structure
const indexRouter = require('./routes/index');
const setupPassport = require('./lib/passport');

module.exports = (config) => {
  const app = express();
  const passport = setupPassport(config);

  // Just in case we need to log something later
  // const { logger } = config;

  // This is used to show the database connection status on the website
  app.locals.databaseStatus = config.database.status;

  // See express body parsers for more information
  app.use(express.json());
  app.use(express.urlencoded({ extended: false }));
  app.use(cookieParser());

  // Set up express-session middleware
  app.use(
    session({
      secret: 'myownsecret', // Replace secret
      resave: false,
      saveUninitialized: false,
      cookie: { secure: false }, // Set to true if using HTTPS
    })
  );

  app.use(passport.initialize());
  app.use(passport.session());

  // Note that we are calling the index router as a function
  app.use('/', indexRouter({ config }));

  // Error handler
  app.use((err, req, res, next) => {
    logger.info(err);
    // Set locals, only providing error in development
    res.locals.message = err.message;
    res.locals.error = req.app.get('env') === 'development' ? err : {};

    // Render the error page
    res.status(err.status || 500).json({ error: res.locals.message });
    // res.render('error');
  });

  return app;
};
