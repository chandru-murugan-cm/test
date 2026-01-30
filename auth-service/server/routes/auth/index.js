const { Router } = require('express');

const registrationRouter = require('./registration');
const loginRouter = require('./login');
const password = require('./password');
const router = Router();
const githubAccess = require('./githubAccess');
const gitlabAccess = require('./gitlabAccess');

const cors = require('cors');

module.exports = (params) => {
  router.use(cors(), registrationRouter(params));
  router.use(cors(), loginRouter(params));
  router.use(cors(), password(params));
  router.use(cors(), githubAccess(params));
  router.use(cors(), gitlabAccess(params));
  return router;
};
