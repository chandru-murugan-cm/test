/* eslint-disable no-param-reassign */
const GroupModel = require('../models/GroupModel');

class GroupService {
  static async createGroup(name, privileges) {
    const Group = new GroupModel();
    Group.name = name;
    Group.privileges = privileges;
    const savedGroup = await Group.save();
    return savedGroup;
  }

  static async findById(id) {
    return GroupModel.findById(id).exec();
  }

  static async getList(names = '') {
    names = names.split(',');
    const query = GroupModel.find();
    if (names && Array.isArray(names) && names.length > 0) {
      query.where({
        name: { $in: names.map((name) => new RegExp(name, 'i')) },
      });
    }
    query.sort({ createdAt: -1 });
    return query.exec();
  }

  static async updateGroup(id, name, privileges) {
    const updatedGroup = await GroupModel.findByIdAndUpdate(
      id,
      { name, privileges },
      { new: true } // return the updated document
    ).exec();
    return updatedGroup;
  }

  static async deleteGroup(id) {
    return GroupModel.findByIdAndDelete(id);
  }
}
module.exports = GroupService;
