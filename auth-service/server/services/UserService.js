const UserModel = require('../models/UserModel');

/**
 * Provides methods to fetch and manipulate users and password tokens
 */
class UserService {
  /**
   * Finds and returns a user by email address
   *
   * @param {*} email
   * @returns database result
   */
  static async findByEmail(email) {
    // throw new Error('Not implemented');
    return UserModel.findOne({ email }).exec();
  }

  /**
   * Creates a new user
   *
   * @param {*} username
   * @param {*} email
   * @param {*} password
   * @returns save result
   */
  static async createUser(
    email,
    password,
    fname,
    lname,
    baddress,
    useownwallet
  ) {
    // throw new Error('Not implemented');

    const user = new UserModel();
    user.email = email;
    user.password = password;
    user.fname = fname;
    user.lname = lname;
    user.baddress = baddress;
    user.useownwallet = useownwallet;
    const savedUser = await user.save();
    return savedUser;
  }

  /**
   * Changes a user's password
   * @param {*} userId
   * @param {*} password
   */
  static async changePassword(email, password) {
    // throw new Error('Not implemented');
    const user = await this.findByEmail(email);
    if (!user) {
      throw new Error('User not found');
    }
    user.password = password;
    return user.save();
  }

  // Helpers

  /**
   * Finds a user by id
   * @param {*} id
   * @returns a user
   */
  static async findById(id) {
    return UserModel.findById(id);
  }

  /**
   * Get all users
   *
   * @returns a list of users
   */
  static async getList() {
    return UserModel.find().sort({ createdAt: -1 }).exec();
  }

  /**
   * Deletes a user
   *
   * @returns result
   */
  static async deleteUser(id) {
    return UserModel.findByIdAndDelete(id);
  }

  /**
   * Adds org to user
   *
   * @returns result
   */
  static async linkOrg(org, uid) {
    // update in database
    const user = await this.findById(uid);
    user.org = org;

    return user.save();
  }

  /**
   * Adds verification to user
   *
   * @returns result
   */
  static async linkVerification(verification, uid) {
    // update in database
    const user = await this.findById(uid);
    user.verifications.push(verification);

    return user.save();
  }
}

module.exports = UserService;
