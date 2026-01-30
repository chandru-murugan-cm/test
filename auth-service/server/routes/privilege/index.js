const { Router } = require('express');
const passport = require('passport');

const cors = require('cors');

const config = require('../../config');
const PrivilegeModel = require('../../models/PrivilegeModel');
const PrivilegeService = require('../../services/PrivilegeService');

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
        const createdPrivilege = await PrivilegeService.createPrivilege(
          req.body.name,
          req.body.privileges
        );
        return res.status(201).json(createdPrivilege);
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
        const query = PrivilegeModel.find();
        query.populate({ path: 'name' });
        query.sort({ createdAt: -1 });
        const privilege = await query.exec();
        const privilegeList = await Promise.all(
          privilege.map(async (privilege) => {
            const privilegeJson = privilege.toJSON();
            return privilegeJson;
          })
        );
        return res.json({ privilegeList });
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
        const privilege = await PrivilegeService.findById(req.params.id);
        return res.json(privilege);
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
        const existingPrivilege = await PrivilegeService.updateprivilege(
          id,
          name
        );

        if (!existingPrivilege) {
          const errMsg = {
            text: 'The given Privilege does not exist!',
          };
          return res.status(400).json({ response: errMsg });
        }

        return res
          .status(200)
          .json({ response: 'updated', data: existingPrivilege });
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
        const result = await PrivilegeService.deletePrivilege(req.params.id);
        return res.json({ result });
      } catch (err) {
        return next(err);
      }
    }
  );

  // Always return the router from such a module.
  return router;
};
