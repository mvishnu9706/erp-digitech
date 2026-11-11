export const isRequired = (value) => Boolean(value && String(value).trim());
export const isEmail = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value || '');
