// TODO: Overlapping schedulers. Will clean up
export const schedulers = {
  cars: {
    schedule: "*/60 0-10 * * 1-5",
  },
  coe: {
    schedule: "*/60 0-10 * * 1-5",
  },
  "coe-1st-bidding": {
    schedule: "*/60 0-10 * * 4,5",
  },
  "coe-2nd-bidding": {
    schedule: "*/60 0-10 * * 4,5",
  },
};
