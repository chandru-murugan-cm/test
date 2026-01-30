/* eslint-disable no-underscore-dangle */
const { Router } = require('express');
const passport = require('passport');

const config = require('../../config');
const OrgModel = require('../../models/OrgModel');
const OrgService = require('../../services/OrgService');

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
        const isOrgExistsWithSameName = await OrgService.findByName(
          req.body.name
        );
        if (isOrgExistsWithSameName) {
          return res
            .status(400)
            .json({ error: 'Organization with the same name already exists.' });
        }
        const createdOrg = await OrgService.createOrg(
          req.body.name,
          req.body.type,
          req.body.address
        );
        return res.status(201).json(createdOrg);
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
        const query = OrgModel.find();
        query.populate({ path: 'type' });
        query.sort({ createdAt: -1 });
        const org = await query.exec();
        const orgList = await Promise.all(
          org.map(async (obj) => {
            const orgJson = obj.toJSON();
            return orgJson;
          })
        );
        return res.json({ orgList });
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
        const org = await OrgService.findById(req.params.id);
        return res.json(org);
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
        const existingOrg = await OrgService.findById(req.body._id);

        if (!existingOrg) {
          const errMsg = {
            text: 'The given Organization does not exist!',
          };
          return res.status(400).json({ response: errMsg });
        }

        existingOrg.name = req.body.name;
        existingOrg.type = req.body.type;
        existingOrg.address = req.body.address;
        existingOrg.save();

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
        const result = await OrgService.deleteOrg(req.params.id);
        return res.json({ result });
      } catch (err) {
        return next(err);
      }
    }
  );

  // Always return the router from such a module.
  return router;
};
