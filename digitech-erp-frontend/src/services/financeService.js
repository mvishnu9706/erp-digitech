export const financeService = {
  list: async () => ({ data: [] }),
  create: async (payload) => ({ data: payload }),
  update: async (id, payload) => ({ data: { id, ...payload } }),
  remove: async (id) => ({ data: { id } }),
};
