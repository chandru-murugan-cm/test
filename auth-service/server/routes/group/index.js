const { Router } = require('express');
const passport = require('passport');

const cors = require('cors');

const config = require('../../config');
const GroupModel = require('../../models/GroupModel');
const GroupService = require('../../services/GroupService');

const router = Router();
const { logger } = config;

// This module returns a function and this allows you to pass parameters down the routing chain

// eslint-disable-next-line no-unused-vars
module.exports = (params) => {
  router.post(
    '/',
    passport.authenticate('jwt', { session: false }),
    async (req, res, next) => {
      try {
        const createdGroup = await GroupService.createGroup(
          req.body.name,
          req.body.privileges
        );
        return res.status(201).json(createdGroup);
      } catch (err) {
        return next(err);
      }
    }
  );

  router.get(
    '/',
    passport.authenticate('jwt', { session: false }),
    async (req, res, next) => {
      try {
        if (req.query.name) {
          const group = await GroupService.getList(req.query.name);
          return res.json(group);
        }
        const group = await GroupService.getList();
        return res.json(group);
      } catch (err) {
        logger.info('in error');
        logger.info(err);
        return next(err);
      }
    }
  );

  router.get(
    '/:id',
    passport.authenticate('jwt', { session: false }),
    async (req, res, next) => {
      try {
        const group = await GroupService.findById(req.params.id);
        return res.json(group);
      } catch (err) {
        return next(err);
      }
    }
  );

  router.put(
    '/:id',
    passport.authenticate('jwt', { session: false }),
    async (req, res, next) => {
      try {
        const { id } = req.body;
        const { name } = req.body;
        const { privileges } = req.body;

        const existingGroup = await GroupService.updateGroup(
          id,
          name,
          privileges
        );

        if (!existingGroup) {
          const errMsg = {
            text: 'The given Group does not exist!',
          };
          return res.status(400).json({ response: errMsg });
        }

        return res
          .status(200)
          .json({ response: 'updated', data: existingGroup });
      } catch (err) {
        return next(err);
      }
    }
  );

  router.delete(
    '/:id',
    passport.authenticate('jwt', { session: false }),
    async (req, res, next) => {
      try {
        const result = await GroupService.deleteGroup(req.params.id);
        return res.json({ result });
      } catch (err) {
        return next(err);
      }
    }
  );

  // Always return the router from such a module.
  return router;
};
