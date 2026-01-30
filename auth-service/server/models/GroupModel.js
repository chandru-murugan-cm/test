const mongoose = require('mongoose');

const groupSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
      trim: true,
      index: { unique: true },
    },
    privileges: [
      {
        type: mongoose.Schema.Types.ObjectId,
        trim: true,
        ref: 'Privilege',
      },
    ],
  },
  {
    timestamps: true,
  }
);

module.exports = mongoose.model('Group', groupSchema);
