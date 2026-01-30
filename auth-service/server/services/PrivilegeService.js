const PrivilegeModel = require('../models/PrivilegeModel');

class PrivilegeService {
  static async createPrivilege(name) {
    const Privilege = new PrivilegeModel();
    Privilege.name = name;
    const savedPrivilege = await Privilege.save();
    return savedPrivilege;
  }

  static async findById(id) {
    return PrivilegeModel.findById(id).exec();
  }

  static async getList() {
    return PrivilegeModel.find().sort({ createdAt: -1 }).exec();
  }

  static async updateGroup(id, name) {
    const updatedGroup = await PrivilegeModel.findByIdAndUpdate(
      id,
      { name },
      { new: true } // return the updated document
    ).exec();
    return updatedGroup;
  }

  static async deletePrivilege(id) {
    return PrivilegeModel.findByIdAndDelete(id);
  }
}
module.exports = PrivilegeService;
