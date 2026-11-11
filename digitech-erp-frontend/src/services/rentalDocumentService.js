import api from "../api/axios";

class RentalDocumentService {

    // =========================================================
    // UPLOAD MACHINE DOCUMENTS
    // =========================================================

    async uploadMachineDocuments(
        machineId,
        rentalAgreementFile = null,
        installationReportFile = null
    ) {

        if (!machineId) {
            throw new Error(
                "Machine ID is required."
            );
        }

        if (
            !rentalAgreementFile &&
            !installationReportFile
        ) {
            return null;
        }

        const formData = new FormData();

        // -----------------------------------------------------
        // Rental Agreement
        // -----------------------------------------------------

        if (rentalAgreementFile) {

            formData.append(
                "rental_agreement",
                rentalAgreementFile,
                rentalAgreementFile.name ||
                "rental-agreement.pdf"
            );
        }

        // -----------------------------------------------------
        // Installation Report
        // -----------------------------------------------------

        if (installationReportFile) {

            formData.append(
                "installation_report",
                installationReportFile,
                installationReportFile.name ||
                "installation-report.pdf"
            );
        }

        console.log(
            "======================================"
        );

        console.log(
            "UPLOADING MACHINE DOCUMENTS"
        );

        console.log(
            "Machine ID:",
            machineId
        );

        console.log(
            "Rental Agreement:",
            rentalAgreementFile
                ? {
                    name: rentalAgreementFile.name,
                    type: rentalAgreementFile.type,
                    size: rentalAgreementFile.size,
                }
                : null
        );

        console.log(
            "Installation Report:",
            installationReportFile
                ? {
                    name: installationReportFile.name,
                    type: installationReportFile.type,
                    size: installationReportFile.size,
                }
                : null
        );

        console.log(
            "======================================"
        );


        // IMPORTANT:
        // DO NOT manually set Content-Type.
        //
        // Browser must generate:
        // multipart/form-data; boundary=...
        //
        const response = await api.post(
            `/rental-bills/machines/${machineId}/documents`,
            formData
        );

        return response.data;
    }


    // =========================================================
    // GET DOCUMENT
    // =========================================================

    async getMachineDocument(
        machineId,
        documentType
    ) {

        if (!machineId) {
            throw new Error(
                "Machine ID is required."
            );
        }

        if (
            documentType !==
                "rental_agreement" &&
            documentType !==
                "installation_report"
        ) {

            throw new Error(
                "Invalid document type."
            );
        }

        return api.get(
            `/rental-bills/machines/${machineId}/documents/${documentType}`,
            {
                responseType: "blob",
            }
        );
    }


    // =========================================================
    // GET DOCUMENT STATUS
    // =========================================================

    async getMachineDocumentStatus(
        machineId
    ) {

        if (!machineId) {
            return null;
        }

        const response = await api.get(
            `/rental-bills/machines/${machineId}/documents/status`
        );

        return response.data;
    }

}


// =============================================================
// SINGLETON
// =============================================================

export default new RentalDocumentService();