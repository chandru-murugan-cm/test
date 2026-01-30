const passport = require('passport');
const passportJWT = require('passport-jwt');
const LocalStrategy = require('passport-local').Strategy;

/* eslint-disable no-unused-vars */
const UserService = require('../../services/UserService');

const JWTStrategy = passportJWT.Strategy;
const ExtractJWT = passportJWT.ExtractJwt;

/**
 * This module sets up and configures passport
 * @param {*} config
 */
module.exports = (config) => {
  passport.use(
    new LocalStrategy(
      {
        passReqToCallback: true,
        usernameField: 'email'
      },
      async (req, username, password, done) => {
        try {
          const user = await UserService.findByEmail(req.body.email);
          if (!user) {
            return done(null, false);
          }
          if (!user?.isactive){
            return done(null, user);
          }
          const isValid = await user.comparePassword(req.body.password);
          if (!isValid) {
            return done(null, false);
          }
          return done(null, user);
        } catch (err) {
          return done(err);
        }
      }
    )
  );

  passport.use(
    new JWTStrategy(
      {
        jwtFromRequest: ExtractJWT.fromAuthHeaderAsBearerToken(),
        secretOrKey: config.JWTSECRET,
      },
      async (jwtPayload, done) => {
        try {
          const user = await UserService.findById(jwtPayload.userId);

          if (!user?.isactive){
            return done(null, false);
          }
          
          return done(null, user);
        } catch (err) {
          return done(err);
        }
      }
    )
  );

  passport.serializeUser((user, done) => {
    done(null, user.id);
  });

  passport.deserializeUser(async (id, done) => {
    try {
      const user = await UserService.findById(id);
      return done(null, user);
    } catch (err) {
      return done(err);
    }
  });
  return passport;
};
