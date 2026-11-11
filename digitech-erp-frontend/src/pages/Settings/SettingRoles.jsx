import React from "react";

import DashboardLayout from "../../layouts/DashboardLayout";
import RoleCards from "../../components/settings/RoleCards/RoleCards";

import "./SettingRoles.css";


const SettingRoles = () => {

    const handleAddUser = (role) => {

        console.log(
            "Add user with role:",
            role
        );

    };


    return (

        <DashboardLayout>

            {/* =================================================
                ROLE MANAGEMENT
            ================================================= */}

            <RoleCards
                onAddUser={handleAddUser}
            />

        </DashboardLayout>

    );

};


export default SettingRoles;