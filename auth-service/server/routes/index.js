const { Router } = require('express');

const cors = require('cors');
const authRouter = require('./auth');
const userRouter = require('./user');
const orgRouter = require('./org');
const orgtypeRouter = require('./orgtype');
const groupRouter = require('./group');
const privilegeRouter = require('./privilege');

const router = Router();

// This module returns a function and this allows you to pass parameters down the routing chain
module.exports = (params) => {
  /* GET index page. */
  router.get('/', (req, res) => {
    res.render('index', { page: 'index' });
  });

  // This delegates everything under /auth to the respective routing module.
  // We also pass down the params.
  router.use('/auth', cors(), authRouter(params));
  router.use('/auth/user', cors(), userRouter(params));
  router.use('/auth/org', cors(), orgRouter(params));
  router.use('/auth/orgtype', cors(), orgtypeRouter(params));
  router.use('/auth/group', cors(), groupRouter(params));
  router.use('/auth/privilege', cors(), privilegeRouter(params));

  // Always return the router from such a module.
  return router;
};
