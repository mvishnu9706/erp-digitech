export const TOKEN_KEY = "erp_access_token";

export const USER_KEY = "erp_user";

export const saveToken = (token) => {

    localStorage.setItem(TOKEN_KEY, token);

};

export const getToken = () => {

    return localStorage.getItem(TOKEN_KEY);

};

export const removeToken = () => {

    localStorage.removeItem(TOKEN_KEY);

};

export const saveUser = (user) => {

    localStorage.setItem(USER_KEY, JSON.stringify(user));

};

export const getUser = () => {

    return JSON.parse(localStorage.getItem(USER_KEY));

};

export const removeUser = () => {

    localStorage.removeItem(USER_KEY);

};

export const logoutStorage = () => {

    removeToken();

    removeUser();

};