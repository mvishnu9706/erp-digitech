import api from "../api/axios";


// =====================================================
// LOGIN
// =====================================================
//
// The user can login using either:
//
// 1. Email
//    admin@digitech.com
//
// OR
//
// 2. Mobile Number
//    9876500011
//
// The backend receives both as "identifier".
// =====================================================

export const login = async (
    identifier,
    password
) => {

    const response = await api.post(
        "/auth/login",
        {
            identifier: identifier.trim(),
            password,
        }
    );

    return response.data;
};