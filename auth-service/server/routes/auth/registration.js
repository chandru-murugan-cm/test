const { Router } = require('express');
const CryptoJS = require('crypto-js');

// eslint-disable-next-line no-unused-vars
const UserService = require('../../services/UserService');

const validation = require('../../middlewares/validation');

const router = Router();

module.exports = () => {
  /**
   * POST route to process the registration form or display
   * it again along with an error message in case validation fails
   */
  router.post(
    '/register',
    // Here we call middlewares to validate the user inputs
    validation.validateEmail,
    validation.validatePassword,
    validation.validatePasswordMatch,
    async (req, res, next) => {
      try {
        // This block deals with processing the validation input
        const validationErrors = validation.validationResult(req);

        if (!validationErrors.isEmpty()) {
          validationErrors.errors.forEach((error) => {
            return res.status(400).json({ response: validationErrors });
          });
        } else {
          const existingEmail = await UserService.findByEmail(req.body.email);

          if (existingEmail) {
            const errMsg = {
              text: 'The given email address exist already!',
            };
            console.log('Email already exists');
            return res.status(400).json({ response: errMsg });
          }
        }

        const secretKey = process.env.CRYPTO_SECRET_KEY;
        const password = CryptoJS.AES.decrypt(
          req.body.password,
          secretKey
        ).toString(CryptoJS.enc.Utf8);

        /**
         * @todo: Provide a method in UserService that will create a new user
         */
        createdUser = await UserService.createUser(
          req.body.email,
          password,
          req.body.fname,
          req.body.lname
        );
        return res
          .status(201)
          .json({ response: { id: createdUser._id, text: 'created' } });
      } catch (err) {
        return next(err);
      }
    }
  );
  return router;
};
