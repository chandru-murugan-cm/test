const { Router } = require('express');
const passport = require('passport');

const router = Router();

const cors = require('cors');

const config = require('../../config');
const UserModel = require('../../models/UserModel');
const UserService = require('../../services/UserService');

const { logger } = config;

// This module returns a function and this allows you to pass parameters down the routing chain

// eslint-disable-next-line no-unused-vars
module.exports = (params) => {
  router.get(
    '/',
    passport.authenticate('jwt', { session: false }),
    async (req, res, next) => {
      try {
        logger.info('in get user');
        const orgId = req.query.orgId;
        const query = UserModel.find();
        if (req.query.query) {
          query.or([
            { fname: { $regex: req.query.query, $options: 'i' } },
            { lname: { $regex: req.query.query, $options: 'i' } },
            { email: { $regex: req.query.query, $options: 'i' } },
          ]);
        }
        if (orgId) {
          query.and([{ org: orgId }]);
        }
        query.sort({ createdAt: -1 });
        const users = await query.exec();
        const userList = await Promise.all(
          users.map(async (user) => {
            const userJson = user.toJSON();
            return userJson;
          })
        );
        return res.json({ userList });
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
        const user = await UserService.findById(req.params.id);
        return res.json(user);
      } catch (err) {
        return next(err);
      }
    }
  );

  router.put(
    '/',
    passport.authenticate('jwt', { session: false }),
    async (req, res, next) => {
      try {
        const existingUser = await UserService.findById(req.body._id);

        if (!existingUser) {
          const errMsg = {
            text: 'The given User does not exist!',
          };
          return res.status(400).json({ response: errMsg });
        }
        existingUser.org = req.body.org;
        existingUser.group = req.body.group;
        existingUser.save();

        return res.status(200).json({ response: 'updated' });
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
        const result = await UserService.deleteUser(req.params.id);
        return res.json({ result });
      } catch (err) {
        return next(err);
      }
    }
  );

  router.get(
    '/group/users',
    passport.authenticate('jwt', { session: false }),
    async (req, res, next) => {
      try {
        const ids = req.query.ids.split(',');
        const users = await UserModel.find({
          group: { $in: ids },
        });
        const userList = await Promise.all(
          users.map(async (user) => {
            const userJson = user.toJSON();
            return userJson;
          })
        );
        return res.json({ userList });
      } catch (err) {
        return next(err);
      }
    }
  );

  router.get(
    '/group/:groupId',
    passport.authenticate('jwt', { session: false }),
    async (req, res, next) => {
      try {
        const users = await UserModel.find({ group: req.params.groupId });
        const userList = await Promise.all(
          users.map(async (user) => {
            const userJson = user.toJSON();
            return userJson;
          })
        );
        return res.json({ userList });
      } catch (err) {
        return next(err);
      }
    }
  );

  // Always return the router from such a module.
  return router;
};
