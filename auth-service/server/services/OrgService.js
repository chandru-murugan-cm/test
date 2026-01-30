const OrgModel = require('../models/OrgModel');

/**
 * Provides methods to fetch and manipulate organizations
 */
class OrgService {
  /**
   * Creates a new organization
   *
   * @param {*} username
   * @param {*} type
   * @param {*} address
   * @returns save result
   */
  static async createOrg(name, type, address) {
    // throw new Error('Not implemented');
    const org = new OrgModel();
    org.name = name;
    org.type = type;
    org.address = address;
    const savedOrganization = await org.save();
    return savedOrganization;
  }

  static async findByName(name) {
    return OrgModel.findOne({ name }).exec();
  }
  // Helpers
  /**
   * Finds a user by id
   * @param {*} id
   * @returns a user
   */

  static async findById(id) {
    return OrgModel.findById(id).exec();
  }
  /**
   * Get all organization
   *
   * @returns a list of organizations
   */

  static async getList() {
    return OrgModel.find().sort({ createdAt: -1 }).exec();
  }

  /**
   * Deletes a organization
   *
   * @returns result
   */
  static async deleteOrg(id) {
    return OrgModel.findByIdAndDelete(id);
  }
}

module.exports = OrgService;
