import {
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";

import PurchaseService from "../services/PurchaseService";

const PurchaseContext = createContext();

export const PurchaseProvider = ({ children }) => {

    //----------------------------------------
    // Master Data States
    //----------------------------------------

    const [suppliers, setSuppliers] = useState([]);
    const [products, setProducts] = useState([]);
    const [warehouses, setWarehouses] = useState([]); // Added to support export

    //----------------------------------------
    // New Feature States
    //----------------------------------------

    const [purchaseOrders, setPurchaseOrders] = useState([]);
    const [dashboard, setDashboard] = useState({});
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [drawerMode, setDrawerMode] = useState("create");
    const [selectedPurchase, setSelectedPurchase] = useState(null);

    //----------------------------------------
    // Filters State
    //----------------------------------------
    
    const [search, setSearch] = useState("");
    const [supplier_id, setSupplierId] = useState("");
    const [warehouse_id, setWarehouseId] = useState("");
    const [date_from, setDateFrom] = useState("");
    const [date_to, setDateTo] = useState("");
    const [page, setPage] = useState(1);

    const filters = {
        search,
        supplier_id,
        warehouse_id,
        date_from,
        date_to,
        page,
    };

    const setFilters = (newFilters) => {
        if (newFilters.search !== undefined)
            setSearch(newFilters.search);
    
        if (newFilters.supplier_id !== undefined)
            setSupplierId(newFilters.supplier_id);
    
        if (newFilters.warehouse_id !== undefined)
            setWarehouseId(newFilters.warehouse_id);
    
        if (newFilters.date_from !== undefined)
            setDateFrom(newFilters.date_from);
    
        if (newFilters.date_to !== undefined)
            setDateTo(newFilters.date_to);
    
        if (newFilters.page !== undefined)
            setPage(newFilters.page);
    };

    const updateFilter = (field, value) => {
        switch (field) {
            case "search":
                setSearch(value);
                break;
            case "supplier_id":
                setSupplierId(value);
                break;
            case "warehouse_id":
                setWarehouseId(value);
                break;
            case "date_from":
                setDateFrom(value);
                break;
            case "date_to":
                setDateTo(value);
                break;
            case "page":
                setPage(value);
                break;
            default:
                break;
        }
    
        if (field !== "page") {
            setPage(1);
        }
    };

    // Trigger load when filters change
    useEffect(() => {
        loadPurchaseOrders();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [
        search,
        supplier_id,
        warehouse_id,
        date_from,
        date_to,
        page,
    ]);

    //----------------------------------------
    // Purchase Form State
    //----------------------------------------

    const [purchase, setPurchase] = useState({
        supplier_id: "",
        warehouse_id: "",
        invoice_no: "",
        purchase_date: new Date()
            .toISOString()
            .split("T")[0],
        remarks: "",
        items: [
            {
                product_id: "",
                unit_id: "",
                quantity: 1,
                purchase_price: 0,
                discount_percentage: 0,
                gst_percentage: 18,
                remarks: "",
                total: 0,
                current_stock: 0,
            },
        ],
    });

    //----------------------------------------
    // Reset Purchase Form
    //----------------------------------------

    const resetPurchase = () => {
        setPurchase({
            supplier_id: "",
            warehouse_id: "",
            invoice_no: "",
            purchase_date: new Date()
                .toISOString()
                .split("T")[0],
            remarks: "",
            items: [
                {
                    product_id: "",
                    unit_id: "",
                    quantity: 1,
                    purchase_price: 0,
                    discount_percentage: 0,
                    gst_percentage: 18,
                    remarks: "",
                    total: 0,
                    current_stock: 0,
                },
            ],
        });
    };

    //----------------------------------------
    // Drawer Functions
    //----------------------------------------

    const openCreateDrawer = () => {
        resetPurchase();
        setDrawerMode("create");
        setSelectedPurchase(null);
        setDrawerOpen(true);
    };

    const openEditDrawer = (purchaseData) => {
        setDrawerMode("edit");
        setSelectedPurchase(purchaseData);
        setPurchase({
            supplier_id: purchaseData.supplier_id,
            warehouse_id: purchaseData.warehouse_id,
            invoice_no: purchaseData.reference_number,
            purchase_date: purchaseData.po_date,
            remarks: purchaseData.remarks,
            items: purchaseData.items
        });
        setDrawerOpen(true);
    };

    const openViewDrawer = (purchaseData) => {
        setDrawerMode("view");
        setSelectedPurchase(purchaseData);
        setPurchase({
            supplier_id: purchaseData.supplier_id,
            warehouse_id: purchaseData.warehouse_id,
            invoice_no: purchaseData.reference_number,
            purchase_date: purchaseData.po_date,
            remarks: purchaseData.remarks,
            items: purchaseData.items
        });
        setDrawerOpen(true);
    };

    const closeDrawer = () => {
        setDrawerOpen(false);
    };

    //----------------------------------------
    // Data Loaders
    //----------------------------------------

    const loadSuppliers = async () => {
        try {
            const data = await PurchaseService.getSuppliers();
            setSuppliers(data.suppliers || []);
        } catch (error) {
            console.error(error);
        }
    };

    const loadProducts = async () => {
        try {
            const data = await PurchaseService.getProducts();
            setProducts(data.items || []);
        } catch (error) {
            console.error(error);
        }
    };

    const loadWarehouses = async () => {
        try {
            const warehouses = await PurchaseService.getWarehouses();
            
            console.log("Warehouse API:", warehouses);
            
            setWarehouses(Array.isArray(warehouses) ? warehouses : []);
        } catch (error) {
            console.error(error);
            setWarehouses([]);
        }
    };

    const loadPurchaseOrders = async () => {
        try {
            const params = {
                page,
                page_size: 10,
            };
            
            if (search) {
                params.search = search;
            }
            if (supplier_id) {
                params.supplier_id = supplier_id;
            }
            if (warehouse_id) {
                params.warehouse_id = warehouse_id;
            }
            if (date_from) {
                params.date_from = date_from;
            }
            if (date_to) {
                params.date_to = date_to;
            }
    
            const data = await PurchaseService.getPurchaseOrders(params);
    
            console.log(data);
    
            if (Array.isArray(data.purchase_orders)) {
                setPurchaseOrders(data.purchase_orders);
            } else {
                setPurchaseOrders([]);
            }
    
        } catch (error) {
            console.error(error);
        }
    };

    const loadDashboard = async () => {
        try {
            const data = await PurchaseService.getDashboard();
            setDashboard(data);
        } catch (error) {
            console.error(error);
        }
    };

    //----------------------------------------
    // Export Purchases
    //----------------------------------------

    console.log(PurchaseService);
    console.log(PurchaseService.exportPurchaseOrders);

    const exportPurchases = async () => {
        try {
            const blob = await PurchaseService.exportPurchaseOrders(filters);
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "purchase_orders.xlsx";
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error(error);
            alert("Failed to export purchase orders.");
        }
    };

    //----------------------------------------
    // Initial Load
    //----------------------------------------

    useEffect(() => {
        loadSuppliers();
        loadProducts();
        loadWarehouses();
        // Removed loadPurchaseOrders() from here as it's now handled by the [search, supplier_id, warehouse_id, date_from, date_to, page] useEffect
        loadDashboard();
    }, []);

    //----------------------------------------
    // Update Purchase Field
    //----------------------------------------

    const updateField = async (field, value) => {
        setPurchase((prev) => ({
            ...prev,
            [field]: value,
        }));

        // Fetch stock for all existing product items if warehouse changes
        if (field === "warehouse_id" && value) {
            purchase.items.forEach(async (item, index) => {
                if (item.product_id) {
                    try {
                        const stock = await PurchaseService.getCurrentStock(
                            item.product_id,
                            value
                        );
                        
                        setPurchase((prev) => {
                            const newItems = [...prev.items];
                            if (newItems[index]) {
                                newItems[index] = {
                                    ...newItems[index],
                                    current_stock: stock,
                                };
                            }
                            return { ...prev, items: newItems };
                        });
                    } catch (error) {
                        console.error("Failed to fetch stock:", error);
                    }
                }
            });
        }
    };

    //----------------------------------------
    // Add Item
    //----------------------------------------

    const addItem = () => {
        setPurchase((prev) => ({
            ...prev,
            items: [
                ...prev.items,
                {
                    product_id: "",
                    unit_id: "",
                    quantity: 1,
                    purchase_price: 0,
                    discount_percentage: 0,
                    gst_percentage: 18,
                    remarks: "",
                    total: 0,
                    current_stock: 0,
                },
            ],
        }));
    };

    //----------------------------------------
    // Remove Item
    //----------------------------------------

    const removeItem = (index) => {
        const items = [...purchase.items];
        items.splice(index, 1);
        setPurchase({
            ...purchase,
            items,
        });
    };

    //----------------------------------------
    // Update Item
    //----------------------------------------

    const updateItem = async (index, field, value) => {
        const items = [...purchase.items];
        items[index][field] = value;
        
        const quantity = Number(items[index].quantity) || 0;
        const purchase_price = Number(items[index].purchase_price) || 0;
        const discount_percentage = Number(items[index].discount_percentage) || 0;
        const gst_percentage = Number(items[index].gst_percentage) || 0;

        const amount = quantity * purchase_price;
        const discount = amount * (discount_percentage / 100);
        const taxable = amount - discount;
        const gst = taxable * (gst_percentage / 100);
        
        items[index].total = taxable + gst;

        setPurchase({
            ...purchase,
            items,
        });

        // Fetch stock if product changes and warehouse is selected
        if (field === "product_id" && value && purchase.warehouse_id) {
            try {
                const stock = await PurchaseService.getCurrentStock(
                    value,
                    purchase.warehouse_id
                );
                
                setPurchase((prev) => {
                    const newItems = [...prev.items];
                    if (newItems[index]) {
                        newItems[index] = {
                            ...newItems[index],
                            current_stock: stock,
                        };
                    }
                    return { ...prev, items: newItems };
                });
            } catch (error) {
                console.error("Failed to fetch stock:", error);
            }
        }
    };

    //----------------------------------------
    // Calculate Grand Total
    //----------------------------------------

    const grandTotal = purchase.items.reduce(
        (sum, item) => sum + Number(item.total),
        0
    );

    //----------------------------------------
    // Save Purchase
    //----------------------------------------

    const savePurchase = async () => {
        try {
            if (drawerMode === "edit") {
                await updatePurchase();
                return;
            }

            const payload = {
                supplier_id: Number(purchase.supplier_id),
                warehouse_id: Number(purchase.warehouse_id),
                po_date: purchase.purchase_date,
                reference_number: purchase.invoice_no,
                remarks: purchase.remarks,
                items: purchase.items.map(item => ({
                    product_id: Number(item.product_id),
                    warehouse_id: Number(purchase.warehouse_id),
                    unit_id: Number(item.unit_id),
                    quantity: Number(item.quantity),
                    purchase_price: Number(item.purchase_price),
                    discount_percentage: Number(
                        item.discount_percentage || 0
                    ),
                    gst_percentage: Number(
                        item.gst_percentage || 18
                    ),
                    remarks: item.remarks || ""
                }))
            };

            await PurchaseService.createPurchase(payload);
            
            await loadPurchaseOrders();
            await loadDashboard();
            closeDrawer();
            resetPurchase();

            alert("Purchase Saved Successfully");

        } catch (error) {
            console.error(error);
            alert(error.response?.data?.detail || "Failed to Save Purchase");
        }
    };

    //----------------------------------------
    // Update Purchase
    //----------------------------------------

    const updatePurchase = async () => {
        try {
            const payload = {
                supplier_id: Number(
                    purchase.supplier_id
                ),
                warehouse_id: Number(
                    purchase.warehouse_id
                ),
                po_date: purchase.purchase_date,
                reference_number: purchase.invoice_no,
                remarks: purchase.remarks,
            };

            await PurchaseService.updatePurchase(
                selectedPurchase.id,
                payload
            );

            await loadPurchaseOrders();
            await loadDashboard();
            closeDrawer();
            resetPurchase();
            
            alert("Purchase Updated Successfully");
            
        } catch (error) {
            console.error(error);
            alert(error.response?.data?.detail || "Failed to Update Purchase");
        }
    };

    //----------------------------------------
    // Delete Purchase
    //----------------------------------------

    const deletePurchase = async (purchaseId) => {
        const confirmDelete = window.confirm(
            "Are you sure you want to cancel this purchase order?"
        );

        if (!confirmDelete) return;

        try {
            await PurchaseService.deletePurchase(purchaseId);
            await loadPurchaseOrders();
            await loadDashboard();
            
            alert("Purchase Deleted Successfully");
        } catch (error) {
            console.error(error);
            alert(error.response?.data?.detail || "Failed to Cancel Purchase Order");
        }
    };

    return (
        <PurchaseContext.Provider
            value={{
                dashboard,
                purchaseOrders,
                
                filters,
                setFilters,
                updateFilter,
                
                loadPurchaseOrders,
                drawerOpen,
                drawerMode,
                selectedPurchase,
                openCreateDrawer,
                openEditDrawer,
                openViewDrawer,
                closeDrawer,
                purchase,
                savePurchase,
                updatePurchase,
                deletePurchase,
                updateField,
                addItem,
                removeItem,
                updateItem,
                suppliers,
                warehouses,
                products,
                grandTotal,
                exportPurchases,
                
                setSearch,
                setSupplierId,
                setWarehouseId,
                setDateFrom,
                setDateTo,
            }}
        >
            {children}
        </PurchaseContext.Provider>
    );
};

export const usePurchase = () => useContext(PurchaseContext); 