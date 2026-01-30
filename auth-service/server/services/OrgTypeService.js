const OrgTypeModel = require('../models/OrgTypeModel');

class OrgTypeService {
  static async createOrgType(name, desc) {
    const orgtype = new OrgTypeModel();
    orgtype.name = name;
    orgtype.desc = desc;
    const savedOrgType = await orgtype.save();
    return savedOrgType;
  }

  static async findById(id) {
    return OrgTypeModel.findById(id).exec();
  }

  static async findByName(name) {
    return OrgTypeModel.findOne({ name }).exec();
  }

  static async getList() {
    return OrgTypeModel.find().sort({ createdAt: -1 }).exec();
  }

  static async deleteOrgType(id) {
    return OrgTypeModel.findByIdAndDelete(id);
  }
}
module.exports = OrgTypeService;
