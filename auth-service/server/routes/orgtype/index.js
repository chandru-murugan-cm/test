const { Router } = require('express');
const passport = require('passport');

const config = require('../../config');
const OrgTypeModel = require('../../models/OrgTypeModel');
const OrgTypeService = require('../../services/OrgTypeService');

const router = Router();
const { logger } = config;

module.exports = () => {
  router.post(
    '/',
    passport.authenticate('jwt', { session: false }),
    async (req, res, next) => {
      try {
        const isOrgTypeExistsWithSameName = await OrgTypeService.findByName(
          req.body.name
        );
        if (isOrgTypeExistsWithSameName) {
          return res.status(400).json({
            error: 'Organization type with the same name already exists.',
          });
        }
        const createdOrgType = await OrgTypeService.createOrgType(
          req.body.name,
          req.body.desc
        );
        return res.status(201).json(createdOrgType);
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
        const query = OrgTypeModel.find();
        query.sort({ createdAt: -1 });
        const orgtypeList = await query.exec();
        return res.json(orgtypeList);
      } catch (err) {
        logger.info(err);
        return next(err);
      }
    }
  );

  router.put(
    '/',
    passport.authenticate('jwt', { session: false }),
    async (req, res, next) => {
      try {
        // eslint-disable-next-line no-underscore-dangle
        const existingOrgType = await OrgTypeService.findById(req.body._id);

        if (!existingOrgType) {
          const errMsg = {
            text: 'The given Organization Type does not exist!',
          };
          return res.status(400).json({ response: errMsg });
        }

        existingOrgType.name = req.body.name;
        existingOrgType.desc = req.body.desc;
        existingOrgType.save();

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
        const result = await OrgTypeService.deleteOrgType(req.params.id);
        return res.json({ result });
      } catch (err) {
        return next(err);
      }
    }
  );

  return router;
};
